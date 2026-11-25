---
name: diff-review
description: "Run a multi-lens, read-only specialist review on a local branch diff, uncommitted diff, or PR (`git diff origin/<base>...HEAD`, working-tree diff, or a written diff artifact). Selects a content-aware mandatory baseline (`code-quality` for code diffs, `docs-quality` for docs-only diffs, or both for mixed diffs with substantial docs), activates up to 11 conditional specialist lenses (`testing`, `security`, `data`, `devops`, `observability`, `frontend`, `seo`, `product-owner`, `product-manager`, `performance`, `api-docs`) plus discovered external specialist agents, and uses smart delta re-runs across rounds. Use when reviewing existing code, documentation, or config changes in a diff, branch, or pull request. Do not use for pre-implementation issue breakdowns, epics, plans, or RFCs before code exists (use plan-review), interactive spec interrogation (use grill-me), or whole-repository audits across untouched modules (use codebase-audit)."
---

# Diff Review

Orchestrate a multi-lens, read-only specialist review of a branch diff (`git diff origin/<base>...HEAD`, an uncommitted working-tree diff, or a written diff artifact when sandboxing prevents git access) covering code, documentation, config, or mixed changes.

The orchestrator selects the content-aware baseline(s) and conditional lenses, dispatches fresh read-only sub-agents, tracks round state in a temporary ledger, escalates conflicts, and enforces the approval bar. **The orchestrator never reviews its own diff and never folds multiple lenses into one sub-agent.**

## Layout

```text
diff-review/
├── SKILL.md
└── references/
    ├── reviewer-contract.md     # Shared read-only, severity & terse output contract
    └── lenses/
        ├── code-quality.md      # Mandatory baseline for code diffs (flagship)
        ├── docs-quality.md      # Mandatory baseline for docs-only diffs / mixed substantial docs (flagship)
        ├── testing.md           # QA / SDET (fast/balanced)
        ├── security.md          # AppSec (flagship)
        ├── data.md              # DBA / Data Eng (flagship)
        ├── performance.md       # Performance (fast/balanced)
        ├── devops.md            # SRE / Platform (fast/balanced)
        ├── observability.md     # Tracing, metrics & logging (fast/balanced)
        ├── frontend.md          # UI / a11y / Impeccable audit (fast/balanced)
        ├── seo.md               # SEO / structured data / CWV (fast/balanced)
        ├── product-owner.md     # Acceptance & grill fidelity (fast/balanced)
        ├── product-manager.md   # Flow, rollout & MVP scope (fast/balanced)
        └── api-docs.md          # Contracts, errors & docs sync (fast/balanced)
```

---

## 1. Non-Negotiable Dispatch Rules

1. **Read-only reviewers**: Every reviewer reports findings only and edits nothing.
2. **One fresh sub-agent per lens per round**: Never fold two lenses into one sub-agent, and never reuse a sub-agent across rounds.
3. **Fail loud without sub-agents**: If the host environment cannot spawn sub-agents, stop and report the gap to the user/coordinator. Do not silently collapse lenses into a single-pass self-review.
4. **Soft lens budget**: At most **3 conditional lenses** (external specialists included) beyond the baseline(s). Lenses activated by a hard trigger (`security`, `data`) do not count. Each lens over budget needs a one-line reason recorded in the ledger and the round summary.
5. **Shared contract**: Pass every reviewer [references/reviewer-contract.md](references/reviewer-contract.md) (read-only rule, severities, terse output format) alongside its single lens guide.

---

## 2. Lens Selection & Activation Triggers

### Content-Aware Mandatory Baseline

Select at least one mandatory baseline based on what the diff actually touches:
- **Code / script / config diff** → `code-quality` (mandatory)
- **Docs-only diff** (`.md`, `docs/**`, `README*`, `AGENTS.md`, `SKILL.md`, ADRs, runbooks, guides — no executable code or runtime config) → `docs-quality` (mandatory; skip `code-quality`)
- **Mixed diff with substantial docs changes** (code + guides/skills/architecture docs, beyond minor comment or catalog tweaks) → **both** `code-quality` and `docs-quality`

### Trivial-Diff Path

When the diff has **under 50 changed lines** (added + deleted, `git diff --shortstat`) and fires **no hard trigger**, run the baseline lens(es) alone. Hard triggers: auth/authz, secrets/credentials, migrations/schemas, crypto, dependency manifests/lockfiles, or public API/CLI contracts — each activates its lens normally.

### Full Lens Roster

Activate each conditional lens **only** when the diff or task context matches its trigger:

| Lens | Tier | Activate Only When | Reference |
| :--- | :--- | :--- | :--- |
| `code-quality` | `flagship` | **Mandatory baseline** whenever executable code, scripts, or runtime/build config changed | [code-quality.md](references/lenses/code-quality.md) |
| `docs-quality` | `flagship` | **Mandatory baseline** for docs-only diffs; co-baseline on mixed diffs with substantial documentation/guide/skill changes | [docs-quality.md](references/lenses/docs-quality.md) |
| `testing` | `fast/balanced` | Behavior/logic changed, tests added/modified, or bugfix without regression test (not pure refactors whose existing tests still pass) | [testing.md](references/lenses/testing.md) |
| `security` | `flagship` | Auth/authz, input parsing, crypto, secrets, headers/CORS, file/shell/SQL ops, or dependencies changed | [security.md](references/lenses/security.md) |
| `data` | `flagship` | Migrations, schemas, ORM models, queries, indexes, transactions, or PII handling changed | [data.md](references/lenses/data.md) |
| `performance` | `fast/balanced` | Hot paths, loops/queries, caching, concurrency, network waterfalls, memory/FD lifecycle, or bundle size affected | [performance.md](references/lenses/performance.md) |
| `devops` | `fast/balanced` | CI/CD workflows, Docker/IaC, deploy scripts, runtime config/env, or healthchecks changed | [devops.md](references/lenses/devops.md) |
| `observability` | `fast/balanced` | Tracing, metrics, structured logging, SLO/alert rules, workers/queues, or retry/error boundaries changed | [observability.md](references/lenses/observability.md) |
| `frontend` | `fast/balanced` | UI components, styles, layout, client state, forms, or accessibility changed | [frontend.md](references/lenses/frontend.md) |
| `seo` | `fast/balanced` | Public web pages, SSR/SSG routes, metadata/OG, canonicals, sitemaps, `robots.txt`, or JSON-LD changed | [seo.md](references/lenses/seo.md) |
| `product-owner` | `fast/balanced` | The issue/spec has explicit acceptance criteria or confirmed grill decisions that the diff could break (not merely because an issue exists) | [product-owner.md](references/lenses/product-owner.md) |
| `product-manager` | `fast/balanced` | Multi-step user flows, feature flags, rollout/telemetry, or MVP scope boundaries are affected | [product-manager.md](references/lenses/product-manager.md) |
| `api-docs` | `fast/balanced` | Public HTTP/RPC/CLI/SDK interfaces, schemas, error shapes, or code-to-docs contract sync changed | [api-docs.md](references/lenses/api-docs.md) |

---

## 3. Open Discovery of External Specialist Agents

Before dispatching Round 1, scan project and user agent/skill directories for installed specialist reviewers:
- Project: `.claude/agents/`, `.claude/skills/`, `.kiro/agents/`, `.agents/`
- User: `~/.claude/agents/`, `~/.claude/skills/`, `~/.kiro/agents/`, `~/.agents/skills/`, `~/.gemini/config/`

Ignore `multi-implement`-managed profiles (marked with `<!-- multi-implement-managed: ... -->` or `"not an external specialist override"`, including `multi-implement-*`, `diff-review-*`, `plan-review-*`, and any legacy `herdr-*` or `review-*` wrappers).

When a discovered specialist matches the diff or task:
- **Overlapping domain**: If it covers the same domain as a built-in lens, even partly (e.g. a project-specific security or UI reviewer), it **replaces** that built-in lens. Never run both.
- **Distinct specialty**: If it covers a domain not in the built-in roster, run it **alongside** the active built-in lenses.
- **Contract**: Bind every external specialist to [references/reviewer-contract.md](references/reviewer-contract.md). Use `fast/balanced` unless the external agent is explicitly tagged as deep/flagship.

---

## 4. Two-Tier Model Guidance

Select the sub-agent model tier by lens depth using portable capability tiers (map each tier to your host's configured models/efforts, or follow project-level rules when present):

| Tier | Capability | Lenses |
| :--- | :--- | :--- |
| `flagship` | Strongest reasoning tier | `code-quality`, `docs-quality`, `security`, `data` (and deep-tagged external agents) |
| `fast/balanced` | Fast general-purpose tier | `testing`, `performance`, `frontend`, `seo`, `devops`, `observability`, `product-owner`, `product-manager`, `api-docs` (and external agents by default) |

On a docs-only diff that qualifies for the trivial-diff path, the orchestrator may dispatch `docs-quality` on `fast/balanced` (hosts with fixed per-lens profiles, such as synced Kiro agents, keep `flagship`).

---

## 5. Severity Mapping & Approval Bar

Every lens emits findings in the terse format defined in [references/reviewer-contract.md](references/reviewer-contract.md), with one of four severities:
- **`blocker` (P0)**: Must fix before approval.
- **`material` (P1)**: Must fix before approval.
- **`nitpick` (P2/P3)**: Non-blocking; the author may fix or reject with a written reason.
- **Out-of-scope**: May be deferred with a written reason (never silently dropped).

**Approval bar**: A round approves **only** when every active lens returns **zero `blocker` and zero `material` findings**.

---

## 6. Smart Delta Re-Runs & Ledger State

In every round (including Round 1), when reviewers cannot run `git` (e.g., sandboxed sub-agents inside a `git worktree`, whose `.git` gitfile points outside the worktree root), write the branch diff, changed-file list, and (on Round N+1) the round delta to `/tmp` or the session scratch directory before each round, and pass those files instead of git commands.

Maintain a temporary ledger file in `/tmp` or the session scratch directory (never commit it to the repository) so round state survives context compaction. Record:
- `prev_round_sha`: the `HEAD` commit reviewed in the last round (or prior working-tree snapshot hash when reviewing uncommitted changes)
- `active_lenses`: currently active lenses (initialized in Round 1, including active baseline(s)) and their status
- `findings_ledger`: per-lens list of `fixed`, `rejected` (with reason), and `deferred` (with reason) findings

### Round 1
1. Compute the base diff (`git diff origin/<base>...HEAD`, uncommitted diff, or written diff artifact).
2. Dispatch 1 fresh read-only sub-agent per active lens in parallel.
3. Record `prev_round_sha` and all findings in the temporary ledger.

### Round N+1 (after a fix commit or revision)
Re-run **only**:
1. **The active baseline lens(es)** (`code-quality` and/or `docs-quality`) **only when** the delta is ≥30 changed lines or adds a new file, function, or module (small targeted fixes for other lenses skip the baseline),
2. **any lens that rejected in Round N** (baselines included), and
3. **any conditional lens or external specialist whose domain files changed** (or a baseline newly activated by the delta) in `git diff <prev_round_sha>..HEAD` (or a written delta diff artifact when sandboxing prevents git access) — both invalidating previously approved lenses and activating newly triggered inactive lenses (adding them to `active_lenses`, including activating `code-quality` if a docs-only branch later introduces code). Check each lens's invalidation triggers/globs in `references/lenses/<lens>.md`, falling back conservatively to re-running whenever uncertain.

Pass each re-run sub-agent a **delta-only brief**:
- the delta since the prior round (`git diff <prev_round_sha>..HEAD` or written delta diff artifact) and the changed-file list,
- its own unresolved findings plus one-line summaries of its settled (`fixed` / `rejected` / `deferred`) ones — never other lenses' findings, and
- the full branch diff only as a path (`git diff origin/<base>...HEAD` or written diff artifact) to open on demand.

Update `prev_round_sha` and the temporary ledger at the end of the round.

### Escalation & Conflicts
- **Max rounds**: After 5 rounds without approval, or when a finding requires a product/architectural decision outside the author's scope, stop and escalate to the user/coordinator with options and a recommendation.
- **Conflict escalation**: When two lenses demand contradictory changes (e.g. `product-manager` vs `code-quality`), never pick a winner silently. Present both positions, the affected files, and a recommendation to the user/coordinator.
- **Post-approval commits**: Any commit made after approval (rebase conflict resolution, PR feedback) requires another delta round before the review remains valid.
