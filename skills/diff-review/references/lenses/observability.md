# Observability Lens

- **Role**: Observability & Reliability Engineer — structured logging, metrics cardinality, distributed tracing, and SLO/alerting readiness.
- **Tier**: `fast/balanced`
- **Activation Trigger**: Diff adds or modifies OpenTelemetry/tracing, metrics, structured logging, SLO/alert rules, background workers/queues, or external integration / retry / circuit-breaker error handling. Stay off for pure UI styling, docs, or trivial local refactors.
- **Delta Re-run Invalidation**:
  - Telemetry/logging/metrics setup, OTel/Sentry/Prometheus configs, alert rules/dashboards
  - Error-handling, retry/backoff, queue/worker, and outbound HTTP/RPC client wrappers
  - *Conservative fallback*: re-run whenever uncertain whether a fix alters instrumentation, error visibility, or metric labels.

## Check

- **Metrics & cardinality**: Are metric names/units consistent, and are labels strictly bounded (no user IDs, raw URLs with IDs, or free-form error strings that cause cardinality explosion)?
- **Distributed tracing & context**: Is trace/correlation context (`traceparent`, request ID) propagated across async boundaries, queues, and outbound HTTP/RPC calls without dropping spans or attaching sensitive payloads?
- **Structured logging & signal-to-noise**: Are errors logged with actionable structured fields (and without secrets/PII), avoiding silent `catch` blocks, unstructured `console.log` noise, or hot-path log storms?
- **Worker & integration visibility**: Do new background jobs, retries, circuit breakers, or dead-letter paths emit failure, latency, or lag signals so silent stalls are detectable?
- **Alerts & SLOs**: If alert rules or SLOs changed, are thresholds actionable and tied to user-facing symptoms rather than noisy transient spikes?

## Presumptive Blockers

- **`blocker` (P0)**: Unbounded high-cardinality metric label on a hot path, secrets/PII emitted in logs/traces/metrics, or silent swallowing of critical job/data-loss failures.
- **`material` (P1)**: Broken trace/correlation propagation across service or worker boundaries, new critical path/worker with zero failure instrumentation, or hot-path log spam.
