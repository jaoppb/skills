---
name: spdd-reasons-canvas
description: "Generate an implementation-ready REASONS Canvas structured prompt (Requirements, Entities, Approach, Structure, Operations, Norms, Safeguards) for {{PROJECT}} from a requirement and its SPDD analysis. Use after spdd-analysis, when a work item is ready for detailed design, or to regenerate a lost canvas. Do not use to analyse a raw requirement (use spdd-analysis), to change an existing canvas (use spdd-prompt-update) or to write code."
---

# SPDD REASONS Canvas

Generate an implementation-ready structured prompt using the REASONS Canvas, specialised for **{{PROJECT}}**: {{STACK}}.

{{#issue}}
**Input**: a GitHub issue whose body holds the analysis from `/spdd-analysis` under `## Analysis`, plus optional `@` reading material.

```text
/spdd-reasons-canvas #12
/spdd-reasons-canvas #12 @docs/notes.md
```
{{/issue}}
{{^issue}}
**Input**: a requirement file `{{ANALYSIS_DIR}}/<slug>.md` that holds `## Analysis`, plus optional `@` reading material.

```text
/spdd-reasons-canvas @{{ANALYSIS_DIR}}/stock-ledger.md
```
{{/issue}}

## Steps

1. **Resolve the work item (REQUIRED)**

{{#issue}}
   a. Extract the issue number from the input: `#12`, `GH-12`, an issue URL, or the `GH-<n>-` prefix of a referenced `{{CANVAS_DIR}}/` file. If there is none, ask the user. Never invent a number.

   b. Verify it with `gh issue view <n> --json number,title,state,body`. Not found → stop. Closed → warn and ask. The title and body, with `## Analysis`, are the business context.
{{#taxonomy}}

   c. **Taxonomy.** {{TAXONOMY_RULE}} Warn, naming the missing field, and ask whether to continue.
{{/taxonomy}}
{{#exempt}}

   d. **Exemption.** {{EXEMPT_RULE}} Say so and ask whether to continue anyway; never refuse.
{{/exempt}}
{{/issue}}
{{^issue}}
   a. Take the slug from the referenced `{{ANALYSIS_DIR}}/<slug>.md`. If there is none, ask the user which requirement file to use.
{{/issue}}
{{#gate}}

   **Size gate.** {{GATE_RULE}} Read the size: {{GATE_READ}}. Below the threshold, not set, or unreadable → stop with one short message and ask "Continue anyway?". Never refuse; on no, change nothing.
{{/gate}}

   **Analysis check.** If the requirement has no `## Analysis` heading, stop and tell the user to run `/spdd-analysis {{REF}}` first. A canvas written from a bare requirement has no mapping onto the code, no decisions and no risks.

2. **Consolidate the context**

   - The requirement, including `## Analysis`, is the context. If the input adds requirement text the requirement lacks, ask the user to add it there first.
   - Read ALL `@` references completely (every relevant file in a folder). Report any that fail.
   - Do NOT summarise or truncate.

3. **Read the ground rules and the relevant code**

   Always read:
   - `{{RULES_DOC}}`: the canonical rules
{{#spec}}
   - `{{SPEC_DOC}}`: decisions and **non-goals**. A canvas never implements a non-goal.
{{/spec}}
{{#adr}}
   - `{{ADR_INDEX}}`, then every decision record relevant to the requirement
{{/adr}}
   {{FINGERPRINT_FILES}}

   Then, scoped to the requirement:
   - The affected modules and their layers
   - The existing shared types to reuse before inventing new ones
   - The existing interfaces and implementations in the affected modules{{#schema}}, the schema (`{{SCHEMA_GLOB}}`){{/schema}}, and the tests and test doubles
{{#design}}
   - The design docs in `{{DESIGN_DIR}}`{{#ephemeral}}. Canvases of other work items are local files and are not read.{{/ephemeral}}
{{/design}}
{{#memory}}
   - The memory tools ({{MEMORY_TOOLS}}), for gotchas and prior decisions on the affected area. They are optional and advisory: if they are unavailable, say so in one line, and the repository documents win on any conflict.
{{/memory}}

{{#adr}}
   If the requirement contradicts an accepted decision record, **stop and report it**. The fix is a superseding record, not a silent deviation.
{{/adr}}

4. **Apply the REASONS Canvas.** Generate fully populated content for all seven sections.

### R: Requirements

```text
## Requirements
{{#issue}}- Issue: #<n> — <issue title>
{{/issue}}[Concise verb phrases describing the essence of the requirement]

### Definition of Done
- [Observable, verifiable outcomes]

### Out of scope
- [Explicit exclusions{{#spec}}, including relevant non-goals{{/spec}}]
```

- What problem, for whom, and what value; the scope and what is explicitly not done
- Verb phrases ("Record…", "Derive…"); abstract the essential problem instead of listing features
- The core requirement fits in one sentence, and the Definition of Done is testable

### E: Entities

````text
## Entities
```mermaid
{{ENTITY_EXAMPLE}}
```
````

- Mark every type with a stereotype: {{STEREOTYPES}}
- Under the diagram, note the owning {{UNIT}} and layer of each type
{{ENTITY_RULES}}

**Conservative constraints (CRITICAL)**: reuse existing types first; leave current types unchanged when they already meet the requirement; restructure only when the requirement cannot be met otherwise; extend rather than rebuild{{#schema}}; {{SCHEMA_RULE}}{{/schema}}. No speculative abstractions.

### A: Approach

```text
## Approach
{{APPROACH_SECTIONS}}
```

- Follow `{{RULES_DOC}}`{{#adr}} and the decision records found by topic in `{{ADR_INDEX}}`{{/adr}}
- Give the rationale for each decision and name the rejected alternatives
- Name the risks and how the design contains them
{{#domainrefs}}
- Cite the reference in {{DOMAIN_REFS}} that governs each domain rule
{{/domainrefs}}
{{#adr}}
- Flag every new architectural choice as a decision record to write
{{/adr}}

### S: Structure

```text
{{STRUCTURE_OUTPUT}}
```

{{ARCH_RULES}}
{{#deps}}
- {{DEPS_RULE}}; justify each new dependency in the Approach
{{/deps}}
- Every component has exactly one home, and the dependency graph stays acyclic and within the boundary rules

### O: Operations

```text
{{OPERATIONS_EXAMPLE}}
```

- **Order by dependency**: {{OPERATION_ORDER}}
- Every operation names its {{UNIT}} and module, has one responsibility, and lists its tests (behaviour, not implementation)
- Write signatures in prose with inline code, never in code blocks (e.g. {{SIGNATURE_EXAMPLE}})
- The operations cover everything in Structure, with no logical gaps, and `/spdd-generate` can execute them directly
- **The last operation is always** `{{CHECK_CMD}}` passing{{#zerolint}} with zero lint exceptions{{/zerolint}}

### N: Norms

```text
## Norms
1. Baseline: {{NORMS_BASELINE}}
{{NORMS_LINES}}
```

- Do not restate `{{RULES_DOC}}`; reference it and add only what is specific to this change
{{#zerolint}}
- Zero lint exceptions: no {{LINT_SUPPRESSIONS}}. Design the code to fit the rule.
{{/zerolint}}
- Use the same patterns as the existing modules

### S: Safeguards

```text
## Safeguards
{{SAFEGUARD_LINES}}
```

- Each safeguard can be checked by a test, by `{{CHECK_CMD}}`, or by review; quantify where possible
- Error messages written here are copied verbatim by `/spdd-generate`

5. **Construct the structured prompt**

   ```text
   # [Derived Requirement Title]

{{#issue}}   - Issue: #<n>
   - Analysis: the `## Analysis` section of issue #<n>
{{/issue}}{{^issue}}   - Requirement: `{{ANALYSIS_DIR}}/<slug>.md`
{{/issue}}{{#adr}}   - Decision records: [titles, as listed in {{ADR_INDEX}}]
{{/adr}}   ```

   Then all seven sections, fully populated and in order. **Do NOT include** the raw business context, framework metadata (objective, guidance, quality standards), a timestamp or the framework name. No placeholders or TODOs.

   **No code blocks (CRITICAL)**: no source-language blocks, type or function bodies, query statements or config snippets. Describe signatures in prose with inline code. Mermaid diagrams are allowed.

6. **Save the canvas**

   a. File name: `{{ID}}-{TIMESTAMP}-[{ACTION}]-{scope}-{description}.md`. `TIMESTAMP` is `YYYYMMDDHHmm`. `ACTION` is one of `[Feat]`, `[Fix]`, `[Refactor]`, `[Test]`, `[Docs]`, `[Chore]`. `scope` is the most affected of {{SCOPES}}. `description` is kebab-case, < 10 words.

   b. Create `{{CANVAS_DIR}}/` if it is missing, and write the file there.
{{#ephemeral}}
   The canvas is an ephemeral working file for the current branch. `{{CANVAS_DIR}}` is gitignored: never stage it, never commit it, and never name it by path in a commit message, an issue or a pull request (write `{{REF}}` in prose).
{{/ephemeral}}
{{^ephemeral}}
   The canvas is versioned: commit it together with the code it describes.
{{/ephemeral}}

   c. **Existing or lost canvas.** If a canvas for this work item already exists, ask whether to update it with `/spdd-prompt-update` instead of writing a second one.
{{#ephemeral}}
   If it is missing partway through a branch (recreated worktree, new checkout, a switch of agent), regenerate it from `## Analysis` and the code already written (`git diff {{MAIN_BRANCH}}...HEAD`), and say that it was regenerated, since it may differ from the first. Anything only the lost canvas knew belongs in the code, the tests or the design docs.

{{^sync}}
   **Stale canvas.** If the branch code changed outside the canvas (review fixes, a hand refactor) and more code will be generated from it, rebuild it the same way, with the canvas as a third input. Code wins over the old canvas, and every difference is listed for the user. There is no separate sync step: the canvas only has to be right for the rest of this branch.
{{/sync}}
{{/ephemeral}}

   d. Show a summary: the path, a one-line summary of each section, the counts of types, operations and safeguards{{#adr}}, and the decision records to write{{/adr}}.

7. **Ask before implementing**: "The REASONS Canvas is ready. Proceed with `/spdd-generate`?"

{{#mdlint}}
## Markdown output

Everything this skill writes must pass `{{MDLINT_CMD}}`. Every fenced block has a language (`text`, `mermaid`). Use real headings, never bold lines. Put blank lines around headings, lists and fences.

{{/mdlint}}
## Guardrails

- **CRITICAL**: generate fully populated content for all seven sections, never just headers
- Do NOT proceed without a resolved work item{{#gate}}, or when the size gate or the analysis check stopped and the user did not confirm{{/gate}}{{^gate}}, or without `## Analysis`{{/gate}}
{{#adr}}
- Do NOT contradict an accepted decision record{{#spec}} or implement a non-goal{{/spec}}; report it instead
{{/adr}}
- Do NOT include framework metadata, code blocks, placeholders or TODOs
- Do NOT implement code before the user confirms the canvas
- The file name MUST follow the convention above
{{#ephemeral}}
- Never stage or commit a file under `{{CANVAS_DIR}}`, and never name a canvas by path outside the working tree
{{/ephemeral}}
- Every operation MUST name its {{UNIT}} and module and list its tests
- Conservative entity design: reuse existing types and avoid unnecessary refactoring
- Read ALL `@` references completely and merge them with the requirement into one context, preserving its intent
