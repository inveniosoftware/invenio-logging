# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio-Requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Custom exceptions used in the Invenio-Logging module."""


class InvalidLogQueryError(Exception):
    """Error raised when an invalid query is made on logging resources."""

    def __init__(self, message="Invalid log query parameters provided."):
        """Initialize error with a default message."""
        self.message = message
        super().__init__(self.message)
