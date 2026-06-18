# SPDX-FileCopyrightText: 2016-2018 CERN.
# SPDX-License-Identifier: MIT

"""Invenio filesystem logging module.

This extension is enabled by default and automatically installed via
``invenio_base.apps`` and ``invenio_base.api_apps`` entry points.
"""

from __future__ import absolute_import, print_function

import logging

from flask.logging import default_handler

from . import config
from .ext import InvenioLoggingBase

handler = logging.StreamHandler()


class InvenioLoggingConsole(InvenioLoggingBase):
    """Invenio-Logging extension for console."""

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)

        if not app.config["LOGGING_CONSOLE"]:
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
        """Install logging handler."""
        if handler in app.logger.handlers:
            return

        if app.config["LOGGING_CONSOLE_PYWARNINGS"]:
            self.capture_pywarnings(handler)

        if app.config["LOGGING_CONSOLE_LEVEL"] is not None:
            handler.setLevel(app.config["LOGGING_CONSOLE_LEVEL"])

        # Add the handler to the app logger
        app.logger.addHandler(handler)

        # Remove the (likely unconfigured) Flask default handler
        app.logger.removeHandler(default_handler)
