# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Invenio filesystem logging module."""

from __future__ import absolute_import, print_function

import logging
from functools import partial

import pkg_resources
from celery.signals import after_setup_logger, after_setup_task_logger
from flask_babelex import gettext as _
from raven.contrib.flask import Sentry
from raven.handlers.logging import SentryHandler
from raven.processors import SanitizePasswordsProcessor


class InvenioLoggingSentry(object):
    """Invenio-Logging extension. Sentry handler."""

    def __init__(self, app=None, test_param=None):
        """Extension initialization."""
        self.test_param = test_param

        _('A translation string')
        if app:
            self.init_app(app)

    def sentry_include_paths(self):
        """Detect Invenio dependencies for use with SENTRY_INCLUDE_PATHS."""
        try:
            dist = pkg_resources.get_distribution('invenio')
            return map(lambda req: req.key, dist.requires())
        except pkg_resources.DistributionNotFound:
            pass

    def setup_warnings(self, sentry):
        """Add sentry to warnings logger."""
        warnings = logging.getLogger('py.warnings')
        warnings.addHandler(
            SentryHandler(sentry.client, level=logging.WARNING))

    def add_sentry_id_header(self, sender, response, *args, **kwargs):
        """Fix issue when last_event_id is not defined."""
        if hasattr(self, 'last_event_id'):
            response.headers['X-Sentry-ID'] = self.last_event_id
        return response

    def celery_dsn_fix(self, app):
        """Fix SENTRY_DSN for Celery.

        Celery does not handle threaded transport very well,
        so allow overriding default transport mechanism for Celery.
        """
        if app.config.get('CELERY_CONTEXT', False) and \
                app.config['LOGGING_SENTRY_CELERY'] and \
                app.config['LOGGING_SENTRY_CELERY_TRANSPORT']:
            parts = app.config['SENTRY_DSN'].split('+', 1)
            if parts[0] in ('eventlet', 'gevent', 'requests', 'sync',
                            'threaded', 'twisted', 'tornado'):
                app.config['SENTRY_DSN'] = "%s+%s" % (
                    app.config['LOGGING_SENTRY_CELERY_TRANSPORT'],
                    parts[1],
                )
            else:
                app.config['SENTRY_DSN'] = "%s+%s" % (
                    app.config['LOGGING_SENTRY_CELERY_TRANSPORT'],
                    "+".join(parts),
                )

    def add_handler(self, logger, app):
        """Add handler to logger if not already added."""
        for h in logger.handlers:
            if isinstance(h, SentryHandler):
                return

        logger.addHandler(
            SentryHandler(
                app.extensions['sentry'].client,
                level=app.config['LOGGING_SENTRY_LEVEL']
            )
        )

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['invenio-logging-sentry'] = self

        """Setup Sentry extension."""

        app.config.setdefault('SENTRY_DSN', None)
        # Sanitize data more
        app.config.setdefault('SENTRY_PROCESSORS', (
            'raven.processors.SanitizePasswordsProcessor',
            'invenio_logging.sentry.InvenioSanitizeProcessor',
        ))
        # When a user is logged in, also include the user info in
        # the log message.
        app.config.setdefault('SENTRY_USER_ATTRS', ['info', ])
        # Defaults to only reporting errors and warnings.
        app.config.setdefault('LOGGING_SENTRY_LEVEL', 'WARNING')
        # Send warnings to Sentry?
        app.config.setdefault('LOGGING_SENTRY_INCLUDE_WARNINGS', True)
        # Send Celery log messages to Sentry?
        app.config.setdefault('LOGGING_SENTRY_CELERY', True)
        # Transport mechanism for Celery. Defaults to synchronous transport.
        # See http://raven.readthedocs.org/en/latest/transports/index.html
        app.config.setdefault('LOGGING_SENTRY_CELERY_TRANSPORT', 'sync')

        if app.config['SENTRY_DSN']:
            # Detect Invenio requirements and add to Sentry include paths so
            # version information about them is added to the log message.
            app.config.setdefault('SENTRY_INCLUDE_PATHS',
                                  self.sentry_include_paths())

            # Fix-up known version problems getting version information
            # Patch submitted to raven-python, if accepted the following lines
            # can be removed:
            # https://github.com/getsentry/raven-python/pull/452
            from raven.utils import _VERSION_CACHE
            try:
                pkg_resources.get_distribution('invenio')
                pkg_resources.get_distribution('webassets')
            except pkg_resources.DistributionNotFound:
                HAS_INVENIO = False
            else:
                import invenio
                import webassets
                HAS_INVENIO = True

                _VERSION_CACHE['invenio'] = invenio.__version__
                _VERSION_CACHE['webassets'] = webassets.__version__

            import setuptools
            _VERSION_CACHE['setuptools'] = setuptools.__version__

            # Modify Sentry transport for Celery - must be called
            # prior to client creation.
            self.celery_dsn_fix(app)

            # Installs sentry in app.extensions['sentry']
            s = Sentry(
                app,
                logging=True,
                level=getattr(logging, app.config['LOGGING_SENTRY_LEVEL'])
            )

            # Replace method with more robust version
            s.add_sentry_id_header = self.add_sentry_id_header

            # Add extra tags information to sentry.
            # Invenio may not be present
            if HAS_INVENIO:
                s.client.extra_context({'version': invenio.__version__})

            # Capture warnings from warnings module
            if app.config['LOGGING_SENTRY_INCLUDE_WARNINGS']:
                self.setup_warnings(s)

            # Setup Celery logging to Sentry
            if app.config['LOGGING_SENTRY_CELERY']:
                # Setup Celery loggers
                after_setup_task_logger.connect(
                    partial(self.celery_logger_setup, app=app),
                    weak=False
                )
                after_setup_logger.connect(
                    partial(self.celery_logger_setup, app=app),
                    weak=False
                )

            # Werkzeug only adds a stream handler if there's no other handlers
            # defined, so when Sentry adds a log handler no output is
            # received from Werkzeug unless we install a console handler
            #  here on the werkzeug logger.
            if app.debug:
                logger = logging.getLogger('werkzeug')
                logger.setLevel(logging.INFO)
                handler = logging.StreamHandler()
                logger.addHandler(handler)

    def init_config(self, app):
        """Initialize configuration."""

    def celery_logger_setup(self, app=None, sender=None, logger=None,
                            **kwargs):
        """Add handler."""
        self.add_handler(logger, app)


class InvenioSanitizeProcessor(SanitizePasswordsProcessor):
    """Remove additional sensitve configuration from Sentry data."""

    FIELDS = frozenset([
        'access_token'
    ])
