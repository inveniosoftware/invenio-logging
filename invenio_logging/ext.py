# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio base logging module."""

from __future__ import absolute_import, print_function

import logging

from .utils import add_request_id_filter


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
    def capture_pywarnings(handler):
        """Log python system warnings."""
        logger = logging.getLogger("py.warnings")
        # Check for previously installed handlers.
        for h in logger.handlers:
            if isinstance(h, handler.__class__):
                return
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)
