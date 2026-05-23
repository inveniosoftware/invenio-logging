# SPDX-FileCopyrightText: 2015-2018 CERN.
# SPDX-License-Identifier: MIT

"""Pytest configuration."""

from __future__ import absolute_import, print_function

import logging
import shutil
import tempfile

import pytest
from mock import Mock, patch


@pytest.yield_fixture()
def tmppath():
    """Make a temporary directory."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir)


@pytest.yield_fixture()
def pywarnlogger():
    """Rest the py.warnings logger."""
    logger = logging.getLogger("py.warnings")
    yield logger
    logger.handlers = []


@pytest.yield_fixture()
def sentry_emit():
    """Mock Sentry emit."""
    from raven.handlers.logging import SentryHandler

    with patch.object(SentryHandler, "emit") as sentry_emit:
        yield sentry_emit
