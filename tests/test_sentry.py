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

"""Sentry logging tests."""

from __future__ import absolute_import, print_function

import logging

import httpretty
import pytest
from celery.utils.log import get_task_logger
from flask import Flask, request
from flask_celeryext import create_celery_app
from flask_login import LoginManager, UserMixin, login_user
from mock import patch


def test_init():
    """Test initialization."""
    from invenio_logging.sentry import InvenioLoggingSentry

    app = Flask('testapp')
    InvenioLoggingSentry(app)
    assert 'invenio-logging-sentry' not in app.extensions

    app = Flask('testapp')
    app.config['SENTRY_DSN'] = 'http://user:pw@localhost/0'
    InvenioLoggingSentry(app)
    assert 'invenio-logging-sentry' in app.extensions
    assert 'sentry' in app.extensions


def test_custom_class(pywarnlogger):
    """Test stream handler."""
    from invenio_logging.sentry import InvenioLoggingSentry
    app = Flask('testapp')
    app.config['SENTRY_DSN'] = 'http://user:pw@localhost/0'
    app.config['LOGGING_SENTRY_CLASS'] = 'invenio_logging.sentry6:Sentry6'
    InvenioLoggingSentry(app)
    from invenio_logging.sentry6 import Sentry6
    assert isinstance(app.extensions['sentry'], Sentry6)


def test_stream_handler_in_debug(pywarnlogger):
    """Test stream handler."""
    from invenio_logging.sentry import InvenioLoggingSentry
    app = Flask('testapp')
    app.debug = True
    app.config['SENTRY_DSN'] = 'http://user:pw@localhost/0'
    InvenioLoggingSentry(app)
    logger = logging.getLogger('werkzeug')
    assert logging.StreamHandler in [x.__class__ for x in logger.handlers]


def test_sentry_handler_attached_to_app_logger():
    from invenio_logging.sentry import InvenioLoggingSentry
    from raven.handlers.logging import SentryHandler
    app = Flask('testapp')
    app.config['SENTRY_DSN'] = 'http://user:pw@localhost/0'
    InvenioLoggingSentry(app)
    assert any(
        [
            isinstance(logger, SentryHandler) for logger in app.logger.handlers
        ]
    )


def test_pywarnings(pywarnlogger):
    """Test celery."""
    from invenio_logging.sentry import InvenioLoggingSentry
    app = Flask('testapp')
    app.config.update(dict(
        SENTRY_DSN='http://user:pw@localhost/0',
        LOGGING_SENTRY_PYWARNINGS=True,
    ))
    assert len(pywarnlogger.handlers) == 0
    InvenioLoggingSentry(app)
    assert len(pywarnlogger.handlers) == 1


def test_import():
    """Test that raven is not required."""
    with patch('raven.contrib.flask.Sentry') as mod:
        mod.side_effect = ImportError
        # We can import and install extension with out hitting the import
        # unless SENTRY_DSN is set.
        from invenio_logging.sentry import InvenioLoggingSentry
        app = Flask('testapp')
        InvenioLoggingSentry(app)

        app = Flask('testapp')
        app.config['SENTRY_DSN'] = '....'
        pytest.raises(ImportError, InvenioLoggingSentry, app)


@httpretty.activate
def test_celery():
    """Test celery."""
    from invenio_logging.sentry import InvenioLoggingSentry
    app = Flask('testapp')
    app.config.update(dict(
        SENTRY_DSN='http://user:pw@localhost/0',
        SENTRY_TRANSPORT='raven.transport.http.HTTPTransport',
        LOGGING_SENTRY_CELERY=True,
        CELERY_ALWAYS_EAGER=True,
        CELERY_RESULT_BACKEND="cache",
        CELERY_CACHE_BACKEND="memory",
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
    ))
    InvenioLoggingSentry(app)
    celery = create_celery_app(app)

    @celery.task
    def test_task():
        logger = get_task_logger(__name__)
        logger.error('CELERYTEST')

    httpretty.register_uri(
        httpretty.POST,
        'http://localhost/api/0/store/',
        body='[{"title": "Test"}]',
        content_type='application/json',
        status=200,
    )
    test_task.delay()
    # Give sentry time to send request
    from time import sleep
    sleep(1)
    assert httpretty.last_request().path == '/api/0/store/'


def test_sentry6():
    """Test Sentry 6."""
    from invenio_logging.sentry import InvenioLoggingSentry
    app = Flask('testapp')
    app.config.update(dict(
        SENTRY_DSN='http://user:pw@localhost/0',
        LOGGING_SENTRY_CLASS='invenio_logging.sentry6:Sentry6',
        SENTRY_USER_ATTRS=['name'],
        SECRET_KEY='CHANGEME',
    ))
    InvenioLoggingSentry(app)
    LoginManager(app)

    class User(UserMixin):
        def __init__(self, user_id, name):
            self.id = user_id
            self.name = name

    with app.test_request_context('/'):
        assert app.extensions['sentry'].get_user_info(request) == {}

    with app.test_request_context('/'):
        login_user(User(1, 'viggo'))
        assert app.extensions['sentry'].get_user_info(request) == {
            'id': '1',
            'name': 'viggo',
        }
