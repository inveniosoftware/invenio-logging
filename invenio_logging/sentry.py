# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
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

"""Sentry logging module.

Sentry can also be configured with the following variables (see raven for
further details):

- ``SENTRY_AUTO_LOG_STACKS``
- ``SENTRY_EXCLUDE_PATHS``
- ``SENTRY_INCLUDE_PATHS``
- ``SENTRY_MAX_LENGTH_LIST``
- ``SENTRY_MAX_LENGTH_STRING``
- ``SENTRY_NAME``
- ``SENTRY_PROCESSORS``
- ``SENTRY_RELEASE``
- ``SENTRY_SITE_NAME``
- ``SENTRY_TAGS``
- ``SENTRY_TRANSPORT``

Note that Celery does not deal well with threaded transport, so you should make
sure that your Celery workers are configured with:

.. code-block:: python

   SENTRY_TRANSPORT = 'raven.transport.http.HTTPTransport'
"""

from __future__ import absolute_import, print_function

import logging

import six
from werkzeug.utils import import_string

from .ext import InvenioLoggingBase


class InvenioLoggingSentry(InvenioLoggingBase):
    """Invenio-Logging extension for Sentry."""

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)

        # Only configure Sentry if SENTRY_DSN is set.
        if app.config['SENTRY_DSN'] is None:
            return

        self.install_handler(app)

        app.extensions['invenio-logging-sentry'] = self

    def init_config(self, app):
        """Initialize configuration."""
        app.config.setdefault('SENTRY_DSN', None)
        # Defaults to only reporting errors and warnings.
        app.config.setdefault('LOGGING_SENTRY_LEVEL', 'WARNING')
        # Send python warnings to Sentry?
        app.config.setdefault('LOGGING_SENTRY_PYWARNINGS', False)
        # Configure Celery?
        app.config.setdefault('LOGGING_SENTRY_CELERY', False)
        # Sentry Flask extension class - only needed in case you need to
        # overwrite something really deep down.
        app.config.setdefault('LOGGING_SENTRY_CLASS', None)
        # Sentry transport
        app.config.setdefault(
            'SENTRY_TRANSPORT',
            'raven.transport.threaded.ThreadedHTTPTransport'
        )

    def install_handler(self, app):
        """Install log handler."""
        from raven.contrib.celery import register_logger_signal, \
            register_signal
        from raven.contrib.flask import Sentry
        from raven.handlers.logging import SentryHandler

        # Installs sentry in app.extensions['sentry']
        level = getattr(logging, app.config['LOGGING_SENTRY_LEVEL'])

        # Get the Sentry class.
        cls = app.config['LOGGING_SENTRY_CLASS']
        if cls:
            if isinstance(cls, six.string_types):
                cls = import_string(cls)
        else:
            cls = Sentry

        sentry = cls(
            app,
            logging=True,
            level=level
        )

        # Capture warnings from warnings module
        if app.config['LOGGING_SENTRY_PYWARNINGS']:
            self.capture_pywarnings(
                SentryHandler(sentry.client))

        # Setup Celery logging to Sentry
        if app.config['LOGGING_SENTRY_CELERY']:
            try:
                register_logger_signal(sentry.client, loglevel=level)
            except TypeError:
                # Compatibility mode for Raven<=5.1.0
                register_logger_signal(sentry.client)
            register_signal(sentry.client)

        # Werkzeug only adds a stream handler if there's no other handlers
        # defined, so when Sentry adds a log handler no output is
        # received from Werkzeug unless we install a console handler
        # here on the werkzeug logger.
        if app.debug:
            logger = logging.getLogger('werkzeug')
            logger.setLevel(logging.INFO)
            logger.addHandler(logging.StreamHandler())
