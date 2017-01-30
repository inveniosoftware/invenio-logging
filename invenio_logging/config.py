# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
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


"""Configuration for Invenio-Logging."""

# -------
# CONSOLE
# -------
LOGGING_CONSOLE = True
"""Enable logging to a console."""

LOGGING_CONSOLE_PYWARNINGS = None
"""Enable logging of Python warnings.

By default, warnings are logged if the application is in debug mode, otherwise
warnings are not logged."""

LOGGING_CONSOLE_LEVEL = None
"""Define valid Python logging level from ``CRITICAL``, ``ERROR``, ``WARNING``,
``INFO``, ``DEBUG``, or ``NOTSET``."""


# ----------
# FILESYSTEM
# ----------
LOGGING_FS_LOGFILE = None
"""Enable logging to a console."""

LOGGING_FS_PYWARNINGS = False
"""Enable Python warnings."""

LOGGING_FS_BACKUPCOUNT = 5
"""Define number of backup files."""

LOGGING_FS_MAXBYTES = 100 * 1024 * 1024
"""Define maximal file size.
By default: 100MB."""

LOGGING_FS_LEVEL = None
"""Define valid Python logging level from ``CRITICAL``, ``ERROR``, ``WARNING``,
``INFO``, ``DEBUG``, or ``NOTSET``.

By default, warnings are logged if , otherwise
warnings are not logged.
If the application is in debug mode, Python logging level will be set
to ``DEBUG``, otherwise it is set to ``WARNING``."""


# ------
# SENTRY
# ------
SENTRY_DSN = None
"""Set SENTRY_DSN environment variable."""

LOGGING_SENTRY_LEVEL = 'WARNING'
"""Default to only reporting errors and warnings."""

LOGGING_SENTRY_PYWARNINGS = False
"""Send python warnings to Sentry?"""

LOGGING_SENTRY_CELERY = False
"""Configure Celery?"""

LOGGING_SENTRY_CLASS = None
"""Sentry Flask extension class - only needed in case you need to overwrite
something really deep down."""

SENTRY_TRANSPORT = 'raven.transport.threaded.ThreadedHTTPTransport'
"""Sentry transport."""
