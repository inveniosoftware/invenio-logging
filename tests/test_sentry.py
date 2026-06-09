# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
# Copyright (C) 2026 CESNET z.s.p.o.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Sentry logging tests."""

from __future__ import absolute_import, print_function

import time
from unittest.mock import patch

from flask import Flask
from sentry_sdk.hub import Hub
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.flask import FlaskIntegration


def test_init():
    """Test initialization."""
    from invenio_logging.sentry import InvenioLoggingSentry

    app = Flask("testapp")
    InvenioLoggingSentry(app)
    assert "invenio-logging-sentry" not in app.extensions

    app = Flask("testapp")
    app.config["SENTRY_DSN"] = "http://user:pw@localhost/0"
    InvenioLoggingSentry(app)
    assert "invenio-logging-sentry" in app.extensions

    assert Hub.current and Hub.client
    if app.config["LOGGING_SENTRY_CELERY"]:
        assert Hub.current.get_integration(CeleryIntegration)
    else:
        assert Hub.current.get_integration(FlaskIntegration)


def test_sentry_failure():
    """Test that sentry works and logs a failure."""
    import sentry_sdk

    from invenio_logging.sentry import InvenioLoggingSentry

    app = Flask("testapp")
    app.config["SENTRY_DSN"] = "http://a-secret-hash@127.0.0.1:8000/1"
    InvenioLoggingSentry(app)

    sentry_transport = sentry_sdk.get_global_scope().client.transport

    with patch.object(sentry_transport, "_send_request") as mock_send_request:
        try:
            1 / 0
        except:
            app.logger.exception("Division by zero")

        # wait a bit for sentry-sdk to send the message
        time.sleep(2)

        mock_send_request.assert_called()

    assert sentry_sdk.last_event_id() is not None
