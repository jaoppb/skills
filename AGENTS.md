# AGENTS.md

Instructions and guidelines for AI coding agents operating in this repository.

---

## 1. Repository Overview

This repository (`jaoppb/skills`) is a curated collection of agent skills adhering to the [agentskills.io](https://agentskills.io) specification. It provides modular, versioned skills for autonomous coding agents (Claude Code, Gemini CLI / Antigravity, GitHub Copilot, Cursor, and others) distributed via the community `skills` CLI (`npx skills`).

---

## 2. Repository Structure

```text
.
├── LICENSE
├── README.md
├── AGENTS.md
└── skills/
    ├── <skill-name>/
    │   ├── SKILL.md            # Required: Primary skill definition with frontmatter
    │   └── references/         # Optional: Detailed procedural guides, runbooks, heuristics
    └── ...
```

Existing skills in this repo:
- [`grill-me`](./skills/grill-me/SKILL.md): Interrogates a spec, plan, or design one question at a time and writes the decisions back.
- [`herdr`](./skills/herdr/SKILL.md): Standalone control of Herdr terminal multiplexer via CLI.
- [`herdr-multi-agent`](./skills/herdr-multi-agent/SKILL.md): Coordinator and worker agent patterns across Herdr worktrees. Uses modular guides in `references/`.
- [`thermo-nuclear-code-quality-review`](./skills/thermo-nuclear-code-quality-review/SKILL.md): Unsparing code maintainability and architectural review.

---

## 3. Skill Authoring Standards

Every skill in this repository must follow these design principles:

### A. Progressive Disclosure
- The root `SKILL.md` must be lean, clear, and scannable. It should introduce roles, core rules, and high-level workflows.
- Offload deep implementation details, checklists, complex heuristics, or multi-step runbooks into modular markdown files under `references/`.
- Cross-reference reference files using relative markdown links (e.g. `[references/waves.md](references/waves.md)`).

### B. Explicit Negative Bounds
- The `description` field in the frontmatter must clearly state both **when to activate** and **when NOT to activate**.
- Prevent false positives and accidental triggering by stating explicit guardrails (e.g., "Use only when the user explicitly mentions...", "Do not use merely because...").

### C. Agent Portability
- Write universal procedural descriptions rather than vendor-locked tool calls.
- Avoid hardcoding agent-specific internal functions unless the skill is intentionally specialized for a specific host tool or CLI environment (e.g. `herdr`).

### D. Frontmatter Specification
Each `SKILL.md` must start with valid YAML frontmatter:

```yaml
---
name: <skill-name>
description: "<Clear summary of function>. Use when <primary trigger>. Do not use when <negative bounds>."
---
```
- `name`: Must match the directory name in kebab-case.
- `description`: Single-line or properly wrapped YAML string containing functionality, triggers, and negative boundaries.

---

## 4. Development & Contribution Guidelines

### Adding a New Skill
1. Create a directory under `skills/<skill-name>/`.
2. Author `skills/<skill-name>/SKILL.md` adhering to the frontmatter and authoring standards.
3. If procedures or heuristics are non-trivial, create `skills/<skill-name>/references/` with focused, single-purpose markdown files.
4. Update `README.md` to catalog the new skill in the **Skills Catalog** table and directory tree.

### Editing Existing Skills
- **Surgical Edits**: Touch only what is necessary. Do not reformat unrelated sections or rewrite working prose unless directly addressing a bug or improvement.
- **Maintain Link Integrity**: When renaming or relocating reference files, update all relative links in `SKILL.md` and related reference documents.
- **Preserve Negative Bounds**: Never remove negative guardrails from frontmatter descriptions without explicit intent.

### Verification Checklist
Before concluding work on any skill:
- [ ] YAML frontmatter parses correctly and contains `name` and `description`.
- [ ] `name` exactly matches the skill folder name.
- [ ] Explicit negative bounds exist in the `description`.
- [ ] All relative links to `references/` or other files resolve to existing files.
- [ ] `README.md` remains in sync with the directory layout and catalog.

---

## 5. Agent Behavioral Rules

1. **Simplicity First**: Minimum changes that solve the problem. Do not add speculative abstractions or superfluous files.
2. **Surgical Changes**: Clean up only your own changes. Match existing tone, formatting, and markdown conventions.
3. **Verify Intent**: Verify file paths, frontmatter validity, and reference links before completing tasks.
4. **Fail Loud**: Never swallow errors or hide ambiguities. If requirements conflict or instructions are unclear, stop and ask.
