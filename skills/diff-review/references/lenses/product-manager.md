# Product Manager Lens

- **Role**: Product Manager — end-to-end user flow coherence, rollout/feature-flag/telemetry readiness, and MVP scope discipline.
- **Tier**: `fast/balanced`
- **Activation Trigger**: Diff alters multi-step user journeys, introduces/modifies feature flags, affects rollout/backward-compatibility, or changes product telemetry/analytics events. Stay off for internal refactors or isolated bugfixes.
- **Delta Re-run Invalidation**:
  - User-flow entrypoints, navigation/routing, feature-flag checks, analytics/telemetry calls
  - *Conservative fallback*: re-run whenever uncertain whether a fix alters user flow, rollout gating, or telemetry.

**Scope guardrail**: Never invent new scope or future-phase features beyond the issue, spec, or confirmed grill decisions. Focus on coherence and safe shipping of the agreed MVP.

## Check

- **User flow coherence**: Do entrypoints, transitions, and exit states make sense end-to-end without dead ends or confusing mode switches?
- **Rollout & feature flags**: If gated behind a flag or gradual rollout, is the off-state safe and tested, and is the flag name/default consistent?
- **Telemetry & observability**: If the feature requires product events or conversion/error tracking per the spec, are events fired at the right point without PII?
- **MVP scope discipline**: Is the PR shipping the leanest coherent slice, or did it accumulate speculative knobs/settings that belong in a later iteration?

## Presumptive Blockers

- **`blocker` (P0)**: Broken end-to-end user journey (dead-end state), unsafe feature-flag default exposing half-finished behavior, or breaking existing user workflows without migration.
- **`material` (P1)**: Missing required rollout/telemetry hook from the spec, confusing UX transition, or speculative scope bloat.
