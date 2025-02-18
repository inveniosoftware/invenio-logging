# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


import pytest

from invenio_logging.datastreams.log_event import LogEvent
from invenio_logging.datastreams.managers import LogManager


class MockLogBuilder:
    def __init__(self):
        self.logs = []

    def build(self, log_event):
        return f"Log: {log_event['message']}"

    def send(self, log):
        self.logs.append(log)


def test_log_manager_initialization():
    log_manager = LogManager()
    assert log_manager.builders == {}


def test_register_builder():
    log_manager = LogManager()
    log_manager.register_builder("info", MockLogBuilder)
    assert "info" in log_manager.builders
    assert log_manager.builders["info"] == MockLogBuilder


def test_log_event():
    log_manager = LogManager()
    mock_builder = MockLogBuilder()
    log_manager.register_builder("info", mock_builder)

    log_event = LogEvent(
        message="Test event",
        event="test",
    )
    log_manager.log("info", log_event, async_mode=False)
    assert mock_builder.logs == ["Log: Test event"]


def test_log_event_no_builder():
    log_manager = LogManager()
    with pytest.raises(ValueError):
        log_event = LogEvent(message="Test event", event="test")
        log_manager.log("error", log_event, async_mode=False)
