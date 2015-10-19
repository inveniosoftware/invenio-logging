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

"""Invenio filesystem logging module."""

from __future__ import absolute_import, print_function

import logging
import os
from logging.handlers import RotatingFileHandler

from flask_babelex import gettext as _


class InvenioLoggingFs(object):

    """Invenio-Logging extension. Filesystem handler"""

    def __init__(self, app=None):
        """Extension initialization."""
        _('A translation string')
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""

        self.init_config(app)
        app.extensions['invenio-logging-fs'] = self

        if app.debug:
            logger = logging.getLogger('py.warnings')
            logger.addHandler(logging.StreamHandler())
            logger.setLevel(logging.WARNING)

        app.config.setdefault('LOGGING_FS_BACKUPCOUNT', 5)
        app.config.setdefault('LOGGING_FS_MAXBYTES', 104857600)  # 100mb
        app.config.setdefault(
            'LOGGING_FS_LEVEL',
            'DEBUG' if app.debug else 'WARNING'
        )

        # Create log directory if it does not exists
        try:
            os.makedirs(
                os.path.join(app.instance_path,
                             app.config.get('CFG_LOGDIR', ''))
            )
        except Exception:
            pass

        handler = RotatingFileHandler(
            os.path.join(
                app.instance_path,
                app.config.get('CFG_LOGDIR', ''),
                app.logger_name + '.log'
            ),
            backupCount=app.config['LOGGING_FS_BACKUPCOUNT'],
            maxBytes=app.config['LOGGING_FS_MAXBYTES']
        )

        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))

        handler.setLevel(app.config['LOGGING_FS_LEVEL'])

        # Add handler to application logger
        app.logger.addHandler(handler)

    def init_config(self, app):
        """Initialize configuration."""
