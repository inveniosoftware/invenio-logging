# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

from __future__ import absolute_import, print_function

import shutil
import tempfile
from datetime import datetime

import pytest
from flask import Flask
from invenio_search import InvenioSearch

from invenio_logging.engine.log_event import BaseLogEvent


class LogEvent(BaseLogEvent):
    """Class to represent a structured log event."""

    def __init__(
        self,
        log_type="application",
        event={},
        resource={},
        user={},
        extra={},
        timestamp=None,
        message=None,
    ):
        """
        Create a LogEvent instance.

        :param log_type: Type of log event.
        :param event: Dict with `action` (required) and optional `description`.
        :param resource: Dict with `type`, `id`, and optional `metadata`.
        :param user: Dict with `id`, `email`, and optional `roles` (default: empty).
        :param extra: Additional metadata dictionary (default: empty).
        :param timestamp: Optional timestamp (defaults to now).
        :param message: Optional human-readable message.
        """
        super().__init__(log_type, timestamp, event, message)
        self.resource = resource
        self.user = user
        self.extra = extra

    def to_dict(self):
        """Convert the log event to a dictionary matching the schema."""
        return {
            "timestamp": self.timestamp,
            "event": self.event,
            "message": self.message,
            "user": self.user,
            "resource": self.resource,
            "extra": self.extra,
        }


@pytest.fixture(scope="module")
def log_event_class():
    """Return the LogEvent class."""
    return LogEvent


@pytest.fixture(scope="module")
def valid_log_event():
    """Return a valid log event."""
    log_event = LogEvent(
        log_type="test",
        message="Test log message",
        event=dict(action="test"),
        resource=dict(id="1", type="test"),
        user=dict(id="1"),
        timestamp=datetime.now().isoformat(),
    )
    return log_event.to_dict()


@pytest.fixture(scope="module")
def invalid_log_event():
    """Return an invalid log event."""
    log_event = LogEvent(
        log_type="test",
        message="Test log message",
        event="test",
    )
    return log_event.to_dict()


@pytest.fixture()
def app(entry_points):
    """Flask application fixture."""
    # Set temporary instance path for sqlite
    instance_path = tempfile.mkdtemp()
    app = Flask("testapp", instance_path=instance_path)
    app.config.update(TESTING=True)
    InvenioSearch(app)

    with app.app_context():
        yield app

    # Teardown instance path.
    shutil.rmtree(instance_path)
