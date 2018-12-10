# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio filesystem logging module.

This extension is automatically installed via ``invenio_base.apps`` and
``invenio_base.api_apps`` entry points.
"""

from __future__ import absolute_import, print_function

import logging
import sys
from logging.handlers import RotatingFileHandler
from os.path import dirname, exists

from . import config
from .ext import InvenioLoggingBase
from .utils import add_request_id_filter


class InvenioLoggingFS(InvenioLoggingBase):
    """Invenio-Logging extension. Filesystem handler."""

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        if app.config['LOGGING_FS_LOGFILE'] is None:
            return
        self.install_handler(app)
        app.extensions['invenio-logging-fs'] = self

    def init_config(self, app):
        """Initialize config."""
        app.config.setdefault(
            'LOGGING_FS_LEVEL',
            'DEBUG' if app.debug else 'WARNING'
        )
        for k in dir(config):
            if k.startswith('LOGGING_FS'):
                app.config.setdefault(k, getattr(config, k))

        # Support injecting instance path and/or sys.prefix
        if app.config['LOGGING_FS_LOGFILE'] is not None:
            app.config['LOGGING_FS_LOGFILE'] = \
                app.config['LOGGING_FS_LOGFILE'].format(
                    instance_path=app.instance_path,
                    sys_prefix=sys.prefix,
                )

    def install_handler(self, app):
        """Install log handler on Flask application."""
        # Check if directory exists.
        basedir = dirname(app.config['LOGGING_FS_LOGFILE'])
        if not exists(basedir):
            raise ValueError(
                'Log directory {0} does not exists.'.format(basedir))

        handler = RotatingFileHandler(
            app.config['LOGGING_FS_LOGFILE'],
            backupCount=app.config['LOGGING_FS_BACKUPCOUNT'],
            maxBytes=app.config['LOGGING_FS_MAXBYTES'],
            delay=True,
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        handler.setLevel(app.config['LOGGING_FS_LEVEL'])

        # Add handler to application logger
        app.logger.addHandler(handler)

        if app.config['LOGGING_FS_PYWARNINGS']:
            self.capture_pywarnings(handler)

        # Add request_id to log record
        app.logger.addFilter(add_request_id_filter)
