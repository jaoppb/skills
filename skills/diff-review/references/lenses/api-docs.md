# API & Docs Lens

- **Role**: Developer Experience (DX) & Contracts Engineer — public API/CLI/schema contracts, error messages, and documentation sync.
- **Tier**: `fast/balanced`
- **Activation Trigger**: Diff modifies public HTTP/RPC/GraphQL endpoints, CLI flags/commands, SDK exports, request/response/config schemas, error formats, or code-to-docs contract sync (`README.md`, `AGENTS.md`, or migration/changelog docs describing public interfaces). Stay off for purely internal implementation changes or pure prose/editorial docs with no public API/CLI/schema contract surface (handled by `docs-quality`).
- **Delta Re-run Invalidation**:
  - Public API routes/controllers, OpenAPI/GraphQL/Protobuf schemas, CLI parsers, exported package entrypoints
  - `README.md`, `AGENTS.md`, `docs/**`, `CHANGELOG*`, migration guides
  - *Conservative fallback*: re-run whenever uncertain whether a fix changed a public contract, error message, or documented behavior.

## Check

- **Breaking contract changes**: Did any public endpoint, CLI flag, exported function signature, or schema field change in a backward-incompatible way without versioning or migration notes?
- **Contract consistency**: Are naming, status codes, pagination envelopes, and error shapes consistent with the rest of the project?
- **Actionable error messages**: Do user/caller-facing errors explain *what* failed and *how* to fix it, without leaking internal stack traces?
- **Docs & catalog sync**: Are `README.md`, `AGENTS.md`, inline docstrings, examples, and relative links updated to match the code changes? Do all relative links resolve cleanly?

## Presumptive Blockers

- **`blocker` (P0)**: Unintended breaking change to a public API/CLI/schema contract, or broken relative links / inaccurate installation/usage docs that break callers.
- **`material` (P1)**: Undocumented new public flag/endpoint/config, inconsistent error contract, or stale `README.md`/`AGENTS.md` out of sync with the diff.
