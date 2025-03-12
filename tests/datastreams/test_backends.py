# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


import pytest
from invenio_search import current_search, current_search_client

from invenio_logging.datastreams.backends import SearchBackend
from invenio_logging.engine.builders import LogBuilder


def test_ensure_template_exists_missing(app):
    with pytest.raises(RuntimeError):
        backend = SearchBackend("test")


def test_init(app):
    log_type = "test"
    # Manually create the registered index templates (we need to consume the generator)
    list(current_search.put_component_templates())
    list(current_search.put_index_templates())

    backend = SearchBackend(log_type)
    assert backend.log_type == log_type
    assert backend.index_name == f"logs-{log_type}"
    assert backend.template_name == "datastream-log-v1.0.0"

    assert current_search_client.indices.exists_index_template(
        name="datastream-log-v1.0.0"
    )


def test_send_and_search(app, valid_log_event):
    backend = SearchBackend("test")
    validated_event = LogBuilder.validate(valid_log_event)
    backend.send(validated_event)
    current_search_client.indices.refresh(index=backend.index_name)
    response = backend.search(query="test")
    assert len(response) == 1
    assert response[0]["message"] == valid_log_event["message"]


def test_send_failure(app, invalid_log_event):
    backend = SearchBackend("test")
    with pytest.raises(Exception):
        backend.send(invalid_log_event)
