# Worked example: Cosmo

This is how the larger slots were filled for Cosmo, a Rust feature-sliced Cargo workspace (point-of-sale and NFC-e fiscal emission) with clean architecture, strict clippy and arch-lint boundaries. Copy the **shape**, never the content: a different stack has different layers, stereotypes and component kinds.

Cosmo decisions: D1 issue mode, D2 gate (Effort 5 or more, from the GitHub Project) plus a spike exemption, D3 ephemeral with `sync` on, because Cosmo's rules doc gives `spdd-sync` a role while the branch is open, D4 `.agents/skills/` mirrored to `.claude/commands/`.

## `ENTITY_EXAMPLE`

```text
classDiagram
direction TB

class StockMovement {
    <<entity>>
    -MovementId id
    -ProductId product
    -Quantity quantity
    -MovementKind kind
    +record(...) Result~StockMovement, StockError~
}

class Quantity {
    <<newtype>>
    -i64 value
    +parse(raw) Result~Quantity, QuantityError~
}

class MovementKind {
    <<enum>>
    Sale
    Receipt
    Adjustment
}

class StockLedger {
    <<trait port>>
    +append(movement) Result~(), StockError~
}

StockMovement "1" --> "1" Quantity
StockMovement "1" --> "1" MovementKind
StockLedger ..> StockMovement : persists
```

## `ENTITY_RULES`

```text
- **Primitives are wrapped**: domain fields are newtypes/value objects, never bare `String`/`i64`/`f64`/`bool`. Money is integer cents.
- **Fields are private** (`-`), behaviour is public (`+`). No getters/setters; model tell-don't-ask methods.
- **≤ 4 fields per struct**: group the rest into value objects.
- **Errors are types**: one `<<error>>` enum per layer boundary with its variants.
- **Cross-slice needs are ports**: a slice that needs another slice models a `<<trait port>>` owned by itself, never a type from the other slice.
- **Boundary shapes** (SEFAZ XML, CSV rows, UI messages) are modelled only where they cross an adapter.
- **Groupings are named and justified**: every Operation that introduces a grouping type (value object, service struct, command, context) names it and the step of the parameter ladder (`AGENTS.md` section 3) that justifies it. A function never takes a 4th parameter (a 3rd beside `self`), a tuple, or a struct named `*Args`, `*Params`, `*Dto`, `*Data`, `*Info` or `*Bag`.
```

## `APPROACH_SECTIONS`

```text
1. Domain design:
   - [Aggregates, invariants, state machines; key decisions and rationale]
2. Slice boundaries and flow:
   - [Which slice owns what; ports declared; how app wires them]
   - [Transactions and orchestration phases; idempotency and crash recovery]
3. Error strategy:
   - [Error enums per layer; adapter → application mapping; what reaches the UI]
4. Persistence and integration:
   - [Tables/migrations, external adapters, rendering]
5. Test strategy:
   - [Behaviour tests per use case with fakes; contract suites; XSD validation]
6. Decisions requiring ADRs:
   - [Any new architectural choice → new ADR, or "None"]
```

## `STRUCTURE_OUTPUT`

```text
## Structure

### Crates and modules
1. `cosmo-core` — [new/changed value objects]
2. `cosmo-<slice>::domain` — [entities, invariants]
3. `cosmo-<slice>::application` — [use cases, ports]
4. `cosmo-<slice>::adapters` — [port implementations]
5. `cosmo` (app) — [wiring, UI screens/messages]

### Trait implementations
1. `TursoStockLedger` implements `StockLedger`
2. `InMemoryStockLedger` implements `StockLedger` (test fake)

### Dependencies
1. [Use case] depends on [ports]
2. [App wiring] provides [adapter] for [port]
3. New crate dependencies: [crate = exact version, which crate uses it] or "None"

### Boundary rules
1. [arch-lint scopes/rules to add or confirm]
```

## `OPERATIONS_EXAMPLE`

```text
## Operations

### 1. Create value object - `Quantity` (`cosmo-core`)
1. Responsibility: [what it guarantees]
2. Representation: [private inner type and invariants]
3. Constructors: `parse(raw: i64) -> Result<Quantity, QuantityError>` — [validation rules]
4. Behaviour: [methods, each with purpose and signature in prose]
5. Tests: [behaviour cases, named as behaviour]

### 2. Define port - `StockLedger` (`cosmo-stock::application`)
1. Contract: [methods, errors, guarantees such as append-only]
2. Contract test suite: [cases every adapter must pass]

### 3. Implement use case - `RecordSale` (`cosmo-sales::application`)
1. Input: [command type]
2. Steps: [ordered logic, early returns, invariants]
3. Errors: [error enum variants and when]
4. Transaction: [what commits together; idempotency and crash recovery]
5. Tests: [behaviour tests with fakes]

### 4. Implement adapter - `TursoStockLedger` (`cosmo-stock::adapters`)
1. Implements: [port]
2. Migration: [new migration, schema in prose]
3. Error mapping: [adapter error → application error]
4. Tests: [runs the port contract suite]

### 5. Wire in app
### 6. Update boundaries - `arch-lint.toml`
### 7. Docs - ADR(s) via `just adr`, design doc
### 8. Verify - `just check`
```

## `SAFEGUARD_LINES`

```text
1. Functional: [invariants with exact conditions]
2. Fiscal: [XSD validity, numbering never reused, contingency — cite XSD/NT]
3. Architecture: [no slice-to-slice deps; layer rules; arch-lint rules]
4. Lints: [clippy/arch-lint pass with zero exceptions; clippy.toml thresholds]
5. Errors: [exact error enum variants and Display messages]
6. Data: [append-only tables, money in cents, validation rules]
7. Performance: [measurable limits]
8. Security & privacy: [secrets in keyring only; no personal data in logs]
9. Tests: [required behaviour tests and contract suites; no mock call-count assertions]
```

## `CODING_NORMS`

```text
- Newtypes with validating constructors; private fields; tell-don't-ask methods
- One level of indentation per function (early returns, `?`, `let ... else`); functions ≤ 25 lines, ≤ 3 parameters counting `self`; files ≤ 250 lines; ≤ 4 fields per struct
- `thiserror` error enums per layer boundary; no `unwrap`/`expect`/`panic!`/indexing/`as` outside tests
- `#[must_use]` on constructors and pure functions; `///` docs on public items
- `tracing` for logs; never log secrets or personal data
- New dependencies only via `[workspace.dependencies]` with exact versions
- No parameter workarounds: a 4th parameter is never solved with a tuple or a bag-named struct; take the first fitting step of the ladder in `AGENTS.md` section 3
```

## Gate, board and memory values

- `GATE_RULE`: `AGENTS.md` section 8 gives SPDD artifacts to an issue with Effort 5 or more only.
- `GATE_READ`: find the Project titled "Cosmo" with `gh project list --owner <owner> --format json`, then `gh project item-list <number> --owner <owner> --limit 1000 --format json`, and take the item for `<n>`. A missing `project` scope is fixed with `gh auth refresh -s project`.
- `BOARD_START`: starting the analysis moves the card to In progress by hand (`just project-sync` never does that).
- `BOARD_AFTER`: run `just project-sync --dry-run`, then `just project-sync`, after opening the PR (→ In review) and after the merge (→ Done).
- `MEMORY_TOOLS`: `ai-memory` `memory_query`, `memory_recent`. `MEMORY_RULE`: durable writes only on request, into `gotchas/`.
