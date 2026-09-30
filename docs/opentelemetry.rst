..
    SPDX-FileCopyrightText: 2026 KTH Royal Institute of Technology.
    SPDX-License-Identifier: MIT

OpenTelemetry console tracing
=============================

Install ``invenio-logging[opentelemetry]`` and set ``LOGGING_OTEL_ENABLED=True``.
The extension is registered in both standard Invenio UI/API extension groups.
Disabled installations require no optional SDK. No metrics, network exporter,
collector or Sentry dependency is configured.

``LOGGING_OTEL_TRACES_EXPORTER`` reads ``OTEL_TRACES_EXPORTER`` when unset:
``console`` (default) prints batched spans; ``none`` disables span output but
retains instrumentation for log correlation. Sampling defaults to 1% trace-ID
ratio. Explicit ``OTEL_TRACES_SAMPLER`` and ``OTEL_TRACES_SAMPLER_ARG`` use SDK
behavior. Full sampling is for short local debugging, not high-traffic defaults.

Existing console/file handlers enrich records with trace/span IDs when
``LOGGING_OTEL_LOG_CORRELATION`` is enabled. They retain ownership of application
logs. Configure ``LOGGING_CONSOLE_FORMAT`` or ``LOGGING_FS_FORMAT`` to display
``trace_id``, ``span_id``, ``trace_sampled`` and ``request_id``. Shared console
formatting/effective-correlation settings must agree across apps in a process;
conflicts fail before handler mutation. Outside valid spans, IDs are ``-``.

``LOGGING_OTEL_SERVICE_NAME`` overrides service identity; otherwise the SDK reads
standard resource variables. Explicit deployment/detector instance IDs are
preserved. ``LOGGING_OTEL_EXCLUDED_URLS`` overrides the standard Flask/global URL
exclusion variables. Header capture is off by default; enable only a minimal
allowlist and configure the standard sanitization fields. URLs and log messages
are not sanitized automatically.

Each app is instrumented once; providers and bounded batch queues are shared per
process and drained at normal exit, not request teardown. Initialize after fork,
enable threads and disable the debug reloader for verification. Do not combine
with another SDK/auto-instrumentation initializer. Restart after configuration
changes. Normal application/audit logging remains independent of this extension.
