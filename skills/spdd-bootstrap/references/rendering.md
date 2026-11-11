# Rendering the templates

The templates are in [templates/](templates/). Each one becomes `<skills-dir>/<name>/SKILL.md` in the target repository. [scripts/render.py](../scripts/render.py) does the mechanical part. You do the profile beforehand and the polish afterwards.

## Run the script

```text
python3 <this-skill-dir>/scripts/render.py --profile <profile.json> --out <skills-dir> [--commands .claude/commands] [--dry-run] [--force]
```

- Run it with `--dry-run` first. It resolves every block, substitutes every slot, skips `spdd-sync` when `sync` is off, and reports:
  - `error`: a missing value or flag, an unknown flag, a multi-line value used inside a sentence, a broken `description`, or a `{{` left over. Fix the profile and rerun.
  - `warn`: a value that no rendered template uses, or a Cosmo word in the output that isn't in the profile.
  - `polish`: an empty sub-step or a gap in the step letters. Fix it by hand after writing.
  - `stale`: a skill from an earlier run that this run no longer generates. Delete it if that is intended.
- Then run it without `--dry-run`. `--commands <dir>` also writes each skill as a slash command (decision D4).
- The script writes `<skills-dir>/spdd.profile.json`: the profile, a hash of the templates and a hash of each generated file. Commit it with the skills.

**Re-runs.** Pass the record itself as `--profile`. If a generated file was edited by hand since the last run, the script stops with exit code 2 and lists the files. Show the user those edits, carry the ones worth keeping into the profile (or back into this skill's templates), then rerun with `--force`. When the templates changed since the last run, the script says so; review the regenerated diff with the user.

## Template syntax

| Syntax | Effect |
|--------|--------|
| `{{NAME}}` | Replaced with the value of slot `NAME` from the profile |
| `{{#flag}}…{{/flag}}` | Kept when `flag` is on; deleted along with its contents when off |
| `{{^flag}}…{{/flag}}` | Kept when `flag` is **off**; deleted when on |

A file whose first line is `<!-- spdd-bootstrap: render-if <flag> -->` (or `^<flag>`) is rendered only under that condition.

Blocks can nest and can sit inline in the middle of a sentence. When a tag stands alone on its line, the whole line goes with the tag, as in Mustache, so no stray blank lines are left inside lists. The script cannot reword prose, so after it writes, fix every `polish` note and reread the result. It must read as if it had been written by hand for this project.

**Hand polish and re-runs.** Polish edits change the file hashes, so a re-run reports them as hand edits. That is intended: rerun with `--force` right after polishing so the record matches the files, and the next real hand edit is caught.

## Rendering rules

1. **Render, then read.** After the script runs, read each generated skill from top to bottom as its user would. Rewrite any sentence that only makes sense with Cosmo or with another stack in mind.
2. **Examples come from the target.** Every example (entity diagram, operation, search term, signature, data flow, update request, sync item) uses names that exist in the target repository or that fit its domain. Leave no Cosmo names in it (`cosmo-*`, SEFAZ, NFC-e, Turso, `just`, crates) unless the target really uses them.
3. **Language-appropriate vocabulary.** Rewrite Rust-shaped words to fit the stack: `trait` → `interface`/`protocol`, `crate` → `{{UNIT}}`, `thiserror` → the project's error convention, `#[must_use]` → whatever the project actually uses. When the stack has no such concept, drop the line.
4. **Reference the rules doc and copy nothing from it.** When a template says "apply `{{RULES_DOC}}`", keep it as a reference. `CODING_NORMS` is the only condensed copy, because `spdd-generate` checks every line against it.
5. **Keep the guardrails.** Template guardrails exist because agents broke them. Adapt their wording to the project, but don't drop one unless its flag is off.
6. **Frontmatter.** `name` matches the directory. `description` is one line and keeps the template's "Do not use" clause.

## File placement

- The script writes `<skills-dir>/spdd-*/SKILL.md`, plus `spdd-sync` only when `sync` is on. If `spdd-sync` exists from an earlier run (or by hand) and `sync` is now off, the script reports it as `stale`; offer to delete it and its command mirror.
- If `ephemeral` is on and `.gitignore` doesn't cover `{{CANVAS_DIR}}`, add it with an `# SPDD canvases (local working files)` comment above it. In file mode, check with `git check-ignore {{ANALYSIS_DIR}}/x.md` that the analysis directory is **not** ignored.
- If the rules doc has no SPDD section, offer a short one: when to use SPDD, the phases, and where artifacts live. Write it only if the user agrees.

## Verify

- [ ] The script exited 0, with no `error` and every `polish` note fixed; the last write was a `--force` run after polishing.
- [ ] Every `warn` was read: unused values are expected only for flags that are off, and a Cosmo word is acceptable only if the target uses it.
- [ ] No generated skill mentions `spdd-sync` when `sync` is off.
- [ ] Every path the generated skills name (rules doc, spec, decision-record index, design dir, schema glob, domain refs) exists.
- [ ] `{{CHECK_CMD}}` is a real command here (it appears in a task-runner file or the rules doc). Don't run it unless the user asks.
- [ ] Each `SKILL.md` frontmatter parses, `name` equals its directory, and `description` keeps its "Do not use" clause.
- [ ] The step letters and numbers in each skill run in sequence, with no gaps left by deleted blocks.
- [ ] The generated skills agree on `CANVAS_DIR`, the ID format and the file-name pattern.
- [ ] `{{MDLINT_CMD}}` passes on the generated files, when `mdlint` is on.
