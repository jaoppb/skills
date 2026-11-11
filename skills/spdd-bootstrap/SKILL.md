---
name: spdd-bootstrap
description: "Generates, once per repository, a project-tailored set of SPDD (Structured Prompt-Driven Development) skills: spdd-analysis, spdd-reasons-canvas, spdd-generate, spdd-prompt-update and, when canvases are committed, spdd-sync. It reads the project's rules, architecture, toolchain and tracker, and writes skills that use that project's own vocabulary and commands. Use when the user asks to set up, bootstrap, install, scaffold or regenerate SPDD / REASONS Canvas skills for a project, or to adapt the spdd-* skills to a new repository. Do not use to run an SPDD phase (analyse an issue, write a canvas, generate or sync code); the generated spdd-* skills do that. Do not use for general skill authoring that has nothing to do with SPDD."
---

# SPDD Bootstrap

Writes the SPDD skills **for one specific repository**. Generic SPDD skills give weak results because they don't know the project's layers, check command, decision records or domain vocabulary. These generated skills bake all of that in, just as hand-tuned skills would.

The templates in [references/templates/](references/templates/) hold the workflow. [scripts/render.py](scripts/render.py) fills them with the **project profile** and records what it wrote in `<skills-dir>/spdd.profile.json`.

## The generated skills

| Skill | Phase | Produces |
|-------|-------|----------|
| `spdd-analysis` | 0: strategic analysis ("what" and "why") | `## Analysis`, in the issue body or in an analysis file |
| `spdd-reasons-canvas` | 1: tactical design ("how") | the REASONS Canvas prompt file |
| `spdd-generate` | 2: implementation | code and tests that follow the canvas Operations |
| `spdd-prompt-update` | iteration: design changes first | an updated canvas |
| `spdd-sync` | iteration: code changed first | a canvas brought back in line with the code. **Committed canvases only** (decision D3) |

With ephemeral canvases, `spdd-sync` is not generated. A canvas dies at merge, so keeping it in line with the code only matters inside the branch. There, `spdd-reasons-canvas` rebuilds it from the analysis and the branch diff.

## Workflow

1. **Check for an existing set.** Look for `spdd.profile.json` in the project's skill directories (`.agents/skills/`, `.claude/skills/`, others). If it exists, this is a re-run: start the profile from it and go to step 3, re-checking only what changed. If there are `spdd-*` skills without a record, they were written by hand. Read them, and ask whether to replace them or stop. Never overwrite them silently.

2. **Build the project profile.** Write a profile JSON with every slot in [references/profile.md](references/profile.md), filled from the repository itself. Read the files; don't guess from the directory names. Discovery order and fallbacks are in that file.

3. **Settle the open decisions.** The decisions in [references/decisions.md](references/decisions.md) can't be read off the code. Ask about them **one at a time** and offer the recommended option first. When the repository already answers one (for example, `spdd/` is already gitignored), state the answer and move on.

4. **Confirm the profile.** Show the filled profile as one compact table with slot, value and source file. Proceed only after the user confirms. A wrong slot spreads into every generated skill.

5. **Render the skills.** Run the script, first with `--dry-run`, then for real. Then fix its `polish` notes by hand and rerun with `--force`. See [references/rendering.md](references/rendering.md).

6. **Verify.** Run the checklist in [references/rendering.md](references/rendering.md#verify): the script exits 0, every path the skills name exists, and the project's markdown linter passes (if it has one).

7. **Report.** Give the files you wrote (including `spdd.profile.json`, which is committed with the skills), the profile used, the decisions taken, and the suggested first run (`/spdd-analysis <issue or requirement>`). Don't commit unless the user asks.

## Rules

- **Grounded, not invented.** Every path, command, layer name and example in the generated skills comes from this repository. If a slot can't be found, ask. Never invent a plausible value.
- **Rules live in the rules doc.** The generated skills point to the project's rules document (`AGENTS.md`, `CLAUDE.md`, or whichever the project uses) and add only SPDD-specific behaviour. Don't copy the project's coding rules into every skill.
- **Optional features disappear cleanly.** If the project has no decision records, no spec, no memory tool or no tracker, drop the matching blocks entirely. Never write "N/A" or empty sections.
- **Portable wording.** Write "ask the user", not one host's tool name, unless the project targets a single agent host and its rules doc says so.
- **One run, one set.** Generate the whole set together from one profile, so the slots stay consistent across them.
