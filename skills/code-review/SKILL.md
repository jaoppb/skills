---
name: code-review
description: "Run a multi-lens, read-only specialist review on a branch diff or PR (`git diff origin/<base>..HEAD`). Always runs the mandatory `code-quality` baseline (structural rigor, <1k LOC guard, code-judo simplification), activates up to 10 conditional specialist lenses (`testing`, `security`, `data`, `devops`, `frontend`, `seo`, `product-owner`, `product-manager`, `performance`, `api-docs`) plus discovered external specialist agents, and uses smart delta re-runs across rounds. Use when reviewing existing code changes, diffs, branches, or pull requests. Do not use for whole-repository audits across untouched modules (use codebase-audit) or for interrogating a spec/plan before code exists (use grill-me)."
---

# Code Review

Orchestrate a multi-lens, read-only specialist review of a branch diff (`git diff origin/<base>..HEAD`, or a written diff file when sandboxing prevents git access).

The orchestrator selects lenses, dispatches fresh read-only sub-agents, tracks round state in a temporary ledger, escalates conflicts, and enforces the approval bar. **The orchestrator never reviews its own diff and never folds multiple lenses into one sub-agent.**

## Layout

```text
code-review/
├── SKILL.md
└── references/
    └── lenses/
        ├── code-quality.md      # Mandatory baseline (flagship)
        ├── testing.md           # QA / SDET (flagship)
        ├── security.md          # AppSec (flagship)
        ├── data.md              # DBA / Data Eng (flagship)
        ├── performance.md       # Performance (flagship)
        ├── devops.md            # SRE / Platform (fast/balanced)
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
4. **No hard lens cap**: Rely on tight activation triggers so typical diffs activate 2–4 lenses instead of spamming irrelevant reviewers.

---

## 2. Lens Selection & Activation Triggers

Always run `code-quality`. Activate each conditional lens **only** when the diff or task context matches its trigger:

| Lens | Tier | Activate Only When | Reference |
| :--- | :--- | :--- | :--- |
| `code-quality` | `flagship` | **Always** (mandatory baseline on every round) | [code-quality.md](references/lenses/code-quality.md) |
| `testing` | `flagship` | Behavior/logic changed, tests added/modified, or bugfix without regression test | [testing.md](references/lenses/testing.md) |
| `security` | `flagship` | Auth/authz, input parsing, crypto, secrets, headers/CORS, file/shell/SQL ops, or dependencies changed | [security.md](references/lenses/security.md) |
| `data` | `flagship` | Migrations, schemas, ORM models, queries, indexes, transactions, or PII handling changed | [data.md](references/lenses/data.md) |
| `performance` | `flagship` | Hot paths, loops/queries, caching, concurrency, network waterfalls, memory/FD lifecycle, or bundle size affected | [performance.md](references/lenses/performance.md) |
| `devops` | `fast/balanced` | CI/CD workflows, Docker/IaC, deploy scripts, runtime config/env, healthchecks, or telemetry infra changed | [devops.md](references/lenses/devops.md) |
| `frontend` | `fast/balanced` | UI components, styles, layout, client state, forms, or accessibility changed | [frontend.md](references/lenses/frontend.md) |
| `seo` | `fast/balanced` | Public web pages, SSR/SSG routes, metadata/OG, canonicals, sitemaps, `robots.txt`, or JSON-LD changed | [seo.md](references/lenses/seo.md) |
| `product-owner` | `fast/balanced` | Issue/spec/grill decisions or user-facing acceptance criteria exist for the branch | [product-owner.md](references/lenses/product-owner.md) |
| `product-manager` | `fast/balanced` | Multi-step user flows, feature flags, rollout/telemetry, or MVP scope boundaries are affected | [product-manager.md](references/lenses/product-manager.md) |
| `api-docs` | `fast/balanced` | Public HTTP/RPC/CLI/SDK interfaces, schemas, error shapes, README, or migration docs changed | [api-docs.md](references/lenses/api-docs.md) |

---

## 3. Open Discovery of External Specialist Agents

Before dispatching Round 1, scan project and user agent/skill directories for installed specialist reviewers:
- Project: `.claude/agents/`, `.claude/skills/`, `.kiro/agents/`, `.agents/`
- User: `~/.claude/agents/`, `~/.claude/skills/`, `~/.kiro/agents/`, `~/.agents/skills/`, `~/.gemini/config/`

When a discovered specialist matches the diff or task:
- **Overlapping domain**: If it clearly covers the same domain as a built-in lens (e.g. a project-specific security or UI reviewer), it **replaces** that built-in lens.
- **Distinct specialty**: If it covers a domain not in the built-in roster, run it **alongside** the active built-in lenses.
- **Contract**: Bind every external specialist to the exact same read-only rule and severity bar (`blocker` / `material` / `nitpick`). Use `fast/balanced` unless the external agent is explicitly tagged as deep/flagship.

---

## 4. Two-Tier Model Guidance

Select the sub-agent model tier by lens depth using portable capability tiers (map each tier to your host's configured models/efforts, or follow project-level rules when present):

| Tier | Capability | Lenses |
| :--- | :--- | :--- |
| `flagship` | Strongest reasoning tier | `code-quality`, `testing`, `security`, `data`, `performance` (and deep-tagged external agents) |
| `fast/balanced` | Fast general-purpose tier | `frontend`, `seo`, `devops`, `product-owner`, `product-manager`, `api-docs` (and external agents by default) |

---

## 5. Severity Mapping & Approval Bar

Every lens emits findings with one of four severities:
- **`blocker` (P0)**: Must fix before approval.
- **`material` (P1)**: Must fix before approval.
- **`nitpick` (P2/P3)**: Non-blocking; the author may fix or reject with a written reason.
- **Out-of-scope**: May be deferred with a written reason (never silently dropped).

**Approval bar**: A round approves **only** when every active lens returns **zero `blocker` and zero `material` findings**.

---

## 6. Smart Delta Re-Runs & Ledger State

Maintain a temporary ledger file in `/tmp` or the session scratch directory (never commit it to the repository) so round state survives context compaction. Record:
- `prev_round_sha`: the `HEAD` commit reviewed in the last round
- `active_lenses`: lenses assigned in Round 1 and their current status
- `findings_ledger`: per-lens list of `fixed`, `rejected` (with reason), and `deferred` (with reason) findings

### Round 1
1. Compute the base diff (`git diff origin/<base>..HEAD` or written diff artifact).
2. Dispatch 1 fresh read-only sub-agent per active lens in parallel.
3. Record `prev_round_sha = HEAD` and all findings in the temporary ledger.

### Round N+1 (after a fix commit)
Re-run **only**:
1. **`code-quality`** (always re-runs to catch fix-induced spaghetti or complexity),
2. **any lens that rejected in Round N**, and
3. **any conditional lens whose domain files changed** in `git diff <prev_round_sha>..HEAD` (or a written delta diff artifact when sandboxing prevents git access) — both invalidating previously approved lenses and activating newly triggered inactive lenses (adding them to `active_lenses`). Check each lens's invalidation triggers/globs in `references/lenses/<lens>.md`, falling back conservatively to re-running whenever uncertain.

Pass each re-run sub-agent:
- the current branch diff (`git diff origin/<base>..HEAD` or written diff artifact),
- the delta since the prior round (`git diff <prev_round_sha>..HEAD` or written delta diff artifact), and
- its prior rounds' `fixed` / `rejected` / `deferred` ledger so it focuses on regressions and unresolved gaps without re-litigating settled nitpicks.

### Escalation & Conflicts
- **Max rounds**: After 5 rounds without approval, or when a finding requires a product/architectural decision outside the author's scope, stop and escalate to the user/coordinator with options and a recommendation.
- **Conflict escalation**: When two lenses demand contradictory changes (e.g. `product-manager` vs `code-quality`), never pick a winner silently. Present both positions, the affected files, and a recommendation to the user/coordinator.
- **Post-approval commits**: Any commit made after approval (rebase conflict resolution, PR feedback) requires another delta round before the review remains valid.
