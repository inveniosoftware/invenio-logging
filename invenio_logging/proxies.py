# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
#
# Invenio-Notifications is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Proxies for accessing the currently instantiated datastream log extension."""

from flask import current_app
from werkzeug.local import LocalProxy

current_logging = LocalProxy(
    lambda: current_app.extensions["invenio-logging-engine"]
)
"""Proxy for the instantiated logging extension."""

current_logging_manager = LocalProxy(lambda: current_logging.manager)
"""Proxy for the instantiated logging manager."""
