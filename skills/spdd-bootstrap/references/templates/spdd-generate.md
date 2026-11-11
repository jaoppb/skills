---
name: spdd-generate
description: "Generate {{PROJECT}} code and tests from a REASONS Canvas structured prompt, executing its Operations in order under its Norms and Safeguards. Use when a canvas from spdd-reasons-canvas is confirmed and ready to implement, or to regenerate the code affected by a canvas update. Do not use without a canvas (use spdd-reasons-canvas), and do not use it to patch code that diverged from the canvas (update the canvas first with spdd-prompt-update)."
---

# SPDD Generate

Generate implementation code from a structured SPDD prompt (a REASONS Canvas). Follow its Operations sequence, Norms and Safeguards strictly, within {{PROJECT}}'s rules (`{{RULES_DOC}}`).

**Input**: the canvas path, e.g. `@{{CANVAS_DIR}}/{{ID}}-<timestamp>-[Feat]-<scope>-<description>.md`.

## Steps

1. **Get the canvas.** If no path was given, ask the user for one. Do NOT proceed without a valid canvas.

2. **Resolve the work item (REQUIRED)**
   - Take it from the `{{ID}}-` file-name prefix (or the header line). If the canvas has none, stop: fix the canvas first with `/spdd-prompt-update`.
{{#issue}}
   - Verify it with `gh issue view <n> --json number,title,state`. Not found → stop. Closed → warn and ask.
{{/issue}}
{{#ephemeral}}
   - The canvas is an ephemeral working file: never stage it, commit it or name it by path in a commit, issue or pull request (write `{{REF}}`). If it does not exist, stop and run `/spdd-reasons-canvas {{REF}}`, which regenerates it from the analysis and the code already written.
{{/ephemeral}}

3. **Read the whole canvas** and extract its sections:

   | Section | Usage |
   |---------|-------|
   | **R** Requirements | Business context, Definition of Done, out of scope |
   | **E** Entities | Types, stereotypes, placement |
   | **A** Approach | Strategy, errors, tests{{#adr}}, decision records to write{{/adr}} |
   | **S** Structure | {{UNIT}}s, modules, implementations, dependencies, boundaries |
   | **O** Operations | **Execute in the defined order** |
   | **N** Norms | Change-specific standards on top of `{{RULES_DOC}}` |
   | **S** Safeguards | Non-negotiable constraints, exact error messages |

4. **Load the project rules and context**: `{{RULES_DOC}}` (the baseline norms every canvas inherits){{#adr}}, the decision records listed in the canvas header{{/adr}}, the tool configs below, and the modules named in Structure together with their closest existing patterns.
   {{FINGERPRINT_FILES}}

   Generated code MUST follow the existing conventions.

5. **Validate the Operations sequence**
   - The dependency order is right ({{OPERATION_ORDER}}), and no operation uses a type defined by a later one
   - No dependency breaks the boundary rules:
     {{ARCH_RULES}}
   - Each operation is atomic, names its {{UNIT}} and module, and lists its tests. Together they cover all of Structure, and they match its implementations, dependencies and boundary rules.

   If you find a problem, report it and suggest a `/spdd-prompt-update` before proceeding. Do NOT re-plan the sequence: the Operations order is the designed order.

6. **Generate the code, one operation at a time, in order**

   a. Read the operation spec: responsibility, representation, signatures, errors, behaviour and tests.

   b. **Apply the Norms** (`{{RULES_DOC}}` and the canvas Norms):
   {{CODING_NORMS}}

   c. **Enforce the Safeguards**:
   - Use the exact error names and messages (do not modify them)
   - Apply the domain, data and security constraints exactly as written
{{#zerolint}}
   - **Zero lint exceptions**: never write {{LINT_SUPPRESSIONS}}. If code cannot fit a rule, stop and report it. The fix is the canvas{{#adr}} or a project-wide decision record{{/adr}}, not an exemption.
{{/zerolint}}

   d. **Write the tests the operation lists**:
   {{TEST_NORMS}}

   e. Write the code in the {{UNIT}} and module the operation names.

   Do NOT deviate from the Operations, add features, methods or fields that are not specified, or change the Safeguard messages.

7. **Batch validation**

   After ALL the code is generated, run `{{CHECK_CMD}}` ({{CHECK_DESC}}).

   a. Fix failures by changing the code to fit the rule, never by adding exceptions.

   b. Cross-check every Definition of Done item, and check that the error names and messages match the Safeguards exactly.

   c. Check that placement matches Structure, that no forbidden dependency was introduced{{#zerolint}}, and that `{{LINT_GREP}}` prints nothing{{/zerolint}}.
{{#adr}}

   d. Check that the decision records{{#design}} and design docs{{/design}} the canvas requires exist ({{ADR_NEW}}).
{{/adr}}

   If a failure cannot be fixed without deviating from the canvas, stop and propose a `/spdd-prompt-update`.

8. **Report**: the work item and the canvas, the files created or changed and their responsibilities, any deviations or assumptions, the `{{CHECK_CMD}}` result, and the Definition of Done checklist (pass or fail per item).
{{#board}}
   Remind the user: {{BOARD_AFTER}}
{{/board}}
{{#issue}}
   The pull request body names the issue with `Closes #<n>`.
{{/issue}}

## Review and iteration loop

> **When reality diverges, fix the prompt first, then update the code.**

If the code was already changed by hand (a review fix) and more operations remain, first bring the canvas in line with it ({{#sync}}`/spdd-sync`{{/sync}}{{^sync}}`/spdd-reasons-canvas {{REF}}`, stale canvas{{/sync}}), so that generation does not undo the change.

1. Identify the incorrect or missing behaviour.
2. Trace it to a section: wrong interpretation → Requirements; missing type or relationship → Entities; flawed strategy → Approach; wrong placement → Structure; wrong detail → Operations; missing standard → Norms; missing constraint → Safeguards.
3. Update the canvas with `/spdd-prompt-update`.
4. Regenerate only the affected components.
5. Commit the code and its tests{{#issue}}, referencing the issue ({{COMMIT_REF}}){{/issue}}{{#ephemeral}}. The canvas is never part of a commit{{/ephemeral}}{{^ephemeral}} together with the updated canvas{{/ephemeral}}.

{{#mdlint}}
## Markdown output

Everything this skill writes to Markdown must pass `{{MDLINT_CMD}}`.

{{/mdlint}}
## Guardrails

- Do NOT generate code before reading the entire canvas and `{{RULES_DOC}}`
- Do NOT generate code for a canvas without a resolved work item
- Do NOT re-plan, reorder or skip operations
- Do NOT change signatures, field names, variant names or error messages from the specification
- Do NOT add features, types or fields that are not specified
{{#zerolint}}
- Do NOT add lint exceptions of any kind
{{/zerolint}}
- Do NOT patch code directly when issues are found: update the canvas first
- Always verify against the Definition of Done, and always finish with `{{CHECK_CMD}}` passing
{{#ephemeral}}
- Never stage the canvas: commit only code and tests
{{/ephemeral}}
{{#memory}}
- When generating reveals a trap too small for a decision record, offer to save it with the memory tools ({{MEMORY_TOOLS}}), and write it only if the user agrees ({{MEMORY_RULE}}). A trap that later changes must obey goes in a code comment{{#design}} or in `{{DESIGN_DIR}}`{{/design}}. The memory tools are optional: if they are unavailable, say so in one line and continue.
{{/memory}}
