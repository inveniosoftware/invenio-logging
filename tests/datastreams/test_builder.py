# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests for LogBuilder."""

from datetime import datetime

import pytest

from invenio_logging.engine.builders import LogBuilder


class TestLogBuilder(LogBuilder):
    """Concrete implementation of LogBuilder for testing."""

    @classmethod
    def build(cls, **kwargs):
        """Build log event context based on log type and additional context."""
        return {"type": cls.type, **kwargs}

    @classmethod
    def send(cls, log_event):
        """Send log event to the log backend."""
        return True


def test_validate_valid_log_event(valid_log_event):
    """Test validation of a valid log event."""
    validated_event = TestLogBuilder.validate(valid_log_event)
    assert validated_event["@timestamp"].isoformat() == valid_log_event["timestamp"]
    assert validated_event["message"] == valid_log_event["message"]
    assert validated_event["event"] == valid_log_event["event"]
    assert validated_event["resource"] == valid_log_event["resource"]
    assert validated_event["user"] == valid_log_event["user"]


def test_validate_invalid_log_event(invalid_log_event):
    """Test validation of an invalid log event."""
    with pytest.raises(ValueError):
        TestLogBuilder.validate(invalid_log_event)


def test_build_log_event():
    """Test building a log event."""
    log_event = TestLogBuilder.build(message="Test log message")
    assert log_event["type"] == "generic"
    assert log_event["message"] == "Test log message"


def test_resolve_context():
    """Test resolving context in a log event."""

    def add_context(log_event):
        log_event["context"] = "test_context"

    TestLogBuilder.context_generators = [add_context]
    log_event = {"message": "Test log message"}
    resolved_event = TestLogBuilder.resolve_context(log_event)
    assert resolved_event["context"] == "test_context"


def test_send_log_event():
    """Test sending a log event."""
    log_event = {"message": "Test log message"}
    assert TestLogBuilder.send(log_event) == True
