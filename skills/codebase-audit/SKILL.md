---
name: codebase-audit
description: "Audit an entire repository for code smells, architecture and design problems, language/framework/library misuse, and gaps in engineering practice (tests, error handling, security, dependencies, CI, docs), fanning the work out to subagents and producing a prioritized report whose findings are ready to become issues. Use when the user asks to audit, assess, health-check or find what is wrong with a whole codebase, map technical debt, find refactoring candidates, or get a list of improvements to file as issues. Do not use for reviewing a single diff or PR, for a strict review of a branch change (use thermo-nuclear-code-quality-review), or to fix code; the audit is read-only."
---

# Codebase Audit

Audit a whole repository against established software-engineering practice and produce a report of
improvement points that can each become an issue.

The repository is too large to read in one context, and a single reviewer drifts toward whatever it
read last. So the work is split: **you (the orchestrator) never read source files in bulk.** You
inventory the repo, plan partitions, dispatch subagents that each review one slice against the
relevant references, and then consolidate what they return into one report.

## Layout of this skill

```
codebase-audit/
├── SKILL.md                         ← you are here (orchestration)
├── scripts/
│   ├── inventory.py                 ← stack detection, metrics, suggested partitions (JSON)
│   └── merge_findings.py            ← validate, dedupe, rank, render report.md + issues.json
└── references/
    ├── generic-practices.md         ← the master table of language-agnostic practices (GEN-*)
    ├── code-smells.md               ← smell catalogue with detection heuristics (SMELL-*)
    ├── architecture.md              ← design principles, layering, boundaries (ARCH-*)
    ├── testing.md                   ← test strategy, AAA, boundaries, doubles, flakiness (TEST-*)
    ├── security.md                  ← secure-coding and supply-chain checks (SEC-*)
    ├── finding-format.md            ← the exact finding schema subagents must emit
    ├── subagent-prompts.md          ← prompt templates for each reviewer role
    ├── report-template.md           ← structure of the final report and issue bodies
    ├── rust/index.md                ← Rust specifics (RS-*)
    └── typescript/
        ├── index.md                 ← TypeScript specifics (TS-*)
        ├── framework/nextjs.md      ← Next.js specifics (NEXT-*)
        └── lib/react.md             ← React specifics (REACT-*)
```

Every rule in the references has a stable ID (e.g. `TEST-004`, `RS-012`). Findings cite rule IDs so
the report is traceable and so duplicates across subagents can be merged.

**Adding a language, framework or library:** create `references/<lang>/index.md`,
`references/<lang>/framework/<name>.md` or `references/<lang>/lib/<name>.md` following the shape of
the existing files (intro, tooling baseline, rule tables with a unique ID prefix, quick grep list).
`scripts/inventory.py` matches each package's dependency names to those file names automatically;
add an entry to `DEP_ALIASES` only when the package name differs from the file name (e.g.
`next` → `nextjs`), and to `LANG_BY_EXT` for a new language's file extensions. Nothing else needs
changing — partitions list the applicable reference files.

## Workflow

### Phase 0 — Scope

Settle three things before spending tokens, asking only if the user hasn't said:

1. **Repo root** — default the current working directory.
2. **Focus** — full audit (default), or a subset (e.g. "only tests", "only `packages/api`").
3. **Output location** — default `./.codebase-audit/<YYYY-MM-DD>/` at the repo root. Suggest adding
   it to `.gitignore` if it isn't.

The audit is read-only with respect to the codebase. Subagents must not edit, format, or "fix"
source files — the deliverable is a map of problems, and silent edits would make the report lie
about the code it describes.

### Phase 1 — Inventory (deterministic, cheap)

```bash
python3 <skill-dir>/scripts/inventory.py <repo-root> --out <audit-dir>/inventory.json
```

It reports: detected languages and LOC, frameworks and libs (from `Cargo.toml`, `package.json`,
lockfiles, config files), workspaces/packages, test files and their ratio to source, CI/lint/format
configs present or absent, largest files, and **suggested partitions** (each a set of paths sized for
one subagent, roughly 4–8k LOC, never splitting a package across partitions when avoidable). It also
lists which reference files apply to each partition.

Read the JSON summary (not the files it mentions). If the repo has a stack the skill has no
reference for, the generic references still apply — note the gap in the report's "Coverage" section
rather than inventing language rules.

When it's available, also run the project's own tools cheaply and capture output to the audit dir
for subagents to use as evidence (skip any that would take long or need network):
`cargo clippy --all-targets -- -W clippy::pedantic`, `cargo test --no-run`, `tsc --noEmit`,
`npx eslint . -f json`, `npm audit --json` / `cargo audit --json`, coverage reports already on disk.
Tool output is evidence, not the audit — a clean linter doesn't mean clean design.

### Phase 2 — Plan the fan-out

Use the partitions from the inventory and add cross-cutting reviewers. A typical plan:

| Reviewer | Scope | References it loads |
|---|---|---|
| `module-<n>` (one per partition) | the partition's paths | generic-practices, code-smells, the lang index + matching framework/lib files |
| `architecture` | whole repo, structure only (dir tree, module graph, entry points, imports) | architecture, generic-practices, lang index |
| `testing` | all test files + the code under test they point to (sampled) | testing, lang index (testing section), framework/lib testing sections |
| `security-deps` | manifests, lockfiles, config, auth/IO/boundary code, secrets scan | security, lang index (security section) |
| `tooling-docs` | CI, lint/format/type configs, README, CONTRIBUTING, ADRs, scripts | generic-practices (tooling & docs rows) |

Scale it: a 3k-LOC repo might need one module reviewer plus `architecture` and `testing`; a 300k-LOC
monorepo might need 30 module reviewers. Prefer more, smaller partitions over fewer large ones —
reviewers that skim produce vague findings. If the user asked for a focused audit, drop reviewers
outside the focus.

Create a task-list entry per reviewer so progress is visible. If the host has no subagent capability, run the reviewers one after another yourself, one slice and its references at a time, writing each findings file before starting the next.

### Phase 3 — Dispatch subagents

Read [references/subagent-prompts.md](references/subagent-prompts.md) and fill the template for each reviewer. Launch all reviewers
in the same turn, in the background, using a general-purpose agent type (it needs Read/Grep/Glob and
Write for its findings file). Key rules baked into the template, and why:

- **Load only the relevant references.** A Rust partition doesn't need React rules; loading them
  dilutes attention.
- **Write findings to a file, return a short summary.** Each reviewer writes
  `<audit-dir>/findings/<reviewer>.json` following `references/finding-format.md` and returns at most
  ~10 lines (counts by severity, top 3 titles, coverage notes). This is what keeps your context
  clean — never ask a reviewer to paste its findings back.
- **Evidence or it didn't happen.** Every finding needs a file path, line range, and a short
  excerpt or concrete observation. A reviewer that can't point at code should not file it.
- **Cite rule IDs**, and use `GEN-000` with an explanation when something is clearly wrong but no
  rule covers it.
- **Calibrate severity with the rubric** in finding-format.md, not with vibes.
- **Report patterns once.** If the same smell appears in 40 places, file one finding listing the
  locations (up to ~10, plus a count), not 40 findings.
- **Record what was not reviewed** (generated code, vendored code, files skipped for size) so the
  report's coverage is honest.

While they run, don't start reading source yourself. When notified that a reviewer finished, tick
its task and move on. If one fails or returns an empty/invalid file, re-dispatch it once with a
narrower scope; if it fails again, record the gap.

### Phase 4 — Consolidate

```bash
python3 <skill-dir>/scripts/merge_findings.py <audit-dir>
```

It validates every findings file against the schema (reporting malformed entries instead of
dropping them silently), merges duplicates (same rule + overlapping locations, or same rule + same
title across reviewers), sorts by priority (severity × confidence, then effort), assigns stable
IDs (`AUD-001`…), and writes:

- `<audit-dir>/report.md` — full report skeleton (see `references/report-template.md`)
- `<audit-dir>/issues.json` — one object per finding, issue-ready (title, body, labels, severity,
  effort, locations)
- `<audit-dir>/issues/AUD-xxx.md` — one markdown file per issue body, ready to paste or script

Then do the judgment work the script can't:

1. **Sanity-check the top findings.** For the critical/high ones, open the cited lines yourself
   (just those lines) to confirm the evidence holds. Downgrade or drop anything that doesn't — a
   false "critical" costs the report its credibility.
2. **Spot themes.** Several findings often share a root cause (e.g. no domain layer → business logic
   in handlers → untestable → low unit coverage). Group them under a theme and say so in the report;
   suggest an epic for the theme with the individual findings as child issues.
3. **Write the executive summary and scorecard** at the top of `report.md` (the script leaves
   placeholders marked `<!-- ORCHESTRATOR: ... -->`). Replace every placeholder.
4. **Note strengths.** A report that only lists faults reads as noise; one or two lines on what the
   codebase does well helps readers trust the rest and tells them what not to "fix".

### Phase 5 — Deliver

Tell the user, briefly: overall health in one sentence, counts by severity, the top 3–5 items, where
the report and `issues.json` live. Offer next steps that fit: creating the issues (e.g. via `gh issue
create --title ... --body-file issues/AUD-001.md --label ...` or a connected tracker), deepening one
area, or re-running after fixes to compare.

Don't create issues without the user saying so — filing dozens of tickets in someone's tracker is
hard to undo.

## Judgment guidelines

- **Context beats rules.** A 200-line function in a parser generated by a state machine is fine; the
  same in a request handler isn't. Reviewers should read the repo's README/ADRs first and respect
  deliberate, documented decisions — flag them only if the decision itself is risky, and say why.
- **Prefer fewer, sharper findings.** Ten precise findings with concrete fixes beat a hundred
  nitpicks. Style issues a formatter would fix collapse into one "adopt/enforce formatter" finding.
- **Severity is about consequences** (data loss, security, outages, blocked change), not about how
  ugly the code is.
- **Every finding must be actionable** — a suggested fix and an acceptance criterion someone could
  verify in a PR.
- **Don't punish small projects for missing enterprise ceremony.** Scale expectations (ADRs, SLOs,
  observability stacks) to the project's size and stage, which the inventory makes visible.
