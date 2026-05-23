# SPDX-FileCopyrightText: 2015-2018 CERN.
# SPDX-License-Identifier: MIT

"""Logging utils."""

import logging

from flask import g


class AddRequestIdFilter(logging.Filter):
    """Filter for loggers."""

    def filter(self, record):
        """If request_id is set in flask.g, add it to log record."""
        if g and hasattr(g, "request_id"):
            record.request_id = g.request_id
        return True


add_request_id_filter = AddRequestIdFilter()
