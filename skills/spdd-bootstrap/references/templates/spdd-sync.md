<!-- spdd-bootstrap: render-if sync -->
---
name: spdd-sync
description: "Sync {{PROJECT}} code changes (refactors, review fixes, renames, new components) back into the REASONS Canvas, so the canvas reflects the actual implementation. Use when the code changed first and the canvas is now out of date. Do not use to make design changes before coding (use spdd-prompt-update), and do not use it to legitimise code that breaks the project rules."
---

# SPDD Sync

Synchronise implementation details from changed code back into the REASONS Canvas, so that the canvas stays an accurate source of truth for the design.

**Input**: the canvas path, e.g. `@{{CANVAS_DIR}}/{{ID}}-<timestamp>-[Feat]-<scope>-<description>.md`.

## Steps

1. **Get the canvas.** If no path was given, ask for one. Do NOT proceed without it.

2. **Read the canvas** and rank its sections by sync priority:

   | Section | Sync priority |
   |---------|---------------|
   | **R** Requirements | Low (rarely changes because of code) |
   | **E** Entities | High (type diagrams change) |
   | **A** Approach | Medium |
   | **S** Structure | High (dependencies and placement change) |
   | **O** Operations | **Highest** |
   | **N** Norms | Medium |
   | **S** Safeguards | Low (constraints rarely relax) |

   **Resolve the work items (REQUIRED).** The canvas's own item comes from the `{{ID}}-` prefix or the header; if it is missing, stop. The current item is the one the code changes belong to: take it from an argument, else from the branch name, else ask. If the two differ, ask which canvas is meant: a canvas belongs to the branch of its own work item.{{#gate}} Sync has no size gate.{{/gate}}
{{#issue}}
   Verify both items with `gh issue view <n> --json number,title,state`. Find the changes with `git log --grep '#<n>'` and `git diff`. When no commit mentions the issue, use `git diff {{MAIN_BRANCH}}...HEAD`.
{{/issue}}
{{^issue}}
   Find the changes with `git diff {{MAIN_BRANCH}}...HEAD`.
{{/issue}}
{{#ephemeral}}
   The canvas is an ephemeral working file for this branch: never stage it, commit it or name it by path (write `{{REF}}`). If it is missing, stop and run `/spdd-reasons-canvas {{REF}}`, which rebuilds it from the analysis and the code.
{{/ephemeral}}

   **Sync never legitimises a rule violation.** If the changed code breaks `{{RULES_DOC}}`{{#adr}}, a decision record{{/adr}}{{#zerolint}}, or needs a lint exception{{/zerolint}}, report it instead of writing it into the canvas.{{#adr}} Cite decision records by topic, as listed in `{{ADR_INDEX}}`, never by number.{{/adr}}

3. **Identify the affected components.** Ask the user which files, types or modules changed, what kind of change it was (renamed, restructured, logic changed, added) and what changed. Or derive the list from the git changes.

4. **Analyse the current implementation**
   - Read each affected source file and extract its types, fields, implemented interfaces, methods and their relationships.
   - Compare against the matching Entities, Structure and Operations entries: names and module paths, signatures, fields, logic steps, validation rules and error messages.
   - Categorise each difference as **structural**, **behavioural**, **naming**, **addition** or **deletion**.

5. **Present a sync plan** for review before changing anything:

   ```text
   ## Prompt Sync Plan

   ### Entities
   - [ ] Update: <type> — <field/variant change>

   ### Structure
   - [ ] Update: <dependency or placement change>

   ### Operations
   - [ ] Update: "<operation>" — <new signature / changed steps>
   - [ ] Add: <new component>
   - [ ] Remove: <obsolete operation>

   ### Norms / Safeguards
   - [ ] Update: <pattern adopted / message changed>
   ```

6. **Apply the approved updates**
   - **Entities**: make the Mermaid diagram match the actual types, stereotypes, placement and relationships.
   - **Structure**: update the implementations, dependencies and layer placement.
   - **Operations** (most critical): update the responsibility, {{UNIT}} and module, fields, signatures, logic steps and validation. Add operations for new components and remove obsolete ones.
   - **Norms**: record newly adopted patterns and naming conventions.
   - **Safeguards**: update the exact error messages and validation rules to match the code.

   Keep each section's structure, style and level of detail.

7. **Validate consistency**: the Entities diagram matches Structure, every Operation maps to a Structure component and back, no old names are left behind, and the Safeguard messages match the Operations.

8. **Report**: the sections updated, the specific changes, any inconsistencies resolved, and the points that need manual review.

{{#mdlint}}
## Markdown output

Everything this skill writes must pass `{{MDLINT_CMD}}`.

{{/mdlint}}
## Guardrails

- Do NOT remove content without explicit user approval, and confirm before any deletion
- Do NOT change Requirements unless the user asks (refactoring does not change business goals)
- Do NOT simplify or abbreviate existing detailed specifications
- Do NOT change Safeguard error messages unless they actually changed in the code
- Never change the canvas's work-item ID or header
- Never sync code that fails `{{CHECK_CMD}}`; fix the code first
- When in doubt, show the proposed change and ask

## Why sync

The canvas must reflect the **actual** implementation, not only the planned one. That way the rest of the work is generated from what the code really is, and regeneration stays consistent.{{#ephemeral}} The canvas only lives while the branch is open, so a sync matters only while more code will be generated from it. Whatever only the canvas knew belongs in the code, the tests or the design docs.{{/ephemeral}}
{{#memory}}

A trap found while syncing that is too small for a decision record can be offered to the memory tools ({{MEMORY_TOOLS}}), and written only if the user agrees ({{MEMORY_RULE}}). They are optional: if they are unavailable, say so in one line and continue.
{{/memory}}
