# SPDX-FileCopyrightText: 2016-2018 CERN.
# SPDX-License-Identifier: MIT

"""Console logging test."""

from __future__ import absolute_import, print_function

import logging

import pytest
from flask import Flask
from flask.logging import default_handler

from invenio_logging import console as console_module
from invenio_logging.console import InvenioLoggingConsole
from invenio_logging.utils import add_trace_context_filter


@pytest.fixture(autouse=True)
def console_state(monkeypatch):
    """Isolate process-wide console settings without leaking handler mutations."""
    monkeypatch.setattr(console_module, "_console_settings", None)
    formatter, filters, level = (
        default_handler.formatter,
        list(default_handler.filters),
        default_handler.level,
    )
    yield
    default_handler.setFormatter(formatter)
    default_handler.filters = filters
    default_handler.setLevel(level)


def test_init():
    """Test extension initialization."""
    app = Flask("testapp")
    InvenioLoggingConsole(app)
    assert "invenio-logging-console" in app.extensions

    ext = InvenioLoggingConsole()
    app = Flask("testapp")
    ext.init_app(app)
    assert "invenio-logging-console" in app.extensions

    app = Flask("testapp")
    app.config.update(dict(LOGGING_CONSOLE=False))
    InvenioLoggingConsole(app)
    assert "invenio-logging-console" not in app.extensions


def test_conf():
    """Test extension initialization."""
    app = Flask("testapp")
    InvenioLoggingConsole(app)
    assert app.config["LOGGING_CONSOLE_PYWARNINGS"] is False
    assert app.config["LOGGING_CONSOLE_LEVEL"] is None
    app = Flask("testapp")
    app.config.update(dict(DEBUG=True, LOGGING_CONSOLE_LEVEL="ERROR"))
    InvenioLoggingConsole(app)
    assert app.config["LOGGING_CONSOLE_PYWARNINGS"] is True
    app.logger.level == logging.ERROR


def test_warnings(pywarnlogger):
    """Test extension initialization."""
    app = Flask("testapp")
    InvenioLoggingConsole(app)
    assert logging.StreamHandler in [x.__class__ for x in pywarnlogger.handlers]


@pytest.mark.parametrize(
    "ui_settings,api_settings",
    [
        (
            {"LOGGING_CONSOLE_FORMAT": "ui %(message)s"},
            {"LOGGING_CONSOLE_FORMAT": None},
        ),
        (
            {"LOGGING_CONSOLE_FORMAT": None},
            {"LOGGING_CONSOLE_FORMAT": "api %(message)s"},
        ),
        ({"LOGGING_OTEL_ENABLED": True}, {"LOGGING_OTEL_ENABLED": False}),
        ({"LOGGING_OTEL_ENABLED": False}, {"LOGGING_OTEL_ENABLED": True}),
        (
            {"LOGGING_OTEL_ENABLED": True, "LOGGING_OTEL_LOG_CORRELATION": True},
            {"LOGGING_OTEL_ENABLED": True, "LOGGING_OTEL_LOG_CORRELATION": False},
        ),
    ],
)
def test_conflicting_app_settings_rejected(ui_settings, api_settings):
    """Reject UI/API conflicts before changing the first app's shared handler."""
    ui, api = Flask("console-ui"), Flask("console-api")
    ui.config.update(ui_settings)
    api.config.update(api_settings)
    InvenioLoggingConsole(ui)
    formatter = default_handler.formatter
    filters = list(default_handler.filters)
    with pytest.raises(ValueError, match="must agree across apps"):
        InvenioLoggingConsole(api)
    assert default_handler.formatter is formatter
    assert default_handler.filters == filters
    assert "invenio-logging-console" not in api.extensions


def test_matching_app_settings_idempotent():
    """Consistent UI/API settings reuse the handler without duplicating filters."""
    ui, api = Flask("console-ui"), Flask("console-api")
    settings = {
        "LOGGING_CONSOLE_FORMAT": "%(trace_id)s %(message)s",
        "LOGGING_OTEL_ENABLED": True,
    }
    ui.config.update(settings)
    api.config.update(settings)
    InvenioLoggingConsole(ui)
    InvenioLoggingConsole(api)
    InvenioLoggingConsole(api)
    assert default_handler.filters.count(add_trace_context_filter) == 1
    record = logging.makeLogRecord({"msg": "shared console", "trace_id": "trace-test"})
    assert default_handler.formatter.format(record) == "trace-test shared console"


def test_default_settings_restore_clean_handler():
    """None explicitly selects the default formatter and disabled correlation."""
    default_handler.setFormatter(logging.Formatter("stale %(trace_id)s %(message)s"))
    default_handler.addFilter(add_trace_context_filter)
    app = Flask("console-default")
    InvenioLoggingConsole(app)
    assert default_handler.formatter is console_module._default_formatter
    assert add_trace_context_filter not in default_handler.filters


def test_effective_correlation_settings():
    """Disabled correlation can share the handler regardless of tracing enablement."""
    ui, api = Flask("console-ui"), Flask("console-api")
    ui.config.update(LOGGING_OTEL_ENABLED=True, LOGGING_OTEL_LOG_CORRELATION=False)
    api.config.update(LOGGING_OTEL_ENABLED=False, LOGGING_OTEL_LOG_CORRELATION=True)
    InvenioLoggingConsole(ui)
    InvenioLoggingConsole(api)
    assert add_trace_context_filter not in default_handler.filters
