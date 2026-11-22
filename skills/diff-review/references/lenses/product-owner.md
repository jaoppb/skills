# Product Owner Lens

- **Role**: Product Owner — acceptance-criteria fidelity, confirmed grill-decision compliance, and user-story completeness.
- **Tier**: `fast/balanced`
- **Activation Trigger**: The issue/spec has explicit acceptance criteria, or confirmed grill-me decisions exist, that the diff could break. The mere existence of an issue is not enough. Stay off for pure refactors or chores with no behavioral acceptance criteria.
- **Delta Re-run Invalidation**:
  - Any file implementing user-facing behavior, acceptance criteria, or confirmed spec decisions
  - *Conservative fallback*: re-run whenever a fix changes user-visible behavior or edge-case handling.

**Scope guardrail**: Never invent new scope, features, or requirements beyond the issue, spec, or confirmed grill decisions. Judge strictly against what was agreed.

## Check

- **Acceptance-criteria fidelity**: Does the implementation satisfy every stated acceptance criterion in the issue/spec?
- **Grill-decision compliance**: Were all confirmed decisions from `grill-me` (or design review) faithfully implemented without silent compromises?
- **Non-goals & boundaries**: Did the PR stay within stated non-goals without sneaking in unrequested features?
- **User-visible edge cases**: Are the edge cases explicitly implied by the user story (empty state, invalid input, permission denied, cancellation) handled coherently?
- **Silent omissions**: Was any requirement quietly skipped, stubbed, or deferred without explicit disclosure?

## Presumptive Blockers

- **`blocker` (P0)**: Fails a core acceptance criterion, violates a confirmed grill decision, or silently ships a stubbed/incomplete required behavior.
- **`material` (P1)**: Partial acceptance-criterion gap, missing agreed edge-case handling, or scope creep violating an explicit non-goal.
