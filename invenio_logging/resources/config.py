from marshmallow import fields

from invenio_records_resources.resources import SearchRequestArgsSchema, RecordResourceConfig
from invenio_records_resources.services.base.config import ConfiguratorMixin

from flask_resources import HTTPJSONException, create_error_handler
from ..errors import InvalidLogQueryError

#
# Request args
#
class LogSearchRequestArgsSchema(SearchRequestArgsSchema):
    """Search parameters for logs."""

    resource_id = fields.String()
    resource_type = fields.String()
    user_id = fields.String()
    action = fields.String()

error_handlers = {
    InvalidLogQueryError: create_error_handler(
        lambda e: HTTPJSONException(code=400, description=str(e))
    ),
}

#
# Resource config
#
class LogsResourceConfig(RecordResourceConfig, ConfiguratorMixin):
    """Logs resource configuration."""

    blueprint_name = "logs"
    url_prefix = "/logs"

    routes = {
        "list": "/",
        "item": "/<id>",
    }

    request_view_args = {
        "resource_id": fields.String(),
        # "resource_type": fields.String(), # TODO: Add direct querying via other search parameters?
        # "user_id": fields.String(),
        # "action": fields.String(),
    }

    request_search_args = LogSearchRequestArgsSchema

    error_handlers = error_handlers

    response_handlers = {
        "application/vnd.inveniordm.v1+json": RecordResourceConfig.response_handlers[
            "application/json"
        ],
        **RecordResourceConfig.response_handlers,
    }
