# Product Alignment Lens

- **Role**: Product Owner & Product Manager — parent-spec/grill fidelity, user-journey coherence, user-visible edge cases, and MVP scope discipline.
- **Tier**: `fast/balanced`
- **Activation Trigger**: Plan derives from a parent epic, product spec, or confirmed `grill-me` decisions, or changes user-facing workflows, acceptance criteria, rollout, or UX. Stay off for pure internal engineering chores with no user-visible behavior or parent product spec.
- **Delta Re-run Invalidation**:
  - Any revision altering user-facing flows, acceptance criteria, non-goals, rollout/telemetry, or scope boundaries
  - *Conservative fallback*: re-run whenever uncertain whether a revision changes user-visible behavior or agreed requirements.

**Scope guardrail**: Never invent unrequested future-phase features beyond the parent spec, epic, or confirmed `grill-me` decisions. Judge strictly against delivering the agreed user value cleanly and completely.

## Check

- **Parent spec & grill fidelity**: Does the breakdown faithfully capture every confirmed decision and requirement from the parent epic/spec/`grill-me` output without silent omissions or compromises?
- **Non-goals & MVP discipline**: Did any ticket sneak in unrequested scope, speculative settings, or gold-plating that violates explicit non-goals?
- **End-to-end user journey**: Walking through the planned slices as an actual user, are entrypoints, transitions, feedback states, and exit paths coherent without dead ends?
- **User-visible edge cases**: Are the edge cases implied by the user story (empty state, invalid input, permission denied, cancellation, error recovery) accounted for in the acceptance criteria?
- **Rollout & measurement readiness**: If the parent spec calls for feature flags, gradual rollout, or telemetry/success metrics, are those explicitly scheduled rather than forgotten?

## Presumptive Blockers

- **`blocker` (P0)**: Drops a core requirement from the parent spec, contradicts a confirmed `grill-me` decision, or leaves an end-to-end user flow with a dead end.
- **`material` (P1)**: Partial requirement gap, missing user-visible edge case in acceptance criteria, missing agreed rollout/telemetry step, or clear scope creep violating an explicit non-goal.
