# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Sentry logging module."""

from __future__ import absolute_import, print_function

import logging
import warnings

import pkg_resources
import six
from flask import g
from werkzeug.utils import import_string

from . import config
from .ext import InvenioLoggingBase

try:
    pkg_resources.get_distribution('raven')
    from raven.processors import Processor
except pkg_resources.DistributionNotFound:
    class Processor(object):
        """Dummy class in case Sentry is not installed.."""

        def __init__(self, *args, **kwargs):
            """Do nothing."""
            pass


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
        for k in dir(config):
            if k.startswith('LOGGING_SENTRY') or k.startswith('SENTRY_'):
                app.config.setdefault(k, getattr(config, k))

    def install_handler(self, app):
        """Install log handler."""
        level = getattr(logging, app.config['LOGGING_SENTRY_LEVEL'])
        logging_exclusions = None
        if not app.config['LOGGING_SENTRY_PYWARNINGS']:
            logging_exclusions = (
                'raven',
                'gunicorn',
                'south',
                'sentry.errors',
                'django.request',
                'dill',
                'py.warnings')
        if app.config['SENTRY_SDK']:
            self.install_sentry_sdk_handler(app, logging_exclusions, level)
        else:
            self.install_raven_handler(app, logging_exclusions, level)

        # Werkzeug only adds a stream handler if there's no other handlers
        # defined, so when Sentry adds a log handler no output is
        # received from Werkzeug unless we install a console handler
        # here on the werkzeug logger.
        if app.debug:
            logger = logging.getLogger('werkzeug')
            logger.setLevel(logging.INFO)
            logger.addHandler(logging.StreamHandler())

    def install_sentry_sdk_handler(self, app, logging_exclusions, level):
        """Install sentry-python sdk log handler."""
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        from sentry_sdk.integrations.celery import CeleryIntegration
        from sentry_sdk import configure_scope

        integrations = [FlaskIntegration()]
        if app.config['LOGGING_SENTRY_CELERY']:
            integrations.append(CeleryIntegration())

        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            in_app_exclude=logging_exclusions,
            integrations=integrations,
            before_send=self.add_request_id_sentry_python,
        )
        with configure_scope() as scope:
            scope.level = level

    def install_raven_handler(self, app, logging_exclusions, level):
        """Install raven log handler."""
        warnings.warn('The Raven library will be depricated.',
                      PendingDeprecationWarning)
        from raven.contrib.celery import register_logger_signal, \
            register_signal
        from raven.contrib.flask import Sentry
        from raven.handlers.logging import SentryHandler

        cls = app.config['LOGGING_SENTRY_CLASS']
        if cls:
            if isinstance(cls, six.string_types):
                cls = import_string(cls)
        else:
            cls = Sentry
        sentry = cls(
            app,
            logging=True,
            level=level,
            logging_exclusions=logging_exclusions,
        )
        app.logger.addHandler(SentryHandler(client=sentry.client, level=level))

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

    def add_request_id_sentry_python(self, event, hint):
        """Add the request id as a tag."""
        if g and hasattr(g, 'request_id'):
            tags = event.get('tags') or []
            tags.append(['request_id', g.request_id])
            event['tags'] = tags
        return event


class RequestIdProcessor(Processor):
    """Sentry event request processor for adding the request id as a tag."""

    def process(self, data, **kwargs):
        """Process event data."""
        data = super(RequestIdProcessor, self).process(data, **kwargs)
        if g and hasattr(g, 'request_id'):
            tags = data.get('tags', {})
            tags['request_id'] = g.request_id
            data['tags'] = tags
        return data
