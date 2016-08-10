# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

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
