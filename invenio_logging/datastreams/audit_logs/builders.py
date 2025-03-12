# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Datastream Logging Builder module."""

from invenio_logging.datastreams.builders import LogBuilder

from .backends import SearchAuditLogBackend


class AuditLogBuilder(LogBuilder):
    """Builder for structured audit logs."""

    type = "audit"

    backend_cls = SearchAuditLogBackend

    @classmethod
    def build(cls, log_event):
        """Build an audit log event context."""
        return cls.validate(log_event)

    @classmethod
    def send(cls, log_event):
        """Send log event using the backend."""
        cls.backend_cls().send(log_event)

    @classmethod
    def search(cls, query):
        """Search logs."""
        return cls.backend_cls().search(query)

    @classmethod
    def list(cls):
        """List audit logs."""
        results = cls.backend_cls().list()
        return cls.schema.dump(results, many=True)
