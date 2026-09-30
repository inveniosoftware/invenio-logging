# SPDX-FileCopyrightText: 2015-2018 CERN.
# SPDX-License-Identifier: MIT

"""Invenio base logging module."""

from __future__ import absolute_import, print_function

import logging

from . import config
from .utils import add_request_id_filter, add_trace_context_filter


class InvenioLoggingBase(object):
    """Invenio-Logging extension for console."""

    def __init__(self, app=None):
        """Extension initialization.

        :param app: An instance of :class:`~flask.Flask`.
        """
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize app.

        :param app: An instance of :class:`~flask.Flask`.
        """
        # Default level is DEBUG, it's the handlers responsibility to
        # set the level that they want to log at.
        app.logger.setLevel(logging.DEBUG)

        # Add request_id filter to root logger so all handlers inherit it
        if add_request_id_filter not in app.logger.filters:
            app.logger.addFilter(add_request_id_filter)

    @staticmethod
    def configure_handler(app, handler):
        """Enrich managed handler records without replacing handlers or factories."""
        enabled = app.config.get("LOGGING_OTEL_ENABLED", config.LOGGING_OTEL_ENABLED)
        correlate = app.config.get(
            "LOGGING_OTEL_LOG_CORRELATION", config.LOGGING_OTEL_LOG_CORRELATION
        )
        if enabled and correlate:
            try:
                import opentelemetry.trace  # noqa: F401
            except ImportError as error:
                raise RuntimeError(
                    "Log correlation requires invenio-logging[opentelemetry]."
                ) from error
            handler.addFilter(add_trace_context_filter)
        else:
            handler.removeFilter(add_trace_context_filter)

    @staticmethod
    def capture_pywarnings(handler):
        """Log python system warnings."""
        logger = logging.getLogger("py.warnings")
        # Check for previously installed handlers.
        for h in logger.handlers:
            if isinstance(h, handler.__class__):
                return
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)
