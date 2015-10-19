# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
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

"""Pytest configuration."""

from __future__ import absolute_import, print_function

import shutil
import tempfile

import pytest
from flask import Flask
from flask.ext.babelex import Babel

from invenio_logging.fs import InvenioLoggingFs
from invenio_logging.sentry import InvenioLoggingSentry


@pytest.fixture
def generic_app():
    app = Flask('testapp')
    app.config.update(TESTING=True)
    return app


@pytest.fixture()
def app_for_sentry(request):

    app = Flask('testapp')
    app.config.update(
        TESTING=True
    )
    app.config["LOGGING_SENTRY_CELERY"] = False

    app.config['SENTRY_INCLUDE_PATHS'] = []
    app.config[
        'SENTRY_DSN'] = "http://f1399efc64ae4ce8aaa1ee9ceeed899a:425e15e651" \
                        "5d44149212f196a1be0264@app.getsentry.com/55471"  #
    Babel(app)

    return app


@pytest.fixture()
def app_for_fs(request):
    """Flask application fixture."""
    instance_path = tempfile.mkdtemp()

    app = Flask('testapp', instance_path=instance_path)
    app.config.update(
        TESTING=True
    )
    Babel(app)

    app.logger_name = "testapp"

    def teardown():
        shutil.rmtree(instance_path)

    request.addfinalizer(teardown)

    return app
