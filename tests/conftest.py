# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

from __future__ import absolute_import, print_function

import logging
import shutil
import tempfile

import pytest


@pytest.yield_fixture()
def tmppath():
    """Make a temporary directory."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir)


@pytest.yield_fixture()
def pywarnlogger():
    """Rest the py.warnings logger."""
    logger = logging.getLogger('py.warnings')
    yield logger
    logger.handlers = []
