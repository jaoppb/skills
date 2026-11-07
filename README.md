<div align="center">

<!-- Badges -->
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Standard](https://img.shields.io/badge/Standard-agentskills.io-blue.svg)
![Claude Code](https://img.shields.io/badge/Agent-Claude_Code-D97706.svg)
![Gemini CLI / Antigravity](https://img.shields.io/badge/Agent-Gemini_CLI-4285F4.svg)

<h3>jaoppb Agent Skills</h3>
<p>Modular, versioned Agent Skills following the <a href="https://agentskills.io">agentskills.io</a> specification.</p>

</div>

---

## Overview

This repository hosts a curated collection of agent skills designed to enhance autonomous coding agents (Claude Code, Gemini CLI / Antigravity, GitHub Copilot, Cursor, and more).

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
# Install herdr multi-agent coordination
npx skills add jaoppb/skills --skill herdr-multi-agent -g

# Install grill-me interrogation
npx skills add jaoppb/skills --skill grill-me -g

# Install herdr CLI integration
npx skills add jaoppb/skills --skill herdr -g

# Install thermo-nuclear code quality review
npx skills add jaoppb/skills --skill thermo-nuclear-code-quality-review -g

# Install codebase audit
npx skills add jaoppb/skills --skill codebase-audit -g
```

---

## Skills Catalog

| Skill | Description & Primary Trigger | Structure |
| :--- | :--- | :--- |
| [`herdr-multi-agent`](./skills/herdr-multi-agent/SKILL.md) | Coordinates multiple agents in parallel across separate Git worktrees using [Herdr](https://herdr.dev). Enforces wave planning, mandatory initial grilling (`/grill-me`), strict quality review loops, and automated PR creation. | Root `SKILL.md` + 10 modular reference runbooks under `references/`. |
| [`herdr`](./skills/herdr/SKILL.md) | Inspects and controls panes, tabs, workspaces, and agents running under the Herdr workspace manager via the `herdr` CLI. | Standalone `SKILL.md`. |
| [`grill-me`](./skills/grill-me/SKILL.md) | Interrogates a spec, plan, or design one hard question at a time to expose gaps and undecided trade-offs, then writes the decisions back. Used by every `herdr-multi-agent` worker at startup. | Standalone `SKILL.md`. |
| [`thermo-nuclear-code-quality-review`](./skills/thermo-nuclear-code-quality-review/SKILL.md) | High-rigor, unsparing maintainability and structural review. Identifies architectural leaks, spaghetti conditionals, bloated files, and enforces code simplicity. | Standalone `SKILL.md`. |
| [`codebase-audit`](./skills/codebase-audit/SKILL.md) | Audits a whole repository for smells, architecture, testing, security and tooling gaps by fanning work out to subagents, then produces a prioritized, issue-ready report. | Root `SKILL.md` + `references/` guides (generic, Rust, TypeScript/Next.js/React) + `scripts/`. |

---

## Structure

```text
skills/
├── codebase-audit/
│   ├── SKILL.md
│   ├── references/
│   └── scripts/
├── grill-me/
│   └── SKILL.md
├── herdr/
│   └── SKILL.md
├── herdr-multi-agent/
│   ├── SKILL.md
│   └── references/
│       ├── agent-effort.md
│       ├── cleanup.md
│       ├── coordinator-rules.md
│       ├── grilling.md
│       ├── reporting-protocol.md
│       ├── review-frontend.md
│       ├── review.md
│       ├── topology.md
│       ├── waves.md
│       └── worker-prompts.md
└── thermo-nuclear-code-quality-review/
    └── SKILL.md
```

---

## License

Distributed under the [MIT License](./LICENSE).
