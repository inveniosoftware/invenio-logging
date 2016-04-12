# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
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
