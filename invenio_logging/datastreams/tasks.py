# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.

"""Datastream logging tasks."""

from celery import shared_task

from invenio_logging.datastreams.log_event import LogEvent
from invenio_logging.proxies import current_datastream_logging_manager


@shared_task(ignore_result=True)
def log_event_task(log_type, log_data):
    """Celery task to log an event asynchronously."""
    if log_type not in current_datastream_logging_manager.builders:
        raise ValueError(f"No log builder found for type '{log_type}'.")

    log_builder = current_datastream_logging_manager.builders[log_type]
    log = log_builder.build(log_data)
    log_builder.send(log)
