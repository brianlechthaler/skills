---
name: opentelemetry
description: >-
  Implement OpenTelemetry observability — traces, metrics, and logs with OTLP
  export, auto-instrumentation, resource attributes, and collector wiring. Use
  when adding telemetry, distributed tracing, metrics, structured logging,
  observability, OTLP, Jaeger, Prometheus, or Grafana to an application or stack.
---

# OpenTelemetry

Add **production-grade observability** to the project: distributed traces, metrics, and correlated logs using the [OpenTelemetry](https://opentelemetry.io/) (OTel) SDK and OTLP export. Instrument the app, wire export to a collector or backend, and verify signals arrive before marking work complete.

Pair with [compose-deploy](../compose-deploy/SKILL.md) to add an OTel Collector sidecar or local stack, and [docker](../docker/SKILL.md) to run the app and collector in containers.

## When This Applies

| Applies | Does not apply |
|---------|----------------|
| User asks for tracing, metrics, logging, or observability | Pure log parsing or grep-only debugging with no instrumentation |
| New service, API, worker, or CLI that needs production visibility | One-off local scripts with no deploy path |
| Existing app lacks trace/metric correlation across requests | Vendor-specific APM already fully configured and user only wants dashboard tweaks |
| Docker Compose or K8s stack needs a collector | Replacing an entire observability platform without touching app code |

When unsure and the project runs as a long-lived service, **default to adding OTel** with OTLP export and environment-based configuration.

## Core Rules

1. **Use OpenTelemetry SDKs and semantic conventions** — not ad-hoc trace IDs in headers or custom metric registries when an OTel SDK exists for the language.
2. **Export via OTLP** — gRPC (`4317`) or HTTP/protobuf (`4318`); configure endpoint with env vars, not hardcoded hosts.
3. **One `Resource` per process** — set `service.name`, `service.version`, and `deployment.environment` on every signal.
4. **Propagate context on every outbound call** — HTTP/gRPC/message clients must inject W3C `traceparent` (and baggage when used).
5. **Prefer auto-instrumentation first** — add manual spans only for business-critical operations auto-instrumentation misses.
6. **Do not log secrets or full PII** — redact tokens, passwords, and sensitive fields in log attributes.
7. **Graceful shutdown** — flush exporters on SIGTERM; do not drop spans on deploy.

## Workflow

Copy and track:

```
OpenTelemetry progress:
- [ ] Stack detected (language, framework, runtime)
- [ ] Existing telemetry reviewed (avoid duplicate agents)
- [ ] OTel SDK + auto-instrumentation added
- [ ] Resource attributes and env-based OTLP config set
- [ ] Traces verified (request → downstream calls linked)
- [ ] Metrics exported (HTTP latency, errors, custom counters/histograms)
- [ ] Logs correlated with trace_id/span_id when supported
- [ ] Collector or backend wired (compose, K8s, or managed endpoint)
- [ ] Sampling strategy documented (always_on dev, parentbased_traceidratio prod)
- [ ] README or docs updated with env vars and local verify steps
```

## Step 1 — Detect stack and existing telemetry

| Signal | Language / runtime | OTel packages |
|--------|-------------------|---------------|
| `package.json` + Express/Fastify/Nest | Node.js | `@opentelemetry/sdk-node`, `@opentelemetry/auto-instrumentations-node` |
| `package.json` + Next.js | Node.js | `@vercel/otel` or manual `NodeSDK` + `HttpInstrumentation` |
| `pyproject.toml` / `requirements*.txt` + FastAPI/Django/Flask | Python | `opentelemetry-distro`, `opentelemetry-exporter-otlp`, framework instrumentor |
| `go.mod` | Go | `go.opentelemetry.io/otel`, `otelhttp`, `otelgrpc` |
| `pom.xml` / `build.gradle` | Java | `opentelemetry-javaagent` JAR or SDK + Spring Boot starter |
| `Cargo.toml` | Rust | `opentelemetry`, `opentelemetry-otlp`, `tracing-opentelemetry` |

**Skip or replace** when the repo already ships a full OTel setup — extend it instead of adding a second exporter. Check for: `OTEL_*` env vars, `opentelemetry` in deps, `otel-collector`, Jaeger/Tempo/Prometheus/Grafana configs, Datadog/New Relic agents.

## Step 2 — Configure via environment

Standard variables (use these names; do not invent project-specific aliases):

| Variable | Typical value |
|----------|---------------|
| `OTEL_SERVICE_NAME` | App name (e.g. `checkout-api`) |
| `OTEL_RESOURCE_ATTRIBUTES` | `service.version=1.2.0,deployment.environment=production` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://otel-collector:4317` (gRPC) or `http://otel-collector:4318` (HTTP) |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `grpc` or `http/protobuf` |
| `OTEL_TRACES_SAMPLER` | `parentbased_traceidratio` |
| `OTEL_TRACES_SAMPLER_ARG` | `0.1` (10% root spans in prod) |
| `OTEL_LOG_LEVEL` | `info` (debug only when troubleshooting) |

Document all required vars in `.env.example`. Never commit backend credentials; use collector auth or secret mounts.

## Step 3 — Instrument the application

### Node.js (auto-instrumentation)

Load the SDK **before** other imports (separate `instrumentation.ts` or `--require ./instrumentation.js`):

```typescript
import { NodeSDK } from "@opentelemetry/sdk-node";
import { getNodeAutoInstrumentations } from "@opentelemetry/auto-instrumentations-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-grpc";
import { OTLPMetricExporter } from "@opentelemetry/exporter-metrics-otlp-grpc";
import { PeriodicExportingMetricReader } from "@opentelemetry/sdk-metrics";
import { Resource } from "@opentelemetry/resources";
import { ATTR_SERVICE_NAME, ATTR_SERVICE_VERSION } from "@opentelemetry/semantic-conventions";

const sdk = new NodeSDK({
  resource: new Resource({
    [ATTR_SERVICE_NAME]: process.env.OTEL_SERVICE_NAME ?? "app",
    [ATTR_SERVICE_VERSION]: process.env.npm_package_version ?? "0.0.0",
  }),
  traceExporter: new OTLPTraceExporter(),
  metricReader: new PeriodicExportingMetricReader({
    exporter: new OTLPMetricExporter(),
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();
process.on("SIGTERM", () => sdk.shutdown());
```

Add manual spans for domain events:

```typescript
import { trace } from "@opentelemetry/api";
const span = trace.getTracer("checkout").startSpan("charge.payment");
try {
  // work
} finally {
  span.end();
}
```

### Python (distro + instrumentors)

```python
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

resource = Resource.create({"service.name": os.environ["OTEL_SERVICE_NAME"]})
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)

HTTPXClientInstrumentor().instrument()
# After app = FastAPI(): FastAPIInstrumentor.instrument_app(app)
```

Or use `opentelemetry-instrument` CLI wrapper when a zero-code path is acceptable.

### Go

```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
    "go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
)

// Setup TracerProvider with OTLP exporter in main(); wrap handlers:
handler := otelhttp.NewHandler(mux, "api")
```

## Step 4 — Metrics and logs

**Metrics:** Use OTel API meters for business KPIs (orders placed, queue depth). Rely on HTTP/server auto-instrumentation for RED metrics (rate, errors, duration).

**Logs:** Prefer the OTel Logs SDK or bridge framework logging so records include `trace_id` and `span_id`. Map severity to OTel log levels. If the stack only supports trace + metrics initially, document log correlation as a follow-up — do not block traces on full log pipeline.

## Step 5 — Wire collector and backends

For local/dev stacks, add **OpenTelemetry Collector** to Compose (see [examples.md](examples.md)):

- **Receivers:** OTLP gRPC + HTTP
- **Processors:** `batch`, optional `memory_limiter`
- **Exporters:** `debug` (dev), `otlp` → Tempo/Jaeger, `prometheus` (metrics scrape endpoint), or vendor OTLP endpoint

Verify end-to-end:

1. Start collector + app with `OTEL_EXPORTER_OTLP_ENDPOINT` pointing at collector
2. Hit a health or sample API route
3. Confirm trace visible in UI or `debug` exporter stdout
4. Confirm metric scrape or OTLP metrics received

## Step 6 — Sampling and production hardening

| Environment | Sampler | Notes |
|-------------|---------|-------|
| Local / CI | `always_on` | Full traces for debugging |
| Staging | `parentbased_traceidratio` ~0.5 | Balance cost and coverage |
| Production | `parentbased_traceidratio` 0.05–0.2 | Tune by volume; keep errors 100% if backend supports tail sampling |

- Set timeouts on exporters; use `BatchSpanProcessor` (not simple sync export) in prod
- Cap attribute and event counts; avoid huge payloads in span attributes
- Health checks should be low-cardinality; exclude from high-cost custom metrics when possible

## Agent Checklist

- [ ] `OTEL_SERVICE_NAME` and resource attributes set
- [ ] OTLP endpoint configurable via env (works in Docker Compose and prod)
- [ ] Auto-instrumentation covers inbound HTTP and outbound clients
- [ ] Manual spans added for critical business operations only
- [ ] Exporter shuts down cleanly on process exit
- [ ] `.env.example` documents telemetry variables
- [ ] No duplicate proprietary + OTel agents without explicit reason
- [ ] Traces verified across at least one service boundary
- [ ] Sampling documented for non-dev environments

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Custom `X-Trace-Id` header only | W3C Trace Context via OTel propagators |
| Hardcoded `localhost:4317` in source | `OTEL_EXPORTER_OTLP_ENDPOINT` env var |
| Sync span export on every request | `BatchSpanProcessor` / SDK batch defaults |
| 100% trace sampling in high-QPS prod | Ratio or tail sampling |
| Logging full auth headers / bodies | Redact; use span attributes sparingly |
| Initializing SDK after HTTP server starts | Load instrumentation before framework imports |
| One giant span per request | Child spans for DB, cache, external HTTP |
| Metrics with unbounded label cardinality | Bounded labels (route template, not raw URL) |

## Additional Resources

- Language-specific setup and Compose collector: [examples.md](examples.md)
- Pre-deploy verification: [checklist.md](checklist.md)
