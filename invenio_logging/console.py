# SPDX-FileCopyrightText: 2016-2018 CERN.
# SPDX-License-Identifier: MIT

"""Invenio filesystem logging module.

This extension is enabled by default and automatically installed via
``invenio_base.apps`` and ``invenio_base.api_apps`` entry points.
"""

from __future__ import absolute_import, print_function

import logging
from threading import Lock

from flask.logging import default_handler

from . import config
from .ext import InvenioLoggingBase

_default_formatter = default_handler.formatter
_console_settings = None
_console_lock = Lock()


class InvenioLoggingConsole(InvenioLoggingBase):
    """Invenio-Logging extension for console."""

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)

        if not app.config["LOGGING_CONSOLE"]:
            app.logger.removeHandler(default_handler)
            return

        self.install_handler(app)

        app.extensions["invenio-logging-console"] = self

    def init_config(self, app):
        """Initialize config."""
        app.config.setdefault("LOGGING_CONSOLE", True)
        app.config.setdefault("LOGGING_CONSOLE_PYWARNINGS", app.debug)
        for k in dir(config):
            if k.startswith("LOGGING_CONSOLE"):
                app.config.setdefault(k, getattr(config, k))

    def install_handler(self, app):
        """Configure the shared handler only with consistent formatting settings."""
        global _console_settings

        log_format = app.config["LOGGING_CONSOLE_FORMAT"]
        correlation = bool(
            app.config.get("LOGGING_OTEL_ENABLED", config.LOGGING_OTEL_ENABLED)
            and app.config.get(
                "LOGGING_OTEL_LOG_CORRELATION", config.LOGGING_OTEL_LOG_CORRELATION
            )
        )
        settings = (log_format, correlation)
        with _console_lock:
            if _console_settings is not None and settings != _console_settings:
                raise ValueError(
                    "LOGGING_CONSOLE_FORMAT and effective OpenTelemetry log "
                    "correlation must agree across apps sharing Flask's console "
                    "handler. Change the process configuration and restart."
                )
            formatter = (
                logging.Formatter(log_format)
                if log_format is not None
                else _default_formatter
            )
            handler = default_handler
            self.configure_handler(app, handler)
            handler.setFormatter(formatter)
            if app.config["LOGGING_CONSOLE_PYWARNINGS"]:
                self.capture_pywarnings(handler)
            if app.config["LOGGING_CONSOLE_LEVEL"] is not None:
                handler.setLevel(app.config["LOGGING_CONSOLE_LEVEL"])
            _console_settings = settings
