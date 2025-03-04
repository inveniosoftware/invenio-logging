# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Decorators for datastream logging."""

from invenio_logging.datastreams.log_event import LogEvent
from invenio_logging.proxies import current_datastream_logging_manager


def log_task():
    """Decorate log task events.

    Useful for celery tasks that need to log events by passing down the log type and log data.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            log_type = kwargs.get(
                "log_type", "TODO"
            )  # Should we have a default log type?
            log_data = kwargs.get("log_data", {})

            def _log_event(
                message=None, event=None, user=None, resource=None, extra=None
            ):
                """Log event."""
                log_data["message"] = message if message else log_data.get("message")
                log_data["event"] = event if event else log_data.get("event")
                log_data["user"] = user if user else log_data.get("user")
                log_data["resource"] = (
                    resource if resource else log_data.get("resource")
                )
                log_data["extra"] = extra if extra else log_data.get("extra")
                log_event = LogEvent(**log_data)
                current_datastream_logging_manager.log(log_type, log_event)

            kwargs["_log_event"] = _log_event
            return func(*args, **kwargs)

        return wrapper

    return decorator
