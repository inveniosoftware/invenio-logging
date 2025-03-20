# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio OpenSearch Datastream Schema."""

from datetime import datetime
from enum import Enum
from marshmallow import EXCLUDE, Schema, fields
from marshmallow.validate import OneOf

class LogType(Enum):
    INFO = "INFO"
    ERROR = "ERROR"
    WARNING = "WARNING"
    DEBUG = "DEBUG"

class UserSchema(Schema):
    """User schema for logging."""

    id = fields.Str(required=True, description="User ID responsible for the event.")
    email = fields.Email(required=False, description="User email (if available).")
    roles = fields.List(
        fields.Str(), required=False, description="Roles assigned to the user."
    )


class EventSchema(Schema):
    """Event schema for logging."""

    action = fields.Str(
        required=True,
        description="The action that took place (e.g., created, deleted).",
    )
    description = fields.Str(
        required=False, description="Detailed description of the event."
    )


class ResourceSchema(Schema):
    """Resource schema to track affected entities."""

    type = fields.Str(
        required=True,
        description="Type of resource (e.g., record, community, user, file).",
    )
    id = fields.Str(required=True, description="Unique identifier of the resource.")
    metadata = fields.Dict(
        required=False, description="Optional metadata related to the resource."
    )
    parent = fields.Nested(
        "self",
        required=False,
        description="Optional parent resource, indicating hierarchy (e.g., a run inside a job).",
    )


class BaseDatastreamSchema(Schema):
    """Main schema for audit log events in InvenioRDM."""

    class Meta:
        """Meta class to ignore unknown fields."""

        unknown = EXCLUDE  # Ignore unknown fields

    timestamp = fields.DateTime(
        required=True,
        description="Timestamp when the event occurred.",
    )

    def load(self, data, **kwargs):
        """Transform `timestamp` to `@timestamp` on load."""
        loaded_data = super().load(data, **kwargs)
        if "timestamp" in loaded_data:
            loaded_data["@timestamp"] = loaded_data.pop("timestamp")
        return loaded_data

    def dump(self, obj, **kwargs):
        """Ensure `@timestamp` is converted to `datetime` before dumping."""
        if "@timestamp" in obj and isinstance(obj["@timestamp"], str):
            obj["timestamp"] = datetime.fromisoformat(obj["@timestamp"])
        return super().dump(obj, **kwargs)


class LogEventSchema(BaseDatastreamSchema):
    """Main schema for audit log events in InvenioRDM."""

    event = fields.Nested(EventSchema, required=True)
    message = fields.Str(
        required=True, description="Human-readable description of the event."
    )
    user = fields.Nested(
        UserSchema,
        required=False,
        description="Information about the user who triggered the event.",
    )
    resource = fields.Nested(
        ResourceSchema,
        required=True,
        description="Information about the affected resource.",
    )
    extra = fields.Dict(
        required=False, description="Additional structured metadata for logging."
    )
    status = fields.Str(
        required=True,
        description="The status type of event (e.g., INFO, ERROR, WARNING, DEBUG).",
        validate=OneOf([e.value for e in LogType])
    )