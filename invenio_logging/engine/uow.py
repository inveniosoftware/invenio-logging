# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Unit of work for datastream logging."""

from invenio_db.uow import Operation

from .log_event import BaseLogEvent
from invenio_logging.proxies import current_datastream_logging_manager


class LoggingOp(Operation):
    """A logging operation."""

    def __init__(self, log_event):
        """Initialize operation."""
        self._log_event = log_event

        if not isinstance(log_event, BaseLogEvent):
            raise ValueError("log_event must be an instance of BaseLogEvent")

    def on_post_commit(self, uow):
        """Log the event."""
        current_datastream_logging_manager.log(self._log_event)
