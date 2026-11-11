# Project profile

The profile is the full set of values the templates need. Fill it from the repository by reading the files that hold each value. Two kinds of slot exist:

- **Value slots** (`{{NAME}}`) are replaced with text.
- **Flag slots** (`{{#flag}}…{{/flag}}` and `{{^flag}}…{{/flag}}`) keep or drop a block. See [rendering.md](rendering.md).

## Discovery order

1. Read the agent rules doc first: `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `GEMINI.md`, `CONTRIBUTING.md`. It usually names the architecture, the check command, the test rules and the decision-record process.
2. Read the build manifests and tool configs: `Cargo.toml`, `package.json`, `pyproject.toml`, `go.mod`, `*.csproj`, `pom.xml`/`build.gradle`, lint configs, boundary tools (`arch-lint.toml`, `dependency-cruiser`, `import-linter`, ESLint boundaries), and task runners (`justfile`, `Makefile`, `package.json` scripts, `Taskfile`).
3. List the source tree two levels deep to learn the module layout.
4. Read 2–3 representative modules end to end to learn the real naming, error and test conventions.
5. Look for docs: spec or PRD, decision records (`docs/adr/`, `docs/decisions/`), design docs, domain references (standards, schemas, vendored specs).
6. Check the tracker with `git remote -v`, then `gh repo view` when the remote is GitHub.

## Value slots

| Slot | What it holds | Example (Cosmo) |
|------|---------------|-----------------|
| `PROJECT` | Project name | `Cosmo` |
| `STACK` | One line: language, build shape, architecture style | `a Rust feature-sliced Cargo workspace with clean architecture, strict clippy, arch-lint boundaries and behaviour-focused tests` |
| `RULES_DOC` | The canonical rules document | `AGENTS.md` |
| `FINGERPRINT_FILES` | Bullets: the few files read first to learn the project (manifest, lint and boundary configs), each with what to look at | `` - Root `Cargo.toml` (workspace members, `[workspace.dependencies]`, `[workspace.lints]`) `` |
| `SOURCE_DIRS` | Directories whose names list the modules (names only) | `` `crates/` and `crates/features/` `` |
| `UNIT` | What the project calls a deployable or compilable unit | `crate` |
| `ARCH_VOCAB` | The architecture vocabulary analyses must use | `crates, slices, layers (domain/application/adapters), ports, adapters, app orchestration and its phases, value objects` |
| `ARCH_RULES` | Bullets: dependency direction and boundary rules | `` - `core` ← {`shared`, `render`} ← slices ← `app`; inside a slice `domain` ← `application` ← `adapters` `` |
| `SCOPES` | Filename scopes: the main modules plus cross-cutting ones | `` `core`, `catalog`, `stock`, `sales`, `app`, or `workspace` / `tooling` `` |
| `DOMAIN_EXAMPLES` | Four bullets with real examples from this domain: domain nouns, action verbs, integration surfaces, technical hints | `"stock movement", "emit NFC-e", NFeAutorizacao4, "contingency"` |
| `DATAFLOW_EXAMPLE` | One real data-flow line | `UI message → app orchestrator → slice use cases in one local transaction → transmit phase → SEFAZ` |
| `CODE_SEARCH_EXAMPLES` | Type or module names to grep for, from this codebase | `` `struct StockMovement`, `trait StockLedger`, `mod cash` `` |
| `STEREOTYPES` | Mermaid stereotypes that fit the language and architecture | `<<entity>>`, `<<value>>`, `<<newtype>>`, `<<enum>>`, `<<trait port>>`, `<<error>>`, `<<message>>` |
| `ENTITY_RULES` | Bullets: modelling rules taken from the rules doc (wrapping primitives, field visibility, size limits, error types, cross-module access) | `- **≤ 4 fields per struct**: group the rest into value objects.` |
| `ENTITY_EXAMPLE` | A small Mermaid `classDiagram` (3–4 types) drawn from a real concept in this repo | see [example-cosmo.md](example-cosmo.md) |
| `APPROACH_SECTIONS` | The numbered headings of the Approach output, adapted to the architecture | `Domain design / Slice boundaries and flow / Error strategy / Persistence and integration / Test strategy / Decisions requiring ADRs` |
| `STRUCTURE_OUTPUT` | The `## Structure` output block: one line per layer or unit, then implementations, dependencies, boundary rules | see [example-cosmo.md](example-cosmo.md) |
| `OPERATION_ORDER` | The dependency order operations follow | `core value objects → domain → ports → use cases → adapters → app wiring → boundaries → docs → verify` |
| `OPERATIONS_EXAMPLE` | The `## Operations` output block: 3–5 typed example operations using real kinds of component in this repo | see [example-cosmo.md](example-cosmo.md) |
| `SIGNATURE_EXAMPLE` | One signature written in prose, in the project's language | `` `append(&self, movement: StockMovement) -> Result<(), StockError>` `` |
| `NORMS_BASELINE` | The first Norms line: which rules-doc sections apply in full | `` `AGENTS.md` sections 2–5 apply in full (Architecture, Object Calisthenics, Rust practices, Tests) `` |
| `NORMS_LINES` | Further Norms headings for this stack | `Error handling / Naming / Logging / Documentation / Tests` |
| `SAFEGUARD_LINES` | Numbered Safeguards categories for this project | `Functional / Fiscal / Architecture / Lints / Errors / Data / Performance / Security & privacy / Tests` |
| `CODING_NORMS` | Bullets that `spdd-generate` applies to every operation: the concrete coding rules of the rules doc, condensed | `- Newtypes with validating constructors; private fields; tell-don't-ask methods` |
| `TEST_NORMS` | Bullets: how tests are written here | `- Behaviour tests through public use cases/ports with in-memory fakes` |
| `CHECK_CMD` | The single command that must pass before work is done | `just check` |
| `CHECK_DESC` | What `CHECK_CMD` runs | `fmt-check, clippy with -D warnings, arch-lint, nextest` |
| `MAIN_BRANCH` | Default branch | `main` |
| `CANVAS_DIR` | Where canvases live | `spdd/prompt` |
| `ANALYSIS_DIR` | File mode only: where requirement and analysis files live | `spdd/analysis` |
| `ID` | The work-item ID that prefixes every canvas file name | `GH-<n>` in issue mode; `<slug>` in file mode |
| `REF` | How prose refers to the work item | `#<n>` in issue mode; `` `<slug>` `` in file mode |

## Flag slots

Turn a flag on only when the repository actually has the feature. A flag that is off drops its block entirely.

| Flag | On when | Extra value slots |
|------|---------|-------------------|
| `issue` | Decision D1 picked issue mode | `COMMIT_REF` (`Refs #<n>` / `Closes #<n>`) |
| `gate` | Decision D2: the rules doc sets a size threshold for SPDD | `GATE_RULE` (the rule as the rules doc states it), `GATE_READ` (exact steps or commands to read the size), `GATE_SECTION` (where it is stated) |
| `taxonomy` | The rules doc requires labels, milestone or parent on issues | `TAXONOMY_RULE` (fields to check and how) |
| `exempt` | The rules doc exempts some kinds of work from SPDD (for example spikes) | `EXEMPT_RULE` |
| `board` | A project board status has to be moved by hand when the analysis starts, or by a command after PR or merge | `BOARD_START`, `BOARD_AFTER` |
| `ephemeral` | Decision D3: canvases are gitignored working files | none |
| `sync` | Decision D3: generate `spdd-sync` (on for committed canvases; on for ephemeral ones only when the rules doc gives sync a role) | none |
| `spec` | A spec or PRD with decisions and non-goals exists | `SPEC_DOC` |
| `adr` | Decision records exist | `ADR_INDEX` (the index or directory), `ADR_NEW` (how to create one) |
| `design` | A design-docs directory exists | `DESIGN_DIR` |
| `schema` | Schema files or migrations exist | `SCHEMA_GLOB`, `SCHEMA_RULE` (for example "append-only: new migration, never edit one") |
| `domainrefs` | Authoritative domain references are vendored (standards, XSDs, protocol specs) | `DOMAIN_REFS` (path and what they govern) |
| `zerolint` | The rules forbid lint suppressions | `LINT_SUPPRESSIONS` (the forms that are forbidden), `LINT_GREP` (a command that must print nothing) |
| `deps` | Dependencies have a rule (central version table, exact pins, approval) | `DEPS_RULE` |
| `memory` | A memory tool is configured for agents (MCP server or similar) | `MEMORY_TOOLS` (tool names), `MEMORY_RULE` (what the rules doc allows it to write) |
| `mdlint` | A markdown linter is configured | `MDLINT_CMD` |

## The profile file

The profile is a JSON file that [scripts/render.py](../scripts/render.py) reads. Write it to a scratch location (never into the target repo by hand); the script records the final copy itself.

```json
{
  "flags": { "issue": true, "gate": false, "ephemeral": true, "sync": false, "adr": true, "...": false },
  "values": {
    "PROJECT": "Acme",
    "CHECK_CMD": "pnpm check",
    "FINGERPRINT_FILES": [
      "- Read the root `package.json` (workspaces, scripts)",
      "- Read `eslint.config.js` (boundary rules)"
    ]
  }
}
```

- Declare **every** flag as `true` or `false`; the script rejects missing or unknown flags.
- A value is a string, or a list of lines for multi-line slots (bullets, diagrams, output blocks).
- Write multi-line values **unindented**. The script indents them to where the slot sits in the template.
- Values of flags that are off may be left out.
- Every `description` is a double-quoted YAML string, so values used in it (`PROJECT`) cannot contain `"`.

## Filling the example slots

`ENTITY_EXAMPLE`, `OPERATIONS_EXAMPLE`, `STRUCTURE_OUTPUT`, `DOMAIN_EXAMPLES` and `CODE_SEARCH_EXAMPLES` must come from a real concept in this repo, not from Cosmo. Pick a small, typical feature and draw it as the canvas would. Agents copy the shape of these examples, so an example taken from another stack teaches the wrong layers.
