# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio OpenSearch Datastream Logging module."""

from __future__ import absolute_import, print_function

from importlib_metadata import entry_points

from . import config
from .datastreams.managers import LogManager
from .ext import InvenioLoggingBase


class InvenioLoggingDatastreams(InvenioLoggingBase):
    """Invenio-Logging extension for OpenSearch Datastreams."""

    def init_app(self, app):
        """Initialize app.

        :param app: An instance of :class:`~flask.Flask`.
        """
        self.init_manager(app)
        self.load_builders()
        app.extensions["invenio-logging-datastreams"] = self

    def init_manager(self, app):
        """Initialize the logging manager."""
        manager = LogManager()
        self.manager = manager

    def load_builders(self):
        """Load log builders from entry points."""
        for ep in entry_points(group="invenio_logging.datastreams.builders"):
            builder_class = ep.load()
            self.manager.register_builder(ep.name, builder_class)
