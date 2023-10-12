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

from flask import g

from . import config
from .ext import InvenioLoggingBase


class InvenioLoggingSentry(InvenioLoggingBase):
    """Invenio-Logging extension for Sentry."""

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)

        # Only configure Sentry if SENTRY_DSN is set.
        if app.config["SENTRY_DSN"] is None:
            return

        self.install_handler(app)

        app.extensions["invenio-logging-sentry"] = self

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith("LOGGING_SENTRY") or k.startswith("SENTRY_"):
                app.config.setdefault(k, getattr(config, k))

    def install_handler(self, app):
        """Install log handler."""
        level = getattr(logging, app.config["LOGGING_SENTRY_LEVEL"])
        logging_exclusions = None
        if not app.config["LOGGING_SENTRY_PYWARNINGS"]:
            logging_exclusions = (
                "gunicorn",
                "south",
                "sentry.errors",
                "django.request",
                "dill",
                "py.warnings",
            )

        self.install_sentry_sdk_handler(app, logging_exclusions, level)

        # Werkzeug only adds a stream handler if there's no other handlers
        # defined, so when Sentry adds a log handler no output is
        # received from Werkzeug unless we install a console handler
        # here on the werkzeug logger.
        if app.debug:
            logger = logging.getLogger("werkzeug")
            logger.setLevel(logging.INFO)
            logger.addHandler(logging.StreamHandler())

    def install_sentry_sdk_handler(self, app, logging_exclusions, level):
        """Install sentry-python sdk log handler."""
        import sentry_sdk
        from sentry_sdk import configure_scope
        from sentry_sdk.integrations.celery import CeleryIntegration
        from sentry_sdk.integrations.flask import FlaskIntegration
        from sentry_sdk.integrations.redis import RedisIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

        integrations = [FlaskIntegration()]
        init_kwargs = {}
        if app.config["LOGGING_SENTRY_CELERY"]:
            integrations.append(CeleryIntegration())
        if app.config["LOGGING_SENTRY_SQLALCHEMY"]:
            integrations.append(SqlalchemyIntegration())
        if app.config["LOGGING_SENTRY_REDIS"]:
            integrations.append(RedisIntegration())
        if app.config["LOGGING_SENTRY_INIT_KWARGS"]:
            init_kwargs = app.config["LOGGING_SENTRY_INIT_KWARGS"]

        sentry_sdk.init(
            dsn=app.config["SENTRY_DSN"],
            in_app_exclude=logging_exclusions,
            integrations=integrations,
            before_send=self.add_request_id_sentry_python,
            **init_kwargs
        )
        with configure_scope() as scope:
            scope.level = level

    def add_request_id_sentry_python(self, event, hint):
        """Add the request id as a tag."""
        if g and hasattr(g, "request_id"):
            tags = event.get("tags") or []
            tags.append(["request_id", g.request_id])
            event["tags"] = tags
        return event
