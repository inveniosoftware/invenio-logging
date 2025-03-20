# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio abstract logging backend."""

from abc import ABC, abstractmethod


class LogBackend(ABC):
    """Abstract base class for log backends."""

    @abstractmethod
    def store(self, log_type, log_event):
        """Store a log event in the backend."""
        raise NotImplementedError()

    @abstractmethod
    def search(self, query, size=10, page=1):
        """Search log events."""
        raise NotImplementedError()
