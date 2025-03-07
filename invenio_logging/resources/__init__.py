# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Resources module."""

from .config import LogsResourceConfig
from .resource import LogsResource

__all__ = (
    "LogsResource",
    "LogsResourceConfig",
)
