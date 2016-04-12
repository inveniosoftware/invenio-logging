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

"""File system logging test."""

from __future__ import absolute_import, print_function

from logging.handlers import RotatingFileHandler
from os.path import exists, join

import pytest
from flask import Flask

from invenio_logging.fs import InvenioLoggingFS


def test_init(tmppath):
    """Test extension initialization."""
    app = Flask('testapp')
    InvenioLoggingFS(app)
    assert 'invenio-logging-fs' not in app.extensions

    ext = InvenioLoggingFS()
    app = Flask('testapp')
    ext.init_app(app)
    assert 'invenio-logging-fs' not in app.extensions

    logfile = join(tmppath, 'test.log')
    app = Flask('testapp')
    app.config.update(dict(LOGGING_FS_LOGFILE=logfile))
    InvenioLoggingFS(app)
    assert 'invenio-logging-fs' in app.extensions
    assert app.config['LOGGING_FS_LEVEL'] == 'WARNING'


def test_filepath_formatting(tmppath):
    """Test extension initialization."""
    app = Flask('testapp', instance_path=tmppath)
    app.config.update(dict(
        DEBUG=True,
        LOGGING_FS_LOGFILE='{instance_path}/testapp.log'
    ))
    InvenioLoggingFS(app)
    assert app.config['LOGGING_FS_LOGFILE'] == join(tmppath, 'testapp.log')
    assert app.config['LOGGING_FS_LEVEL'] == 'DEBUG'


def test_missing_dir(tmppath):
    """Test missing dir."""
    app = Flask('testapp')
    filepath = join(tmppath, 'invaliddir/test.log')
    app.config.update(dict(LOGGING_FS_LOGFILE=filepath))
    assert pytest.raises(ValueError, InvenioLoggingFS, app)


def test_warnings(tmppath, pywarnlogger):
    """Test extension initialization."""
    app = Flask('testapp', instance_path=tmppath)
    app.config.update(dict(
        LOGGING_FS_LOGFILE='{instance_path}/testapp.log',
        LOGGING_FS_PYWARNINGS=True,
        LOGGING_FS_LEVEL='WARNING'
    ))
    InvenioLoggingFS(app)
    assert RotatingFileHandler in [x.__class__ for x in pywarnlogger.handlers]


def test_logging(tmppath):
    """Test extension initialization."""
    filepath = join(tmppath, 'test.log')
    app = Flask('testapp')
    app.config.update(dict(
        LOGGING_FS_LOGFILE=filepath,
        LOGGING_FS_LEVEL='WARNING'
    ))
    InvenioLoggingFS(app)
    # Test delay opening of file
    assert not exists(filepath)
    app.logger.warn('My warning')
    assert exists(filepath)
    app.logger.info('My info')
    # Test log level
    with open(filepath) as fp:
        content = fp.read()
    assert 'My warning' in content
    assert 'My info' not in content
