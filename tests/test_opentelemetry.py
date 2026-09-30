# SPDX-FileCopyrightText: 2026 KTH Royal Institute of Technology.
# SPDX-License-Identifier: MIT

"""Tests for optional console traces and application log correlation."""

import io
import logging
from importlib.metadata import entry_points

import pytest
from flask import Flask, g
from flask.logging import default_handler
from opentelemetry import metrics, trace
from opentelemetry.metrics import NoOpMeterProvider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.sampling import Decision, TraceIdRatioBased

from invenio_logging import console as console_module
from invenio_logging import opentelemetry as otel
from invenio_logging.console import InvenioLoggingConsole
from invenio_logging.fs import InvenioLoggingFS
from invenio_logging.utils import AddTraceContextFilter


@pytest.fixture(autouse=True)
def logging_state(monkeypatch):
    """Isolate shared console state and restore handlers after each test."""
    monkeypatch.setattr(console_module, "_console_settings", None)
    filters, formatter, level = (
        list(default_handler.filters),
        default_handler.formatter,
        default_handler.level,
    )
    logger = logging.getLogger("otel-test")
    handlers, logger_level = list(logger.handlers), logger.level
    yield
    logger.handlers = handlers
    logger.setLevel(logger_level)
    default_handler.filters = filters
    default_handler.setFormatter(formatter)
    default_handler.setLevel(level)


@pytest.fixture()
def spans(monkeypatch):
    """Provide deterministic in-memory tracing without global SDK registration."""
    exporter = InMemorySpanExporter()
    provider = TracerProvider(shutdown_on_exit=False)
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    monkeypatch.setattr(otel, "_provider", provider)
    monkeypatch.setattr(otel, "_provider_settings", ("console", None))
    monkeypatch.delenv("OTEL_SDK_DISABLED", raising=False)
    yield exporter
    provider.shutdown()


def make_app(enabled=True):
    """Build a small Flask application without backing Invenio services."""
    app = Flask("otel-test")
    app.config.update(
        LOGGING_OTEL_ENABLED=enabled,
        LOGGING_OTEL_TRACES_EXPORTER="console",
        LOGGING_OTEL_EXCLUDED_URLS=r"/static/.*,/health(?:/|$|\?)",
    )

    @app.route("/records")
    def records():
        g.request_id = "request-test"
        app.logger.warning("record request")
        return "served"

    @app.route("/health")
    def health():
        return "ok"

    @app.route("/failure")
    def failure():
        raise ValueError("test failure")

    return app


def test_disabled_without_extra(monkeypatch):
    """Disabled installations require no optional SDK dependencies."""
    monkeypatch.setattr(otel, "trace", None)
    app = make_app(False)
    otel.InvenioLoggingOpenTelemetry(app)
    assert "invenio-logging-opentelemetry" not in app.extensions
    assert app.config["LOGGING_OTEL_SERVICE_NAME"] is None
    assert app.test_client().get("/records").status_code == 200


def test_enabled_without_extra(monkeypatch):
    """Enabled but unavailable optional dependencies fail with clear guidance."""
    monkeypatch.setattr(otel, "trace", None)
    with pytest.raises(RuntimeError, match=r"invenio-logging\[opentelemetry\]"):
        otel.InvenioLoggingOpenTelemetry(make_app())


def test_sdk_disabled(spans, monkeypatch):
    """The SDK disable switch prevents instrumentation."""
    monkeypatch.setenv("OTEL_SDK_DISABLED", "true")
    app = make_app()
    otel.InvenioLoggingOpenTelemetry(app)
    assert "invenio-logging-opentelemetry" not in app.extensions


def test_server_span_and_propagation(spans):
    """Emit one server span per request and preserve incoming trace context."""
    app = make_app()
    ext = otel.InvenioLoggingOpenTelemetry(app)
    duplicate = otel.InvenioLoggingOpenTelemetry(app)
    assert duplicate.tracer_provider is ext.tracer_provider
    app.test_client().get(
        "/records",
        headers={
            "traceparent": "00-12345678901234567890123456789012-1234567890123456-01"
        },
    )
    assert len(spans.get_finished_spans()) == 1
    span = spans.get_finished_spans()[0]
    assert span.kind == trace.SpanKind.SERVER
    assert span.context.trace_id == int("12345678901234567890123456789012", 16)
    assert span.parent.span_id == int("1234567890123456", 16)
    assert span.attributes["http.route"] == "/records"
    assert span.attributes["http.status_code"] == 200


def test_exclusions(spans):
    """Excluded static and health requests produce no spans."""
    app = make_app()
    otel.InvenioLoggingOpenTelemetry(app)
    app.test_client().get("/health?check=1")
    app.test_client().get("/static/missing.css")
    assert not spans.get_finished_spans()


def test_environment_exclusions(spans, monkeypatch):
    """Read the standard exclusion setting at application initialization."""
    monkeypatch.setenv("OTEL_PYTHON_FLASK_EXCLUDED_URLS", "/records")
    app = make_app()
    app.config["LOGGING_OTEL_EXCLUDED_URLS"] = None
    otel.InvenioLoggingOpenTelemetry(app)
    app.test_client().get("/records")
    assert not spans.get_finished_spans()


def test_shared_provider(spans):
    """UI and API instances share a provider without shutting it down on teardown."""
    ui, api = make_app(), make_app()
    first = otel.InvenioLoggingOpenTelemetry(ui)
    second = otel.InvenioLoggingOpenTelemetry(api)
    assert first.tracer_provider is second.tracer_provider
    ui.test_client().get("/records")
    api.test_client().get("/records")
    assert len(spans.get_finished_spans()) == 2


def test_errors(spans):
    """Flask failures create error spans with exception events."""
    app = make_app()
    otel.InvenioLoggingOpenTelemetry(app)
    assert app.test_client().get("/failure").status_code == 500
    span = spans.get_finished_spans()[0]
    assert span.status.status_code == trace.StatusCode.ERROR
    assert any(event.name == "exception" for event in span.events)


def test_console_correlation(spans):
    """Preserve existing handlers and enrich their records without factory changes."""
    factory = logging.getLogRecordFactory()
    app = make_app()
    app.config.update(
        LOGGING_CONSOLE_LEVEL="WARNING",
        LOGGING_CONSOLE_FORMAT="%(request_id)s %(trace_id)s %(span_id)s %(trace_sampled)s %(message)s",
    )
    # Root capture in pytest suppresses Flask's automatic default handler.
    app.logger.addHandler(default_handler)
    console = InvenioLoggingConsole(app)
    console.install_handler(app)
    otel.InvenioLoggingOpenTelemetry(app)
    assert app.logger.handlers.count(default_handler) == 1
    assert (
        len(
            [f for f in default_handler.filters if isinstance(f, AddTraceContextFilter)]
        )
        == 1
    )
    assert logging.getLogRecordFactory() is factory
    output = io.StringIO()
    with app.test_request_context(environ_overrides={"wsgi.errors": output}):
        app.logger.warning("outside span")
    assert "- - - False outside span" in output.getvalue()
    output = io.StringIO()
    app.test_client().get("/records", environ_overrides={"wsgi.errors": output})
    span = spans.get_finished_spans()[0]
    assert "request-test" in output.getvalue()
    assert format(span.context.trace_id, "032x") in output.getvalue()
    assert format(span.context.span_id, "016x") in output.getvalue()


def test_file_correlation(spans, tmp_path):
    """Existing rotating-file logs expose the same trace context."""
    app = make_app()
    logfile = tmp_path / "app.log"
    app.config.update(
        LOGGING_FS_LOGFILE=str(logfile),
        LOGGING_FS_FORMAT="%(trace_id)s %(span_id)s %(message)s",
    )
    InvenioLoggingFS(app)
    otel.InvenioLoggingOpenTelemetry(app)
    app.test_client().get("/records")
    span = spans.get_finished_spans()[0]
    for handler in app.logger.handlers[:]:
        if getattr(handler, "baseFilename", None) == str(logfile):
            handler.close()
            app.logger.removeHandler(handler)
    assert format(span.context.trace_id, "032x") in logfile.read_text()
    assert format(span.context.span_id, "016x") in logfile.read_text()


def test_correlation_can_be_disabled(spans):
    """Correlation is optional independently of console span output."""
    app = make_app()
    app.config["LOGGING_OTEL_LOG_CORRELATION"] = False
    handler = logging.StreamHandler()
    InvenioLoggingConsole.configure_handler(app, handler)
    assert not handler.filters


def test_filter_outside_flask_context():
    """Background records receive safe formatter defaults."""
    record = logging.makeLogRecord({"msg": "background"})
    assert AddTraceContextFilter().filter(record)
    assert (record.trace_id, record.span_id, record.request_id) == ("-", "-", "-")
    assert record.trace_sampled is False


def test_header_sanitization(spans, monkeypatch):
    """Opt-in header capture honours native sanitization settings."""
    monkeypatch.setenv(
        "OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST",
        "authorization,cookie,user-agent",
    )
    monkeypatch.setenv(
        "OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_RESPONSE", "set-cookie"
    )
    monkeypatch.setenv(
        "OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SANITIZE_FIELDS",
        "authorization,cookie,set-cookie",
    )
    app = make_app()

    @app.after_request
    def add_cookie(response):
        response.set_cookie("session", "secret")
        return response

    otel.InvenioLoggingOpenTelemetry(app)
    client = app.test_client()
    client.set_cookie("session", "secret")
    client.get(
        "/records", headers={"Authorization": "Bearer secret", "User-Agent": "test"}
    )
    attrs = spans.get_finished_spans()[0].attributes
    assert attrs["http.request.header.authorization"] == ("[REDACTED]",)
    assert attrs["http.request.header.cookie"] == ("[REDACTED]",)
    assert attrs["http.response.header.set_cookie"] == ("[REDACTED]",)
    assert attrs["http.request.header.user_agent"] == ("test",)


def test_metrics_explicitly_disabled(spans, monkeypatch):
    """Flask receives a no-op meter even if legacy metric settings remain."""
    monkeypatch.setenv("OTEL_METRICS_EXPORTER", "otlp")
    original_provider = metrics.get_meter_provider()
    instrument = otel.FlaskInstrumentor.instrument_app
    captured = []

    def instrument_app(app, **kwargs):
        captured.append(kwargs["meter_provider"])
        return instrument(app, **kwargs)

    monkeypatch.setattr(
        otel.FlaskInstrumentor, "instrument_app", staticmethod(instrument_app)
    )
    app = make_app()
    otel.InvenioLoggingOpenTelemetry(app)
    app.test_client().get("/records")
    assert isinstance(captured[0], NoOpMeterProvider)
    assert metrics.get_meter_provider() is original_provider
    assert not hasattr(
        app.extensions["invenio-logging-opentelemetry"], "meter_provider"
    )


@pytest.fixture()
def pipeline(monkeypatch):
    """Isolate SDK registration through its public API."""
    monkeypatch.setattr(otel, "_provider", None)
    monkeypatch.setattr(otel, "_provider_settings", None)
    monkeypatch.setattr(
        trace, "get_tracer_provider", lambda: trace.ProxyTracerProvider()
    )
    installed = []
    monkeypatch.setattr(trace, "set_tracer_provider", installed.append)
    monkeypatch.setenv("OTEL_TRACES_SAMPLER", "always_on")
    for name in (
        "OTEL_SERVICE_NAME",
        "OTEL_RESOURCE_ATTRIBUTES",
        "OTEL_TRACES_SAMPLER_ARG",
        "OTEL_TRACES_EXPORTER",
    ):
        monkeypatch.delenv(name, raising=False)
    yield installed
    if otel._provider is not None:
        otel._provider.shutdown()


def test_safe_sampling_default(pipeline, monkeypatch):
    """Default to one percent without inheriting the incoming sampled flag."""
    monkeypatch.delenv("OTEL_TRACES_SAMPLER")
    ext = otel.InvenioLoggingOpenTelemetry(make_app())
    sampler = ext.tracer_provider.sampler
    assert isinstance(sampler, TraceIdRatioBased)
    assert sampler.rate == 0.01
    parent = trace.NonRecordingSpan(
        trace.SpanContext(
            trace_id=1,
            span_id=1,
            is_remote=True,
            trace_flags=trace.TraceFlags(trace.TraceFlags.SAMPLED),
        )
    )
    assert (
        sampler.should_sample(
            trace.set_span_in_context(parent), (1 << 128) - 1, "test"
        ).decision
        == Decision.DROP
    )


def test_sampler_override(pipeline, monkeypatch):
    """Explicit SDK sampler settings override the conservative default."""
    monkeypatch.setenv("OTEL_TRACES_SAMPLER", "traceidratio")
    monkeypatch.setenv("OTEL_TRACES_SAMPLER_ARG", "0.2")
    ext = otel.InvenioLoggingOpenTelemetry(make_app())
    assert ext.tracer_provider.sampler.rate == 0.2


def test_console_pipeline(pipeline, monkeypatch):
    """Default to a bounded console batch pipeline with no external service."""
    exporter = InMemorySpanExporter()
    monkeypatch.setattr(otel, "ConsoleSpanExporter", lambda: exporter)
    app = make_app()
    app.config.update(
        LOGGING_OTEL_TRACES_EXPORTER=None, LOGGING_OTEL_SERVICE_NAME="invenio-test"
    )
    ext = otel.InvenioLoggingOpenTelemetry(app)
    assert pipeline == [ext.tracer_provider]
    assert ext.tracer_provider.resource.attributes["service.name"] == "invenio-test"
    app.test_client().get("/records")
    assert ext.tracer_provider.force_flush()
    assert len(exporter.get_finished_spans()) == 1


def test_none_exporter(pipeline, monkeypatch):
    """Correlation-only mode creates no console export processor."""

    def unexpected_exporter():
        raise AssertionError("Console exporter must not be created")

    monkeypatch.setattr(otel, "ConsoleSpanExporter", unexpected_exporter)
    app = make_app()
    app.config["LOGGING_OTEL_TRACES_EXPORTER"] = "none"
    ext = otel.InvenioLoggingOpenTelemetry(app)
    assert pipeline == [ext.tracer_provider]
    assert app.test_client().get("/records").status_code == 200


@pytest.mark.parametrize("value", ["otlp", "grpc", "", "none,console"])
def test_invalid_exporter(pipeline, value):
    """Only console and none are supported by this minimal feature."""
    app = make_app()
    app.config["LOGGING_OTEL_TRACES_EXPORTER"] = value
    with pytest.raises(ValueError, match="console or none"):
        otel.InvenioLoggingOpenTelemetry(app)
    assert not pipeline


def test_process_configuration_conflict(spans):
    """Do not silently reuse another app's incompatible exporter settings."""
    app = make_app()
    app.config["LOGGING_OTEL_TRACES_EXPORTER"] = "none"
    with pytest.raises(ValueError, match="must agree"):
        otel.InvenioLoggingOpenTelemetry(app)


def test_external_provider_rejected(pipeline, monkeypatch):
    """Avoid competing agent and programmatic SDK initializers."""
    monkeypatch.setattr(trace, "get_tracer_provider", lambda: object())
    with pytest.raises(RuntimeError, match="already installed"):
        otel.InvenioLoggingOpenTelemetry(make_app())


def test_deployment_instance_id_preserved(pipeline, monkeypatch):
    """Deployment resource IDs are not replaced by generated IDs."""
    monkeypatch.setenv(
        "OTEL_RESOURCE_ATTRIBUTES", "service.instance.id=deployment-worker-42"
    )

    def unexpected_uuid():
        raise AssertionError("Explicit resource ID must be preserved")

    monkeypatch.setattr(otel, "uuid4", unexpected_uuid)
    ext = otel.InvenioLoggingOpenTelemetry(make_app())
    assert (
        ext.tracer_provider.resource.attributes["service.instance.id"]
        == "deployment-worker-42"
    )


def test_missing_instance_id_generated(pipeline, monkeypatch):
    """Supply one fallback ID when older SDK resource detectors omit it."""
    monkeypatch.setattr(
        otel.Resource, "create", lambda attributes: otel.Resource(attributes)
    )
    generated = []

    def uuid():
        generated.append("generated-worker")
        return generated[-1]

    monkeypatch.setattr(otel, "uuid4", uuid)
    ext = otel.InvenioLoggingOpenTelemetry(make_app())
    second = otel.InvenioLoggingOpenTelemetry(make_app())
    assert generated == ["generated-worker"]
    assert (
        ext.tracer_provider.resource.attributes["service.instance.id"]
        == "generated-worker"
    )
    assert second.tracer_provider is ext.tracer_provider


def test_detected_instance_id_preserved(pipeline, monkeypatch):
    """Retain detector IDs as well as explicitly deployed IDs."""
    monkeypatch.setattr(
        otel.Resource,
        "create",
        lambda attributes: otel.Resource(
            {**attributes, "service.instance.id": "detected-worker"}
        ),
    )
    ext = otel.InvenioLoggingOpenTelemetry(make_app())
    assert (
        ext.tracer_provider.resource.attributes["service.instance.id"]
        == "detected-worker"
    )


def test_entry_points():
    """Register the package in both standard Invenio extension groups."""
    for group in ("invenio_base.apps", "invenio_base.api_apps"):
        entries = list(entry_points(group=group, name="invenio_logging_opentelemetry"))
        assert len(entries) == 1
        assert entries[0].load() is otel.InvenioLoggingOpenTelemetry
