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

"""Module providing logging capabilities.

Invenio-Logging is a core component of Invenio responsible for configuring
a loggers of your Flask application. The loggers are exposing standard Python
interface for creating log records and installing predefined handlers.

There are following logger extensions:

- :class:`~invenio_logging.console.InvenioLoggingConsole`
- :class:`~invenio_logging.fs.InvenioLoggingFS`
- :class:`~invenio_logging.sentry.InvenioLoggingSentry`

Initialization
--------------
First make sure you have Flask application with Click support (meaning
Flask 0.11+):

>>> from flask import Flask
>>> app = Flask('myapp')

Next, initialize your logging extensions:

>>> from invenio_logging.console import InvenioLoggingConsole
>>> from invenio_logging.fs import InvenioLoggingFS
>>> console = InvenioLoggingConsole(app)
>>> fs = InvenioLoggingFS(app)

In order for the following examples to work, you need to work within an
Flask application context so let's push one:

>>> ctx = app.app_context()
>>> ctx.push()

Logging
-------
There are situations when you want to get informed about invalid user input,
application misbehavior, or third-party service problems.

>>> app.logger.debug('Where am I?')
>>> app.logger.info('Hello world!')
>>> app.logger.warning('Be carefull with overlogging.')
>>> app.logger.error('Connection could not be initialized.')
>>> app.logger.exception('You should not divide by zero!')

For more information about logging in Flask please follow:

 * http://flask.pocoo.org/docs/0.11/quickstart/#logging

"""

from __future__ import absolute_import, print_function

from .version import __version__

__all__ = (
    '__version__',
)
