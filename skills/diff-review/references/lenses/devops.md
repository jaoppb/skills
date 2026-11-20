# DevOps Lens

- **Role**: SRE / Platform Engineer — CI/CD reliability, containers/IaC, runtime configuration, healthchecks, and rollback safety.
- **Tier**: `fast/balanced`
- **Activation Trigger**: Diff touches CI/CD workflows, Dockerfiles/compose, Kubernetes/Terraform/IaC, deploy/release scripts, runtime env/config, or readiness/liveness healthchecks. Stay off when no operational or build/deploy files change.
- **Delta Re-run Invalidation**:
  - `.github/workflows/**`, `Dockerfile*`, `docker-compose*`, `**/infra/**`, `**/terraform/**`, `**/k8s/**`, `**/helm/**`
  - `.env*`, `Makefile`, `justfile`, release/deploy scripts, healthcheck endpoints
  - *Conservative fallback*: re-run whenever uncertain whether a fix affects build, runtime config, or deployability.

## Check

- **CI/CD & build determinism**: Are workflow actions/images pinned? Are secrets scoped to minimum permissions (`permissions:` in GitHub Actions)? Do checks fail loud rather than swallowing errors (`set -e` / `|| true`)?
- **Containers & IaC**: Non-root user in containers, multi-stage builds, `.dockerignore` hygiene, resource limits, and no baked-in secrets?
- **Config & environment safety**: Are new env vars documented, validated at startup with clear errors, and given safe defaults (or explicit fail-fast when required)?
- **Healthchecks**: Do readiness/liveness probes accurately reflect critical dependencies without causing cascading restarts?
- **Rollback safety**: Can this change be rolled back cleanly without manual intervention or broken state?

## Presumptive Blockers

- **`blocker` (P0)**: Broken CI/deploy pipeline, baked-in secrets, overly permissive CI token/IAM grants, or silent error swallowing in critical release steps.
- **`material` (P1)**: Unvalidated required env vars causing cryptic runtime crashes, missing healthcheck/rollback consideration on infra changes, or unpinned risky build actions.
