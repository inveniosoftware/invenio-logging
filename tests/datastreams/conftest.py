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

from invenio_logging.engine.log_event import LogEvent


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
