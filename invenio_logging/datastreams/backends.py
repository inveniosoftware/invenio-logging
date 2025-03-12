# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for datastream backends."""


from abc import ABC, abstractmethod

from flask import current_app
from invenio_search import current_search_client


class LogBackend(ABC):
    """Abstract base class for log backends."""

    @abstractmethod
    def send(self, log_type, log_event):
        """Send a log event to the backend."""
        raise NotImplementedError()


class SearchBackend(LogBackend):
    """Generic backend for storing logs in datastreams index."""

    def __init__(self, log_type):
        """
        Initialize SearchBackend.

        :param log_type: Type of log (e.g., "audit", "task", "system").
        """
        self.client = current_search_client
        self.log_type = log_type
        self.template_name = "datastream-log-v1.0.0"
        self.index_name = f"logs-{log_type}"
        self.search_fields = [
            "message",
            "event.action",
            "user.id",
            "user.email",
            "resource.id",
            "resource.parent.id",
        ]

        self._ensure_template_exists()

    def _ensure_template_exists(self):
        """Check if required template exists, enforce if missing."""
        index_prefix = current_app.config.get("SEARCH_INDEX_PREFIX", "")
        full_template_name = f"{index_prefix}{self.template_name}"
        if not self.client.indices.exists_index_template(name=full_template_name):
            raise RuntimeError(
                f"Required template '{self.template_name}' is missing. "
                "Ensure it is created before logging events."
            )

    def send(self, log_event):
        """Send the log event to Search engine."""
        try:
            index_prefix = current_app.config.get("SEARCH_INDEX_PREFIX", "")
            full_index_name = f"{index_prefix}{self.index_name}"
            self.client.index(index=full_index_name, body=log_event)

        except Exception as e:
            current_app.logger.error(f"Failed to send log Search engine: {e}")
            raise e

    def search(self, query=None, size=10):
        """
        Search log events.

        :param size: Number of results to return.
        :return: List of log events that match the search query.
        """
        try:
            index_prefix = current_app.config.get("SEARCH_INDEX_PREFIX", "")
            full_index_name = f"{index_prefix}{self.index_name}"

            search_query = {
                "size": size,
                "query": (
                    {"match_all": {}} if not query else {
                        "multi_match": {
                            "query": query,
                            "fields": self.search_fields,
                            "operator": "and"
                        }
                    }
                ),
                "sort": [{"@timestamp": {"order": "desc"}}],
            }
            # TODO: add pagination?
            response = self.client.search(index=full_index_name, body=search_query)
            return [hit["_source"] for hit in response.get("hits", {}).get("hits", [])]

        except Exception as e:
            current_app.logger.error(f"Failed to search logs: {e}")
            raise e

    def list(self, size=10):
        """
        List log events.

        :param size: Number of results to return.
        :return: List of log events.
        """
        try:
            index_prefix = current_app.config.get("SEARCH_INDEX_PREFIX", "")
            full_index_name = f"{index_prefix}{self.index_name}"

            response = self.client.search(
                index=full_index_name,
                body={"size": size, "sort": [{"@timestamp": {"order": "desc"}}]},
            )
            return [hit["_source"] for hit in response.get("hits", {}).get("hits", [])]

        except Exception as e:
            current_app.logger.error(f"Failed to search logs: {e}")
            raise e
