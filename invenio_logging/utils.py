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


class AddTraceContextFilter(logging.Filter):
    """Enrich handler records with the active OpenTelemetry trace context."""

    def filter(self, record):
        """Add safe defaults outside spans without changing messages or levels."""
        # Optional dependency: imported only when correlation is explicitly enabled.
        from opentelemetry import trace

        context = trace.get_current_span().get_span_context()
        record.trace_id = format(context.trace_id, "032x") if context.is_valid else "-"
        record.span_id = format(context.span_id, "016x") if context.is_valid else "-"
        record.trace_sampled = bool(context.is_valid and context.trace_flags.sampled)
        if not hasattr(record, "request_id"):
            record.request_id = getattr(g, "request_id", "-") if g else "-"
        return True


add_request_id_filter = AddRequestIdFilter()
add_trace_context_filter = AddTraceContextFilter()
