# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016, 2017 CERN.
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

"""Invenio filesystem logging module.

This extension is enabled by default and automatically installed via
``invenio_base.apps`` and ``invenio_base.api_apps`` entry points.
"""

from __future__ import absolute_import, print_function

import logging

from . import config
from .ext import InvenioLoggingBase


class InvenioLoggingConsole(InvenioLoggingBase):
    """Invenio-Logging extension for console."""

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)

        if not app.config['LOGGING_CONSOLE']:
            return

        self.install_handler(app)

        app.extensions['invenio-logging-console'] = self

    def init_config(self, app):
        """Initialize config."""
        app.config.setdefault('LOGGING_CONSOLE', True)
        app.config.setdefault('LOGGING_CONSOLE_PYWARNINGS', app.debug)
        for k in dir(config):
            if k.startswith('LOGGING_CONSOLE'):
                app.config.setdefault(k, getattr(config, k))

    def install_handler(self, app):
        """Install logging handler."""
        # Configure python logging
        if app.config['LOGGING_CONSOLE_PYWARNINGS']:
            self.capture_pywarnings(logging.StreamHandler())

        if app.config['LOGGING_CONSOLE_LEVEL'] is not None:
            for h in app.logger.handlers:
                h.setLevel(app.config['LOGGING_CONSOLE_LEVEL'])
