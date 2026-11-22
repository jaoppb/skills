---
name: plan-review
description: "Run a multi-lens, read-only specialist review on pre-implementation artifacts: issue breakdowns, refinement tickets, epics, implementation plans, dependency graphs, or RFCs/ADRs. Always runs the mandatory `plan-quality` baseline (clarity, explicit non-goals, testable acceptance criteria, plan-judo simplification), activates up to 4 conditional specialist lenses (`feasibility`, `slicing-and-dependencies`, `risk`, `product-alignment`) plus discovered external specialist agents, and uses revision-snapshot delta re-runs via `/tmp` without mutating the artifact or requiring git commits. Use when critiquing drafted issues, refinements, epics, plans, or RFCs before implementation begins. Do not use for reviewing git diffs, branches, or pull requests (use diff-review), for interactive one-question-at-a-time spec interrogation with the user (use grill-me), or for whole-repository audits (use codebase-audit)."
---

# Plan Review

Orchestrate a multi-lens, read-only specialist review of pre-implementation artifacts — issue breakdowns, refinement tickets, epics, implementation plans, dependency graphs, or RFCs/ADRs — before code is written.

The orchestrator fetches and snapshots the artifact into `/tmp` (or session scratch), selects lenses, dispatches fresh read-only sub-agents in parallel, tracks round state in a temporary ledger, escalates conflicts, and enforces the approval bar. **The orchestrator never reviews its own plan, never folds multiple lenses into one sub-agent, and never mutates the target artifact or tracker issues.**

## Layout

```text
plan-review/
├── SKILL.md
└── references/
    ├── reviewer-contract.md             # Shared read-only, severity & terse output contract
    └── lenses/
        ├── plan-quality.md              # Mandatory baseline (flagship)
        ├── feasibility.md               # Codebase & architecture grounding (flagship)
        ├── slicing-and-dependencies.md  # Multi-issue slicing, DAG & concurrency safety (fast/balanced)
        ├── risk.md                      # Security, data migration, rollback & failure modes (flagship)
        └── product-alignment.md         # Spec/grill fidelity, user edge cases & MVP scope (fast/balanced)
```

---

## 1. Non-Negotiable Dispatch Rules

1. **Read-only reviewers**: Every reviewer reports findings (and concrete suggested rewrites/splits) only; it edits nothing and mutates no tracker issues.
2. **Pre-snapshot to `/tmp` before dispatching**: The orchestrator fetches any remote tracker items (GitHub/Linear/Jira issues, parent epic, confirmed `grill-me` decisions) or collects local plan/RFC files and writes a single consolidated snapshot `/tmp/plan-<slug>-r<n>.md` (or in session scratch) before launching reviewers. Reviewers need only `/tmp` + repository read access — never shell, write, network, or MCP tools.
3. **One fresh sub-agent per lens per round**: Never fold two lenses into one sub-agent, and never reuse a sub-agent across rounds.
4. **Fail loud without sub-agents**: If the host environment cannot spawn sub-agents, stop and report the gap to the user/coordinator. Do not silently collapse lenses into a single-pass self-review.
5. **Soft lens budget**: At most **3 conditional lenses** (external specialists included) beyond `plan-quality`. `risk` activated by a hard trigger does not count. Each lens over budget needs a one-line reason recorded in the ledger and the round summary.
6. **Shared contract**: Pass every reviewer [references/reviewer-contract.md](references/reviewer-contract.md) (read-only rule, severities, terse output format) alongside its single lens guide.

---

## 2. Lens Selection & Activation Triggers

Always run `plan-quality`. Activate each conditional lens **only** when the artifact matches its trigger.

**Trivial-plan path**: A single standalone ticket, RFC, or ADR whose snapshot is **under 80 lines** and that hits no `risk` trigger runs `plan-quality` alone. Multi-issue breakdowns never take this path.

| Lens | Tier | Activate Only When | Reference |
| :--- | :--- | :--- | :--- |
| `plan-quality` | `flagship` | **Always** (mandatory baseline in Round 1; conditional re-run per §6) | [plan-quality.md](references/lenses/plan-quality.md) |
| `feasibility` | `flagship` | The plan or issue set targets an existing repository/codebase whose files, APIs, schemas, or tooling can be verified | [feasibility.md](references/lenses/feasibility.md) |
| `slicing-and-dependencies` | `fast/balanced` | Multi-issue breakdown, epic decomposition, backlog refinement batch, or task dependency graph (stay off for a single standalone RFC/ADR/ticket) | [slicing-and-dependencies.md](references/lenses/slicing-and-dependencies.md) |
| `risk` | `flagship` | Plan touches auth/permissions, secrets, data migrations/schemas, external APIs, backward compatibility, rollout/feature flags, or concurrency/scale | [risk.md](references/lenses/risk.md) |
| `product-alignment` | `fast/balanced` | Plan derives from a parent epic, product spec, or confirmed `grill-me` decisions, or changes user-facing flows/acceptance criteria | [product-alignment.md](references/lenses/product-alignment.md) |

---

## 3. Open Discovery of External Specialist Agents

Before dispatching Round 1, scan project and user agent/skill directories for installed specialist reviewers:
- Project: `.claude/agents/`, `.claude/skills/`, `.kiro/agents/`, `.agents/`
- User: `~/.claude/agents/`, `~/.claude/skills/`, `~/.kiro/agents/`, `~/.agents/skills/`, `~/.gemini/config/`

Ignore `herdr-multi-agent`-managed profiles (marked with `<!-- herdr-multi-agent-managed: ... -->` or `"not an external specialist override"`, including `herdr-*`, `diff-review-*`, `plan-review-*`, and any legacy `review-*` wrappers).

When a discovered specialist matches the plan's domain:
- **Overlapping domain**: If it covers the same domain as a built-in lens, even partly, it **replaces** that built-in lens. Never run both.
- **Distinct specialty**: If it covers a domain not in the built-in roster (e.g. a domain-specific compliance or design-system reviewer), run it **alongside** the active built-in lenses.
- **Contract**: Bind every external specialist to [references/reviewer-contract.md](references/reviewer-contract.md). Use `fast/balanced` unless the external agent is explicitly tagged as deep/flagship.

---

## 4. Two-Tier Model Guidance

Select the sub-agent model tier by lens depth using portable capability tiers (map each tier to your host's configured models/efforts, or follow project-level rules when present):

| Tier | Capability | Lenses |
| :--- | :--- | :--- |
| `flagship` | Strongest reasoning tier | `plan-quality`, `feasibility`, `risk` (and deep-tagged external agents) |
| `fast/balanced` | Fast general-purpose tier | `slicing-and-dependencies`, `product-alignment` (and external agents by default) |

---

## 5. Severity Mapping & Approval Bar

Every lens emits findings in the terse format defined in [references/reviewer-contract.md](references/reviewer-contract.md), with one of four severities:
- **`blocker` (P0)**: Must resolve before implementation starts (broken assumptions, impossible dependencies, untestable/contradictory requirements, irreversible data/security traps).
- **`material` (P1)**: Must resolve before approval (meaningful scope ambiguity, bad slicing, missing edge case or touchpoint, unmitigated risk).
- **`nitpick` (P2/P3)**: Non-blocking; the author may incorporate or reject with a written reason.
- **Out-of-scope**: May be deferred with a written reason (never silently dropped).

**Approval bar**: A round approves **only** when every active lens returns **zero `blocker` and zero `material` findings**.

---

## 6. Revision-Snapshot Delta Re-Runs & Ledger State

Maintain a temporary ledger file in `/tmp` or the session scratch directory (never commit it to the repository) so round state survives context compaction. Record:
- `prev_snapshot_path`: path to the prior round's snapshot (`/tmp/plan-<slug>-r<n>.md`)
- `active_lenses`: currently active lenses (initialized in Round 1) and their status
- `findings_ledger`: per-lens list of `fixed`, `rejected` (with reason), and `deferred` (with reason) findings

### Round 1
1. Gather the full target artifact (issue bodies, parent epic, plan/RFC markdown, or chat draft plus any confirmed `grill-me` decisions) and write `/tmp/plan-<slug>-r1.md`.
2. Dispatch 1 fresh read-only sub-agent per active lens in parallel, passing its lens guide path, `/tmp/plan-<slug>-r1.md`, and [references/reviewer-contract.md](references/reviewer-contract.md).
3. Record `prev_snapshot_path` and all findings in the temporary ledger, then present the consolidated findings (grouped by severity and lens) to the author/coordinator.

### Round N+1 (after the author revises the plan/issues)
1. Re-fetch or re-read the updated artifact and write `/tmp/plan-<slug>-r<n>.md`.
2. Compute a unified text diff against the previous snapshot (`diff -u /tmp/plan-<slug>-r<n-1>.md /tmp/plan-<slug>-r<n>.md > /tmp/plan-delta-<slug>-r<n>.diff`; exit code `1` from `diff` is expected when differences exist).
3. Re-run **only**:
   - **`plan-quality`** **only when** the delta is ≥20 changed lines or edits scope, acceptance criteria, or non-goals sections,
   - **any lens that rejected in Round N** (`plan-quality` included), and
   - **any conditional lens or external specialist whose domain was touched** in `/tmp/plan-delta-<slug>-r<n>.diff` — both invalidating previously approved lenses and activating newly triggered inactive lenses (adding them to `active_lenses`). Check each lens's invalidation triggers in `references/lenses/<lens>.md`, falling back conservatively to re-running whenever uncertain.

Pass each re-run sub-agent a **delta-only brief**:
- the revision delta (`/tmp/plan-delta-<slug>-r<n>.diff`),
- its own unresolved findings plus one-line summaries of its settled (`fixed` / `rejected` / `deferred`) ones — never other lenses' findings, and
- the current full snapshot (`/tmp/plan-<slug>-r<n>.md`) only as a path to open on demand.

Update `prev_snapshot_path` and the temporary ledger at the end of the round.

### Escalation & Conflicts
- **Max rounds**: After 5 rounds without approval, or when a finding requires a product/architectural decision that needs human judgment (a strong signal to run `grill-me`), stop and escalate to the user/coordinator with options and a recommendation.
- **Conflict escalation**: When two lenses demand contradictory changes (e.g. `slicing-and-dependencies` vs `product-alignment`), never pick a winner silently. Present both positions, the affected issues/sections, and a recommendation to the user/coordinator.
- **Post-approval edits**: Any substantive edit to the plan or issues after approval requires another delta round before the approval holds.
