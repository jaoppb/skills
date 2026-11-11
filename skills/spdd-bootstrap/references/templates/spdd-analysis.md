---
name: spdd-analysis
description: "Analyze a {{PROJECT}} requirement{{#issue}} (a GitHub issue){{/issue}} against the codebase at a strategic level: domain concepts, strategic direction, risks and Definition of Done gaps, as input for REASONS Canvas generation. Use when starting SPDD work on a requirement{{#gate}} that passes the size gate{{/gate}}, or when the analysis must be revised. Do not use to design the implementation (use spdd-reasons-canvas) or to write code."
---

# SPDD Analysis

Analyze a requirement against the current codebase and produce a **strategic-level** analysis. It adds domain concept identification, high-level approach decisions and risk analysis to what the requirement already says, and it is the input for `/spdd-reasons-canvas`. This phase covers the "what" and the "why"; the "how" belongs to the REASONS Canvas.

{{#issue}}
**Input**: a GitHub issue. The issue body is the requirement. `@` file references are reading material to analyse against, not requirement.

```text
/spdd-analysis #12
/spdd-analysis #14 @docs/notes.md
```

The analysis is written into the issue body under one `## Analysis` heading, never into a file.
{{/issue}}
{{^issue}}
**Input**: a requirement file `{{ANALYSIS_DIR}}/<slug>.md`, or a requirement typed in the prompt. `@` file references are reading material to analyse against, not requirement.

```text
/spdd-analysis @{{ANALYSIS_DIR}}/stock-ledger.md
/spdd-analysis "Record every stock movement in a ledger"
```

The analysis is written into the requirement file, under one `## Analysis` heading that is always last.
{{/issue}}

## Steps

0. **Resolve the work item (REQUIRED)**

{{#issue}}
   a. Extract the issue number from the input: `#12`, `GH-12`, or an issue URL.

   b. If no issue is found, ask the user: "Which GitHub issue does this work belong to? (number or URL)". Do NOT proceed without one. Never invent a number or use a placeholder.

   c. Verify it with `gh issue view <n> --json number,title,state,body`. Not found → stop and report. Closed → warn and ask whether to continue. The issue title and body are the requirement.
{{#taxonomy}}

   d. **Taxonomy.** {{TAXONOMY_RULE}} Warn, naming the missing field, and ask whether to continue.
{{/taxonomy}}
{{#exempt}}

   e. **Exemption.** {{EXEMPT_RULE}} Say so and ask whether to continue anyway; never refuse.
{{/exempt}}
{{/issue}}
{{^issue}}
   a. If the input is a file under `{{ANALYSIS_DIR}}/`, it is the requirement and its slug is its file name.

   b. If the input is typed text, derive a kebab-case slug (< 6 words), confirm it with the user, and write the text to `{{ANALYSIS_DIR}}/<slug>.md` under `## Requirement`. Then continue from that file.

   c. If there is no input, ask the user for the requirement. Never invent one.
{{/issue}}
{{#gate}}

   **Size gate** ({{GATE_SECTION}}). {{GATE_RULE}} Read the size: {{GATE_READ}}. If the size is below the threshold, is not set, or cannot be read, stop with one short message that says which case applies{{#exempt}} (together with the exemption question when both apply){{/exempt}}, and ask "Continue anyway?". Never refuse and never print a token. On yes, continue; on no, stop and change nothing.
{{/gate}}
{{#board}}

   **Board.** {{BOARD_START}}
{{/board}}

1. **Read the requirement**

   a. The requirement{{#issue}} (the issue body){{/issue}} is the only source of requirements. If the input adds requirement text that it does not hold, say so and ask the user to add it to the requirement first. Never put that text into the analysis instead.

   b. If the input contains `@` file or folder references, read ALL of them completely (every relevant file in a folder). If any cannot be read, report it and ask for an alternative.

   c. Check that the requirement has a goal, a scope and a Definition of Done. If not, ask the user to complete it first.

2. **Concept-driven codebase exploration**

   Do NOT read the whole codebase. Build a lightweight fingerprint, extract search concepts from the requirement, then explore only the relevant parts in depth.

   a. **Project fingerprint (always first, fast)**:
   - Read `{{RULES_DOC}}` (the rules){{#spec}} and `{{SPEC_DOC}}` (decisions and **non-goals**){{/spec}}
   {{FINGERPRINT_FILES}}
   - List {{SOURCE_DIRS}} (directory names only) to see which modules exist
{{#adr}}
   - Read `{{ADR_INDEX}}` (the decision-record index; read single records only when a concept touches them)
{{/adr}}

   b. **Extract search concepts** from the requirement:
   {{DOMAIN_EXAMPLES}}

   These concepts are the search scope for everything that follows.


   c. **Targeted schema and reference exploration**:
{{#schema}}
   - Search `{{SCHEMA_GLOB}}` for tables or schemas whose names match the domain nouns. Read only the matches, then follow references **one hop outward** to capture boundary context
{{/schema}}
{{#domainrefs}}
   - For concepts governed by {{DOMAIN_REFS}}, find the governing rule there instead of guessing
{{/domainrefs}}

   d. **Targeted code exploration**:
   - Search for types, interfaces and modules that match the concepts (e.g. {{CODE_SEARCH_EXAMPLES}})
   - Read the matched files to learn the existing invariants, error types, boundaries and adapters
   - Follow direct dependencies **one hop** (read the interface a use case takes and its implementations, but don't keep chaining)
   - Note which module owns each concept and which shared types already exist for reuse
   - Observe conventions in use (naming, error types, test doubles, test names)
   - If no matching code exists, say so explicitly and rely on `{{RULES_DOC}}`{{#adr}} and the decision records{{/adr}}

   e. **Design and decision context**:
{{#design}}
   - List `{{DESIGN_DIR}}` and read only the files whose names match the concepts{{#ephemeral}} (canvases are local working files and are not a source){{/ephemeral}}
{{/design}}
{{#adr}}
   - Read the decision records the concepts touch, found by topic in `{{ADR_INDEX}}`; never cite a record by number from memory
{{/adr}}
{{#memory}}
   - Ask the memory tools ({{MEMORY_TOOLS}}) for gotchas, decisions and prior sessions on the concepts, and use what they return as hints to check against the code. They are optional: when they are missing, unreachable or empty, say so in one line and continue. Their answers are advisory, and the repository documents and the requirement win on any conflict.
{{/memory}}

   f. **Controlled expansion (one extra hop only)**: if steps c–e reveal a concept that is clearly essential but was not extracted, add it and do **one** more targeted search. Stop there and note the boundary.

   If the scope turns out very large (10+ existing modules), list all concepts, prioritise the core ones, and mark the rest as "boundary context" to verify during the REASONS Canvas.

3. **Domain Concept Identification**: conceptual level only, with no attributes, types or signatures.

   ```text
   ### Domain Concept Identification

   #### Existing Concepts (from codebase)
   - [ConceptName]: [business purpose] — [where it lives] — [relationship to other concepts]

   #### New Concepts Required
   - [ConceptName]: [business purpose] — [how it relates to existing concepts]

   #### Key Business Rules
   - [Rule, explicit or implicit]: [which concepts it governs]
   ```

4. **Strategic Approach & Trade-offs**: direction, not specifics (no queries, payload shapes, signatures or step-by-step logic).

   - The overall approach, the existing patterns to reuse, and the general data flow (e.g. "{{DATAFLOW_EXAMPLE}}")
   - The key decisions: their trade-offs, the recommendation and why
{{#adr}}
   - Any conflict with an accepted decision record{{#spec}} or a non-goal in `{{SPEC_DOC}}`{{/spec}}: flag it. It needs a superseding record or must be dropped, never silently implemented
   - Which choices are new architectural decisions that need a record
{{/adr}}
{{^adr}}
{{#spec}}
   - Any conflict with a non-goal in `{{SPEC_DOC}}`: flag it, never silently implement it
{{/spec}}
{{/adr}}

   ```text
   ### Strategic Approach

   #### Solution Direction
   - [High-level description of approach]

   #### Key Design Decisions
   - [Decision]: [trade-offs] → [recommendation and rationale]

   #### Alternatives Considered
   - [Alternative]: [why rejected]
   ```

5. **Risk & Gap Analysis**: surface everything that needs clarifying before detailed design. List only the gaps; never restate the Definition of Done.

   ```text
   ### Risk & Gap Analysis

   #### Requirement Ambiguities
   - [Ambiguity]: [what needs clarification]

   #### Edge Cases
   - [Scenario]: [why it matters]

   #### Technical Risks
   - [Risk]: [potential impact and mitigation direction]

   #### Definition of Done Gaps
   - [Item or scope line]: [what the Definition of Done does not check]
   ```

6. **Assemble** `## Analysis` with the three `###` sections above, in that order. The exploration in step 2 is a working process: its findings show up as file paths and conventions inside the sections, never as a separate "codebase context" section. Never paste what the requirement already says.

7. **Write the section**

   `## Analysis` is always the last section, and nothing above it is ever changed.

{{#issue}}
   a. Write the body through a temporary file, never an inline string: `gh issue edit <n> --body-file <file>`.

   b. **No `## Analysis` yet**: append it after the existing text, with one blank line between them.

   c. **`## Analysis` already there**: show the user the `###` entries you would add, change or drop, each with a one-line reason. Edit only those and keep the others word for word. After the user confirms, read the live body again (`gh issue view <n> --json body`). If it has changed since you read it, stop and tell the user. Never write over someone else's edit.
{{/issue}}
{{^issue}}
   a. **No `## Analysis` yet**: append it to `{{ANALYSIS_DIR}}/<slug>.md`.

   b. **`## Analysis` already there**: show the user the `###` entries you would add, change or drop, each with a one-line reason. Edit only those after the user confirms.
{{/issue}}

   Then show a summary: the work item, the modules involved, the counts of existing concepts, new concepts, key decisions, Definition of Done gaps and open risks{{#adr}}, the decision-record conflicts or new records needed{{/adr}}, and the next step `/spdd-reasons-canvas {{REF}}`.

8. **Offer the next phase**: "The analysis is ready. Proceed with `/spdd-reasons-canvas {{REF}}`?"

{{#mdlint}}
## Markdown output

Everything this skill writes must pass `{{MDLINT_CMD}}`. Every fenced block has a language (`text`, `mermaid`). Use real headings, never bold lines. Put blank lines around headings, lists and fences.

{{/mdlint}}
## Guardrails

- Do NOT proceed without a resolved work item; never use a placeholder
{{#gate}}
- Do NOT proceed when the size gate stopped and the user did not confirm
{{/gate}}
- Do NOT skip codebase exploration, and do NOT read the whole codebase: scope by concepts
- Do NOT assume structure without reading the actual files
- Do NOT paste what the requirement already says (requirement, scope, Definition of Done)
- Use {{PROJECT}}'s vocabulary: {{ARCH_VOCAB}}
{{#adr}}
- Do NOT propose anything that contradicts an accepted decision record{{#spec}} or a non-goal{{/spec}} without flagging it
{{/adr}}
- Do NOT include implementation detail (queries, payload shapes, signatures, attributes, step-by-step logic); that belongs to `/spdd-reasons-canvas`
- Do NOT generate code or modify any file in the codebase{{#issue}}, and never change the issue body above `## Analysis`{{/issue}}
- Do NOT leave placeholders or TODOs
- Definition of Done gaps MUST be listed, and only the gaps; ambiguities MUST be surfaced, never silently assumed
- Read ALL `@` references completely, never truncated; report any that fail

## Where this fits

`/spdd-analysis` (what and why) → `/spdd-reasons-canvas` (how) → `/spdd-generate` (code) → `/spdd-prompt-update`{{#sync}} or `/spdd-sync`{{/sync}} (keep the canvas and the code in step).

| Concern | `/spdd-analysis` | `/spdd-reasons-canvas` |
|---------|------------------|------------------------|
| Thinking level | Strategic: what and why | Tactical: how |
| Domain | Conceptual identification | Detailed entity modelling (E) |
| Solution | Direction and trade-offs | Concrete design (A, S) |
| Implementation | Out of scope | Ordered operations (O) |
| Standards | Out of scope | Norms and safeguards (N, S) |
| Risks | Identify and surface | Resolve through constraints |
