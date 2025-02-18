# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for datastream logging management."""

from invenio_logging.datastreams.backends import SearchBackend


class SearchAuditLogBackend(SearchBackend):
    """Backend for storing audit logs in datastreams."""

    def __init__(self):
        """Initialize backend for audit logs."""
        super().__init__(log_type="audit")
