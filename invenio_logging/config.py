# SPDX-FileCopyrightText: 2017-2018 CERN.
# SPDX-License-Identifier: MIT


"""Configuration for Invenio-Logging.

Sentry can, in addition to the configuration variables listed, be further
configured with the folllowing configuration variables (see
`Sentry <https://docs.sentry.io/platforms/python/integrations/flask/#configure>`_
for further details):

- ``SENTRY_AUTO_LOG_STACKS``
- ``SENTRY_EXCLUDE_PATHS``
- ``SENTRY_INCLUDE_PATHS``
- ``SENTRY_MAX_LENGTH_LIST``
- ``SENTRY_MAX_LENGTH_STRING``
- ``SENTRY_NAME``
- ``SENTRY_RELEASE``
- ``SENTRY_SITE_NAME``
- ``SENTRY_TAGS``

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

LOGGING_CONSOLE_FORMAT = None
"""Optional console log format. None preserves Flask's default formatter."""

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

LOGGING_FS_FORMAT = (
    "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
)
"""Filesystem log format."""

LOGGING_FS_LEVEL = None
"""Filesystem logging level.

Set to a valid Python logging level: ``CRITICAL``, ``ERROR``, ``WARNING``,
``INFO``, ``DEBUG``, or ``NOTSET``.
"""


# -------------
# OPENTELEMETRY
# -------------
LOGGING_OTEL_ENABLED = False
"""Enable programmatic Flask tracing. Requires the opentelemetry extra."""

LOGGING_OTEL_SERVICE_NAME = None
"""Service name. None uses the standard OTEL resource environment settings."""

LOGGING_OTEL_TRACES_EXPORTER = None
"""Console trace output or none. None reads OTEL_TRACES_EXPORTER (default console).

No network exporter, metrics pipeline or collector is configured.
"""

LOGGING_OTEL_EXCLUDED_URLS = None
"""Comma-separated URL regexes. None reads the standard OTEL exclusion variables."""

LOGGING_OTEL_LOG_CORRELATION = True
"""Add trace context to console/file log records when LOGGING_OTEL_ENABLED is true.

No log export pipeline is installed. Existing handlers and collectors remain in use.
"""

# ------
# SENTRY
# ------

LOGGING_SENTRY_LEVEL = "WARNING"
"""Sentry logging level.

Defaults to only reporting errors and warnings.
"""

LOGGING_SENTRY_PYWARNINGS = False
"""Enable logging of Python warnings to Sentry."""

LOGGING_SENTRY_CELERY = False
"""Configure Celery to send logging to Sentry."""

LOGGING_SENTRY_SQLALCHEMY = False
"""Configure SQL Alchemy to send logging to Sentry."""

LOGGING_SENTRY_REDIS = False
"""Configure REDIS to send logging to Sentry."""

LOGGING_SENTRY_CLASS = None
"""Import path of sentry Flask extension class.

This allows you to customize the Sentry extension class."""

LOGGING_SENTRY_INIT_KWARGS = None
"""Pass extra options when initializing Sentry instance."""

SENTRY_DSN = None
"""Set SENTRY_DSN environment variable."""
