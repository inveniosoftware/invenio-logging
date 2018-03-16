# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module providing logging capabilities.

Invenio-Logging is a core component of Invenio responsible for configuring
the Flask application logger. The Flask application logger exposes the standard
Python logging interface for creating log records and installing predefined
handlers.

The following logger extensions exists:

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

>>> app.app_context().push()

Logging
-------
All application logging should happen via the Flask application logger to
ensure that you only have to configure one logger in order to route log
messages to your desired logging infrastructure.

In Invenio modules this is easily achieved by simply using the Flask current
application context:

>>> from flask import current_app
>>> current_app.logger.debug('Where am I?')
>>> current_app.logger.info('Hello world!')
>>> current_app.logger.warning('Be carefull with overlogging.')
>>> current_app.logger.error('Connection could not be initialized.')
>>> current_app.logger.exception('You should not divide by zero!')

Note that ``logger.exception()`` will automatically include the exception
stacktrace in the log record, which each log handler may decide to include or
not in its output.

You may also manually include exception information in the logger using the
``exc_info`` keyword argument:

>>> current_app.logger.critical("My message", exc_info=1)

Warnings
--------
Warnings are useful to alert developers and system administrators about
possible problems, e.g. usage of obsolete modules, deprecated APIs etc.

By default warnings are only sent to the console when the Flask application
is in debug mode. This can however be changed via the configuration variables:
:data:`invenio_logging.config.LOGGING_CONSOLE_PYWARNINGS`,
:data:`invenio_logging.config.LOGGING_FS_PYWARNINGS` and
:data:`invenio_logging.config.LOGGING_SENTRY_PYWARNINGS`

>>> import warnings
>>> warnings.warn('This feature is deprecated.', PendingDeprecationWarning)

For more information about logging please see:

 * http://flask.pocoo.org/docs/0.11/quickstart/#logging
 * https://docs.python.org/3/library/logging.html
"""

from __future__ import absolute_import, print_function

from .version import __version__

__all__ = (
    '__version__',
)
