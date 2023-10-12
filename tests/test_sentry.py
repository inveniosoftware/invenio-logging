# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Sentry logging tests."""

from __future__ import absolute_import, print_function

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
