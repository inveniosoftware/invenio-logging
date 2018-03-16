# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Console logging test."""

from __future__ import absolute_import, print_function

import logging

from flask import Flask

from invenio_logging.console import InvenioLoggingConsole


def test_init():
    """Test extension initialization."""
    app = Flask('testapp')
    InvenioLoggingConsole(app)
    assert 'invenio-logging-console' in app.extensions

    ext = InvenioLoggingConsole()
    app = Flask('testapp')
    ext.init_app(app)
    assert 'invenio-logging-console' in app.extensions

    app = Flask('testapp')
    app.config.update(dict(LOGGING_CONSOLE=False))
    InvenioLoggingConsole(app)
    assert 'invenio-logging-console' not in app.extensions


def test_conf():
    """Test extension initialization."""
    app = Flask('testapp')
    InvenioLoggingConsole(app)
    assert app.config['LOGGING_CONSOLE_PYWARNINGS'] is False
    assert app.config['LOGGING_CONSOLE_LEVEL'] is None
    app = Flask('testapp')
    app.config.update(dict(DEBUG=True, LOGGING_CONSOLE_LEVEL='ERROR'))
    InvenioLoggingConsole(app)
    assert app.config['LOGGING_CONSOLE_PYWARNINGS'] is True
    app.logger.level == logging.ERROR


def test_warnings(pywarnlogger):
    """Test extension initialization."""
    app = Flask('testapp')
    InvenioLoggingConsole(app)
    assert logging.StreamHandler in \
        [x.__class__ for x in pywarnlogger.handlers]
