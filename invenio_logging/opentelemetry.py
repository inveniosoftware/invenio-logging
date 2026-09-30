# SPDX-FileCopyrightText: 2026 KTH Royal Institute of Technology.
# SPDX-License-Identifier: MIT

"""Optional Flask console tracing and application log correlation."""

import os
from threading import Lock
from uuid import uuid4

from . import config
from .ext import InvenioLoggingBase

try:
    from opentelemetry import trace
    from opentelemetry.instrumentation.flask import FlaskInstrumentor
    from opentelemetry.metrics import NoOpMeterProvider
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
except ImportError:
    trace = None

_provider = None
_provider_settings = None
_provider_lock = Lock()


def _get_provider(app):
    """Create one process-wide console pipeline shared by UI and REST apps."""
    global _provider, _provider_settings

    exporter = app.config["LOGGING_OTEL_TRACES_EXPORTER"]
    if exporter is None:
        exporter = os.environ.get("OTEL_TRACES_EXPORTER", "console")
    exporter = exporter.strip()
    if exporter not in {"console", "none"}:
        raise ValueError("LOGGING_OTEL_TRACES_EXPORTER supports console or none")
    service_name = app.config["LOGGING_OTEL_SERVICE_NAME"]
    settings = (exporter, service_name)

    with _provider_lock:
        if _provider is not None:
            if settings != _provider_settings:
                raise ValueError(
                    "OpenTelemetry settings must agree across apps in a process"
                )
            return _provider
        if not isinstance(trace.get_tracer_provider(), trace.ProxyTracerProvider):
            raise RuntimeError(
                "Another OpenTelemetry provider is already installed. "
                "Disable LOGGING_OTEL_ENABLED when using opentelemetry-instrument "
                "or a separately configured SDK."
            )

        resource = Resource.create(
            {"service.name": service_name} if service_name else {}
        )
        if "service.instance.id" not in resource.attributes:
            resource = resource.merge(Resource({"service.instance.id": str(uuid4())}))
        sampler = (
            None if os.environ.get("OTEL_TRACES_SAMPLER") else TraceIdRatioBased(0.01)
        )
        provider = TracerProvider(resource=resource, sampler=sampler)
        try:
            if exporter == "console":
                provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        except Exception:
            provider.shutdown()
            raise
        trace.set_tracer_provider(provider)
        _provider = provider
        _provider_settings = settings
        return provider


class InvenioLoggingOpenTelemetry(InvenioLoggingBase):
    """Invenio-Logging extension for optional console traces and log correlation."""

    def init_app(self, app):
        """Instrument Flask without a network exporter or metrics pipeline."""
        self.init_config(app)
        if not app.config["LOGGING_OTEL_ENABLED"]:
            return
        if os.environ.get("OTEL_SDK_DISABLED", "false").lower() == "true":
            return
        if "invenio-logging-opentelemetry" in app.extensions:
            self.tracer_provider = app.extensions[
                "invenio-logging-opentelemetry"
            ].tracer_provider
            return
        if trace is None:
            raise RuntimeError(
                "LOGGING_OTEL_ENABLED requires invenio-logging[opentelemetry]."
            )
        if getattr(app, "_is_instrumented_by_opentelemetry", False):
            raise RuntimeError("Flask app is already instrumented by OpenTelemetry")

        excluded_urls = app.config["LOGGING_OTEL_EXCLUDED_URLS"]
        if excluded_urls is None:
            excluded_urls = os.environ.get(
                "OTEL_PYTHON_FLASK_EXCLUDED_URLS",
                os.environ.get("OTEL_PYTHON_EXCLUDED_URLS", ""),
            )
        self.tracer_provider = _get_provider(app)
        FlaskInstrumentor().instrument_app(
            app,
            tracer_provider=self.tracer_provider,
            meter_provider=NoOpMeterProvider(),
            excluded_urls=excluded_urls,
        )
        # The shared provider drains its bounded batch queue at normal process exit,
        # not on request teardown. Existing console/file handlers still own logs.
        app.extensions["invenio-logging-opentelemetry"] = self

    def init_config(self, app):
        """Initialize defaults without overwriting instance configuration."""
        for name in dir(config):
            if name.startswith("LOGGING_OTEL"):
                app.config.setdefault(name, getattr(config, name))
