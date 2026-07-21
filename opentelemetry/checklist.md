# OpenTelemetry Deployment Checklist

Use before marking observability work complete or opening a PR.

## Configuration

- [ ] `OTEL_SERVICE_NAME` set per deployable service (unique, stable)
- [ ] `service.version` and `deployment.environment` on resource
- [ ] `OTEL_EXPORTER_OTLP_ENDPOINT` points at collector or backend (not hardcoded in code)
- [ ] Protocol matches endpoint (`grpc` vs `http/protobuf`)
- [ ] `.env.example` lists all telemetry variables
- [ ] Secrets for vendor backends injected via env/secrets manager, not committed

## Instrumentation

- [ ] SDK or agent loads before application framework handles traffic
- [ ] Inbound HTTP/gRPC instrumented
- [ ] Outbound HTTP/gRPC/DB clients instrumented (auto or manual)
- [ ] Context propagation verified across service boundary (if multi-service)
- [ ] Manual spans only for business-critical paths not covered by auto-instrumentation
- [ ] Health/readiness endpoints do not emit high-cardinality custom metrics

## Signals

- [ ] Traces visible in backend or collector `debug` exporter after sample request
- [ ] Metrics exported (RED or equivalent for HTTP services)
- [ ] Logs include trace correlation IDs when log pipeline supports it
- [ ] No secrets, auth tokens, or full PII in span attributes or log fields

## Production readiness

- [ ] Batch export enabled (not synchronous per-span in hot path)
- [ ] Sampling strategy set for non-dev (`parentbased_traceidratio` or tail sampling)
- [ ] Exporter shutdown on SIGTERM tested (no span loss on rolling deploy)
- [ ] Collector processors include `batch`; `memory_limiter` when volume is high
- [ ] Dashboards or runbook link documented (Jaeger, Grafana, vendor UI)

## Documentation

- [ ] README section: how to run with telemetry locally
- [ ] Required env vars and default endpoints documented
- [ ] Known gaps noted (e.g. log pipeline deferred)
