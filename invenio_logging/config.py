# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Configuration for Invenio-Logging.

Sentry can, in addition to the configuration variables listed, be further
configured with the folllowing configuration variables (see
`Raven <https://docs.sentry.io/clients/python/integrations/flask/#settings>`_
for further details):

- ``SENTRY_AUTO_LOG_STACKS``
- ``SENTRY_EXCLUDE_PATHS``
- ``SENTRY_INCLUDE_PATHS``
- ``SENTRY_MAX_LENGTH_LIST``
- ``SENTRY_MAX_LENGTH_STRING``
- ``SENTRY_NAME``
- ``SENTRY_PROCESSORS``
- ``SENTRY_RELEASE``
- ``SENTRY_SITE_NAME``
- ``SENTRY_TAGS``
- ``SENTRY_TRANSPORT``


.. note::

   Celery does not deal well with the threaded Sentry transport, so you should
   make sure that your **Celery workers** are configured with:

   .. code-block:: python

      SENTRY_TRANSPORT = 'raven.transport.http.HTTPTransport'
"""

# -------
# CONSOLE
# -------
LOGGING_CONSOLE = True
"""Enable logging to the console."""

LOGGING_CONSOLE_PYWARNINGS = None
"""Enable logging of Python warnings to the console.

By default, warnings are logged to the console if the application is in debug
mode, otherwise warnings are not logged.
"""

LOGGING_CONSOLE_LEVEL = None
"""Console logging level.

Set to a valid Python logging level: ``CRITICAL``, ``ERROR``, ``WARNING``,
``INFO``, ``DEBUG``, or ``NOTSET``.
"""


# ----------
# FILESYSTEM
# ----------
LOGGING_FS_LOGFILE = None
"""Enable logging to the filesystem."""

LOGGING_FS_PYWARNINGS = False
"""Enable logging of Python warnings to filesystem logging."""

LOGGING_FS_BACKUPCOUNT = 5
"""Number of rotated log files to keep."""

LOGGING_FS_MAXBYTES = 100 * 1024 * 1024
"""Maximum size of logging file. Default: 100MB."""

LOGGING_FS_LEVEL = None
"""Filesystem logging level.

Set to a valid Python logging level: ``CRITICAL``, ``ERROR``, ``WARNING``,
``INFO``, ``DEBUG``, or ``NOTSET``.
"""


# ------
# SENTRY
# ------
LOGGING_SENTRY_LEVEL = 'WARNING'
"""Sentry logging level.

Defaults to only reporting errors and warnings.
"""

LOGGING_SENTRY_PYWARNINGS = False
"""Enable logging of Python warnings to Sentry."""

LOGGING_SENTRY_CELERY = False
"""Configure Celery to send logging to Sentry."""

LOGGING_SENTRY_CLASS = None
"""Import path of sentry Flask extension class.

This allows you to customize the Sentry extension class. In particular if you
are logging to Sentry v6, you can set this to
:class:`invenio_logging.sentry6.Sentry6`."""

SENTRY_DSN = None
"""Set SENTRY_DSN environment variable."""

SENTRY_PROCESSORS = (
    'raven.processors.SanitizePasswordsProcessor',
    'invenio_logging.sentry.RequestIdProcessor',
)
"""Default Sentry event processors."""

SENTRY_TRANSPORT = 'raven.transport.threaded.ThreadedHTTPTransport'
"""Default Sentry transport."""
