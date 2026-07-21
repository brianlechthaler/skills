# OpenTelemetry Examples

Copy-paste patterns referenced from [SKILL.md](SKILL.md). Pin package versions to match the project's lockfile policy.

## Docker Compose — Collector + Jaeger + Prometheus

Minimal local stack apps can export to:

```yaml
services:
  app:
    environment:
      OTEL_SERVICE_NAME: my-api
      OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317
      OTEL_EXPORTER_OTLP_PROTOCOL: grpc
      OTEL_TRACES_SAMPLER: always_on
    depends_on:
      - otel-collector

  otel-collector:
    image: otel/opentelemetry-collector-contrib:0.96.0
    command: ["--config=/etc/otel-collector-config.yaml"]
    volumes:
      - ./otel-collector-config.yaml:/etc/otel-collector-config.yaml:ro
    ports:
      - "4317:4317"   # OTLP gRPC
      - "4318:4318"   # OTLP HTTP
      - "8889:8889"   # Prometheus exporter scrape endpoint

  jaeger:
    image: jaegertracing/all-in-one:1.54
    ports:
      - "16686:16686" # UI

  prometheus:
    image: prom/prometheus:v2.49.1
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
    ports:
      - "9090:9090"
```

### `otel-collector-config.yaml`

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 5s
    send_batch_size: 1024

exporters:
  otlp/jaeger:
    endpoint: jaeger:4317
    tls:
      insecure: true
  prometheus:
    endpoint: 0.0.0.0:8889
  debug:
    verbosity: basic

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/jaeger, debug]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus, debug]
```

### `prometheus.yml` (scrape collector metrics)

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: otel-collector
    static_configs:
      - targets: ["otel-collector:8889"]
```

## Python — FastAPI bootstrap

`telemetry.py`:

```python
import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

def setup_telemetry() -> None:
    resource = Resource.create(
        {
            "service.name": os.environ.get("OTEL_SERVICE_NAME", "app"),
            "service.version": os.environ.get("SERVICE_VERSION", "dev"),
            "deployment.environment": os.environ.get("DEPLOYMENT_ENV", "local"),
        }
    )
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    HTTPXClientInstrumentor().instrument()
```

`main.py`:

```python
from telemetry import setup_telemetry

setup_telemetry()

from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)
```

Run with zero-code alternative when acceptable:

```bash
opentelemetry-instrument \
  --traces_exporter otlp \
  --metrics_exporter otlp \
  --service_name my-api \
  uvicorn main:app --host 0.0.0.0 --port 8000
```

## Node.js — Express entrypoint

`instrumentation.mjs`:

```javascript
import { NodeSDK } from "@opentelemetry/sdk-node";
import { getNodeAutoInstrumentations } from "@opentelemetry/auto-instrumentations-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-grpc";

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter(),
  instrumentations: [
    getNodeAutoInstrumentations({
      "@opentelemetry/instrumentation-fs": { enabled: false },
    }),
  ],
});

sdk.start();

process.on("SIGTERM", async () => {
  await sdk.shutdown();
});
```

```bash
node --import ./instrumentation.mjs src/server.js
```

## Go — HTTP server wrapper

```go
package main

import (
    "context"
    "log"
    "net/http"
    "os"
    "os/signal"

    "go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
    "go.opentelemetry.io/otel/sdk/resource"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.24.0"
)

func initTracer(ctx context.Context) (*sdktrace.TracerProvider, error) {
    exp, err := otlptracegrpc.New(ctx)
    if err != nil {
        return nil, err
    }
    res, err := resource.New(ctx,
        resource.WithAttributes(semconv.ServiceNameKey.String(os.Getenv("OTEL_SERVICE_NAME"))),
    )
    if err != nil {
        return nil, err
    }
    tp := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exp),
        sdktrace.WithResource(res),
    )
    otel.SetTracerProvider(tp)
    return tp, nil
}

func main() {
    ctx := context.Background()
    tp, err := initTracer(ctx)
    if err != nil {
        log.Fatal(err)
    }

    mux := http.NewServeMux()
    mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
    })

    srv := &http.Server{Addr: ":8080", Handler: otelhttp.NewHandler(mux, "api")}

    go func() { log.Fatal(srv.ListenAndServe()) }()

    quit := make(chan os.Signal, 1)
    signal.Notify(quit, os.Interrupt)
    <-quit
    _ = tp.Shutdown(ctx)
}
```

## Java — OpenTelemetry Java agent

Attach without code changes when using a JVM app:

```bash
java -javaagent:opentelemetry-javaagent.jar \
  -Dotel.service.name=my-service \
  -Dotel.exporter.otlp.endpoint=http://otel-collector:4317 \
  -Dotel.metrics.exporter=otlp \
  -Dotel.logs.exporter=otlp \
  -jar app.jar
```

## Manual span with attributes

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("order.checkout") as span:
    span.set_attribute("order.id", order_id)
    span.set_attribute("payment.provider", "stripe")
    # business logic
```

Use semantic conventions where they exist (`http.route`, `db.system`, `rpc.system`) instead of inventing attribute names.

## Verify traces locally

```bash
# After starting stack and hitting the app:
curl -s http://localhost:8080/health

# Jaeger UI
open http://localhost:16686

# Or watch collector debug exporter stdout
docker compose logs -f otel-collector
```

Expect a trace with at least one server span and child spans for outbound calls when auto-instrumentation is enabled.
