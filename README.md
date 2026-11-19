<div align="center">

<!-- Badges -->
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Standard](https://img.shields.io/badge/Standard-agentskills.io-blue.svg)
![Claude Code](https://img.shields.io/badge/Agent-Claude_Code-D97706.svg)
![Gemini CLI / Antigravity](https://img.shields.io/badge/Agent-Gemini_CLI-4285F4.svg)
![Kiro CLI](https://img.shields.io/badge/Agent-Kiro_CLI-7C3AED.svg)

<h3>jaoppb Agent Skills</h3>
<p>Modular, versioned Agent Skills following the <a href="https://agentskills.io">agentskills.io</a> specification.</p>

</div>

---

## Overview

This repository hosts a curated collection of agent skills designed to enhance autonomous coding agents (Claude Code, Gemini CLI / Antigravity, Kiro CLI, GitHub Copilot, Cursor, and more).

### Design Principles

1. **Progressive Disclosure**: Lean root `SKILL.md` documents that load procedural guidelines and detailed heuristics on demand from `references/`.
2. **Explicit Negative Bounds**: Precise semantic triggers with strict negative guardrails to prevent accidental activation.
3. **Agent Portability**: Universal procedural descriptions avoiding vendor-locked tool names.

---

## Installation

Install directly via the community [skills CLI](https://skills.sh) (`npx skills`):

### Install all skills globally

```bash
npx skills add jaoppb/skills -g
```

### Install a specific skill

```bash
# Install herdr multi-agent coordination (also install companion skills: herdr, grill-me, diff-review, plan-review)
npx skills add jaoppb/skills --skill herdr-multi-agent -g

# Install single-issue end-to-end implementation (also install companion skills: grill-me, diff-review, plan-review)
npx skills add jaoppb/skills --skill implement -g

# Install grill-me interrogation
npx skills add jaoppb/skills --skill grill-me -g

# Install herdr CLI integration
npx skills add jaoppb/skills --skill herdr -g

# Install multi-lens diff review (code, docs, and mixed diffs/PRs)
npx skills add jaoppb/skills --skill diff-review -g

# Install multi-lens plan review (issue breakdowns, refinements, epics, plans, RFCs)
npx skills add jaoppb/skills --skill plan-review -g

# Install codebase audit
npx skills add jaoppb/skills --skill codebase-audit -g

# Install SPDD bootstrap (generates project-tailored spdd-* skills)
npx skills add jaoppb/skills --skill spdd-bootstrap -g
```

---

## Skills Catalog

| Skill | Description & Primary Trigger | Structure |
| :--- | :--- | :--- |
| [`herdr-multi-agent`](./skills/herdr-multi-agent/SKILL.md) | Coordinates multiple agents in parallel across separate Git worktrees using [Herdr](https://herdr.dev). Enforces wave planning, optional pre-wave `plan-review`, mandatory initial grilling (`grill-me`), multi-lens `diff-review` loops, per-host protocols, and automated PR creation. | Root `SKILL.md` + 9 workflow runbooks under `references/` + 4 host protocols under `references/protocols/` + Kiro agent templates under `references/kiro-agents/` + `scripts/sync_kiro_agents.py`. |
| [`herdr`](./skills/herdr/SKILL.md) | Inspects and controls panes, tabs, workspaces, and agents running under the Herdr workspace manager via the `herdr` CLI. | Standalone `SKILL.md`. |
| [`implement`](./skills/implement/SKILL.md) | Implements a single issue, spec, or task end-to-end in one session: branch/worktree setup, mandatory `grill-me`, optional `plan-review`, checks/tests, multi-lens `diff-review` loop, and PR creation without Herdr or multi-agent overhead. | Standalone `SKILL.md`. |
| [`grill-me`](./skills/grill-me/SKILL.md) | Interrogates a spec, plan, or design one hard question at a time to expose gaps and undecided trade-offs, then writes the decisions back. Used by every `herdr-multi-agent` worker at startup. | Standalone `SKILL.md`. |
| [`diff-review`](./skills/diff-review/SKILL.md) | Multi-lens, read-only diff/branch/PR review with content-aware baseline (`code-quality` for code, `docs-quality` for docs-only, or both for mixed substantial docs), 11 conditional specialist lenses (`testing`, `security`, `data`, `devops`, `observability`, `frontend`, `seo`, `product-owner`, `product-manager`, `performance`, `api-docs`), open discovery of external specialists, and smart delta re-runs. | Root `SKILL.md` + 13 lens guides under `references/lenses/`. |
| [`plan-review`](./skills/plan-review/SKILL.md) | Multi-lens, read-only pre-implementation review of issue breakdowns, refinement tickets, epics, implementation plans, and RFCs/ADRs with mandatory `plan-quality` baseline, 4 conditional specialist lenses (`feasibility`, `slicing-and-dependencies`, `risk`, `product-alignment`), open discovery of external specialists, and revision-snapshot delta re-runs. | Root `SKILL.md` + 5 lens guides under `references/lenses/`. |
| [`codebase-audit`](./skills/codebase-audit/SKILL.md) | Audits a whole repository for smells, architecture, testing, security and tooling gaps by fanning work out to subagents, then produces a prioritized, issue-ready report. | Root `SKILL.md` + `references/` guides (generic, Rust, TypeScript/Next.js/React) + `scripts/`. |
| [`spdd-bootstrap`](./skills/spdd-bootstrap/SKILL.md) | Generates, once per repository, SPDD skills (`spdd-analysis`, `spdd-reasons-canvas`, `spdd-generate`, `spdd-prompt-update`, plus `spdd-sync` when canvases are committed) tailored to that project's rules, architecture, check command and tracker. | Root `SKILL.md` + `references/` (profile, decisions, rendering, Cosmo worked example, `templates/`) + `scripts/render.py`. |

---

## Structure

```text
skills/
├── codebase-audit/
│   ├── SKILL.md
│   ├── references/
│   └── scripts/
├── diff-review/
│   ├── SKILL.md
│   └── references/
│       └── lenses/
│           ├── api-docs.md
│           ├── code-quality.md
│           ├── data.md
│           ├── devops.md
│           ├── docs-quality.md
│           ├── frontend.md
│           ├── observability.md
│           ├── performance.md
│           ├── product-manager.md
│           ├── product-owner.md
│           ├── security.md
│           ├── seo.md
│           └── testing.md
├── grill-me/
│   └── SKILL.md
├── herdr/
│   └── SKILL.md
├── herdr-multi-agent/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── sync_kiro_agents.py
│   │   └── test_sync_kiro_agents.py
│   └── references/
│       ├── agent-effort.md
│       ├── cleanup.md
│       ├── coordinator-rules.md
│       ├── grilling.md
│       ├── kiro-agents/
│       │   ├── diff-review-lens.md
│       │   ├── herdr-coordinator.md
│       │   ├── herdr-worker.md
│       │   └── plan-review-lens.md
│       ├── protocols/
│       │   ├── agy.md
│       │   ├── claude.md
│       │   ├── fallback.md
│       │   └── kiro.md
│       ├── reporting-protocol.md
│       ├── review.md
│       ├── topology.md
│       ├── waves.md
│       └── worker-prompts.md
├── implement/
│   └── SKILL.md
├── plan-review/
│   ├── SKILL.md
│   └── references/
│       └── lenses/
│           ├── feasibility.md
│           ├── plan-quality.md
│           ├── product-alignment.md
│           ├── risk.md
│           └── slicing-and-dependencies.md
├── spdd-bootstrap/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── render.py
│   └── references/
│       ├── decisions.md
│       ├── example-cosmo.md
│       ├── profile.md
│       ├── rendering.md
│       └── templates/
│           ├── spdd-analysis.md
│           ├── spdd-generate.md
│           ├── spdd-prompt-update.md
│           ├── spdd-reasons-canvas.md
│           └── spdd-sync.md
```

---

## License

Distributed under the [MIT License](./LICENSE).
