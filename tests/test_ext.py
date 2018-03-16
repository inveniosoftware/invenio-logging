# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Warnings capturing tests."""

from __future__ import absolute_import, print_function

import logging

from flask import Flask

from invenio_logging.ext import InvenioLoggingBase


def test_init(pywarnlogger):
    """Test extension initialization."""
    app = Flask('testapp')
    ext = InvenioLoggingBase(app)
    assert len(pywarnlogger.handlers) == 0

    # Capture warnings.
    handler = logging.StreamHandler()
    ext.capture_pywarnings(handler)
    assert len(pywarnlogger.handlers) == 1

    # Don't install the same handler twice (i.e. prevent multiple Flask apps
    # to install the same handlers and thus receiving double notifications)
    handler = logging.StreamHandler()
    ext.capture_pywarnings(handler)
    assert len(pywarnlogger.handlers) == 1

    # Different types of handlers are welcome
    handler = logging.NullHandler()
    ext.capture_pywarnings(handler)
    assert len(pywarnlogger.handlers) == 2
