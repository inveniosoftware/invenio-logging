# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Datastream Logging Builder module."""

from abc import ABC, abstractmethod

from marshmallow import ValidationError

from .schema import LogEventSchema


class LogBuilder(ABC):
    """Base log builder for structured logging."""

    context_generators = []
    """List of ContextGenerator to update log event context."""

    type = "generic"
    """Type of log event."""

    schema = LogEventSchema()
    """Schema for validating log events."""

    @classmethod
    def validate(cls, log_event):
        """Validate the log event against the schema."""
        try:
            return cls.schema.dump(log_event)
        except ValidationError as err:
            raise ValueError(f"Invalid log data: {err.messages}")

    @classmethod
    @abstractmethod
    def build(cls, **kwargs):
        """Build log event context based on log type and additional context."""
        raise NotImplementedError()

    @classmethod
    def resolve_context(cls, log_event):
        """Resolve all references in the log context."""
        for ctx_func in cls.context_generators:
            ctx_func(log_event)
        return log_event

    @classmethod
    def send(cls, log_event):
        """Send log event to the log backend."""
        raise NotImplementedError()

    def search(self, query):
        """Search logs."""
        raise NotImplementedError()
