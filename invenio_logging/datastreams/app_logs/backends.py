# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Loggigng module for app."""

from invenio_logging.datastreams.backends import SearchBackend


class SearchAppLogBackend(SearchBackend):
    """Backend for storing app logs in datastreams."""

    def __init__(self):
        """Initialize backend for app logs."""
        super().__init__(log_type="app")
