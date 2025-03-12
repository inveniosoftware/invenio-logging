# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for datastream logging management."""

from .log_event import BaseLogEvent
from .tasks import log_event_task


class LogManager:
    """Manager for handling logging builders."""

    def __init__(self):
        """Initialize the log manager with builders."""
        self.builders = {}

    def log(self, log_event, async_mode=True):
        """
        Log an event using the correct builder.

        :param log_event: Instance of LogEvent.
        :param async_mode: If True, sends logs via Celery.
        """
        if log_event.type not in self.builders:
            raise ValueError(
                f"No log builder found for type '{log_event.type}'. Available types: {self.builders.keys()}"
            )
        if not isinstance(log_event, BaseLogEvent):
            raise ValueError("log_event must be an instance of BaseLogEvent")

        log_data = log_event.to_dict()

        if async_mode:
            log_event_task.delay(log_event.type, log_data)
        else:
            log_builder = self.builders[log_event.type]
            log = log_builder.build(log_data)
            log_builder.send(log)

    def search(self, log_type, query):
        """
        Search for logs using the correct builder.
        """
        if log_type not in self.builders:
            raise ValueError(
                f"No log builder found for type '{log_type}'. Available types: {self.builders.keys()}"
            )

        log_builder = self.builders[log_type]
        return log_builder.search(query)

    def list(self, log_type):
        """
        List logs using the correct builder.
        """
        if log_type not in self.builders:
            raise ValueError(
                f"No log builder found for type '{log_type}'. Available types: {self.builders.keys()}"
            )

        log_builder = self.builders[log_type]
        return log_builder.list()

    def register_builder(self, log_type, builder_class):
        """Register a log builder."""
        self.builders[log_type] = builder_class
