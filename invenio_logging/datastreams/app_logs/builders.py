# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Loggigng module for app."""

from invenio_logging.datastreams.builders import LogBuilder

from .backends import SearchAppLogBackend


class AppLogBuilder(LogBuilder):
    """Builder for structured app logs."""

    type = "app"

    backend_cls = SearchAppLogBackend

    @classmethod
    def build(cls, log_event):
        """Build an app log event context."""
        return cls.validate(log_event)

    @classmethod
    def send(cls, log_event):
        """Send log event using the backend."""
        cls.backend_cls().send(log_event)

    @classmethod
    def search(cls, query):
        """Search logs."""
        return cls.backend_cls().search(query)
