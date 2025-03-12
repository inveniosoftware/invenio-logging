# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Datastream log event."""

from abc import ABC, abstractmethod
from datetime import datetime


class BaseLogEvent(ABC):
    """Class to represent a structured log event."""

    def __init__(
        self,
        log_type="application",
        timestamp=None,
        event={},
        message=None,
    ):
        """
        Create a LogEvent instance.

        :param log_type: Type of log event.
        :param timestamp: Optional timestamp (defaults to now).
        :param event: Dict with `action` (required) and optional `description`.
        :param message: Optional human-readable message.
        """
        self.type = log_type
        self.timestamp = timestamp or datetime.now().isoformat()
        self.event = event
        self.message = message

    @abstractmethod
    def to_dict(self):
        """Convert the log event to a dictionary matching the schema."""
        raise NotImplementedError()
