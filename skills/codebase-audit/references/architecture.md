# Architecture & Design Review (ARCH-*)

The architecture reviewer looks at the **shape** of the system: directory/module structure,
dependency direction, boundaries, and where responsibilities live. It reads the tree, manifests,
entry points and import graphs — not every line.

## How to review

1. **Find the intended architecture first.** Read README, `docs/`, ADRs, top-level folder names,
   workspace manifests. Note the declared style (layered, hexagonal/clean, feature-sliced, MVC,
   microservices, modular monolith, library). Judge the code against its *own* declared intent
   before judging it against an ideal; mismatch between intent and reality is itself a finding
   (ARCH-002).
2. **Map the modules and dependency direction.** Use imports (`grep -rE "^(use|import|from) "`,
   `use crate::`, `from '...'`) to sketch which modules depend on which. Look for cycles and arrows
   pointing the wrong way (domain → infrastructure).
3. **Trace one or two core use cases end to end** (e.g. "create order": route → handler → service →
   repository → DB). Note every place business rules live along the way.
4. **Check the seams**: where does IO happen, where is validation, where are transactions, where is
   configuration read, how are dependencies wired (DI container, constructor injection, globals)?
5. Record findings with the IDs below; add a short "architecture as found" description for the
   report (3–6 sentences, optionally a mermaid diagram of the main modules and dependency arrows).

## Principles and checks

| ID | Principle | What to look for | Sev |
|---|---|---|---|
| ARCH-001 | **Clear, documented structure.** A newcomer can tell where code for a feature goes. | No discernible organizing principle; mixed by-type and by-feature folders without reason. | medium |
| ARCH-002 | **Code matches the declared architecture.** | Docs say "hexagonal" but adapters are imported from the domain; layers bypassed. | medium |
| ARCH-003 | **Dependency rule**: dependencies point inward toward the domain/stable core; the core imports no framework/IO. | Domain/entities importing ORM, HTTP framework, UI, env. | high |
| ARCH-004 | **No dependency cycles** between modules/packages/crates. | Mutual imports; barrel files creating cycles. | medium |
| ARCH-005 | **Business logic lives in a domain/application layer**, not in controllers, route handlers, UI components, or SQL. | Fat handlers/components; pricing rules inside React components or route files; logic in stored procedures without tests. | high |
| ARCH-006 | **Thin adapters at the edges** (HTTP, CLI, queue consumers, UI) that translate and delegate. | Handlers doing validation + business + persistence + formatting. | medium |
| ARCH-007 | **Explicit ports/interfaces at IO boundaries**, so the core can be tested without infrastructure. | Core calls concrete clients; tests need a real DB/network for business rules. | medium |
| ARCH-008 | **Composition root**: dependencies wired in one place at startup. | `new Client()` / global singletons constructed deep inside modules. | low |
| ARCH-009 | **Feature/bounded-context boundaries**: modules own their data and expose an API; others don't reach into their tables or internals. | Cross-module DB table access; shared "models" package everyone mutates. | medium |
| ARCH-010 | **Shared/common code is small and stable**, not a dumping ground. | `utils/`, `common/`, `shared/`, `helpers/` that is large and imported by everything. | medium |
| ARCH-011 | **Consistent cross-cutting concerns**: auth, logging, error mapping, validation implemented once (middleware/decorators/layers). | Each handler re-implements auth checks or error formatting. | medium |
| ARCH-012 | **Separation of read and write models where complexity warrants** (not mandatory; flag only when queries are contorting the domain model). | Domain entities bent to serve reporting queries. | info |
| ARCH-013 | **Monorepo/workspace hygiene**: packages have clear purpose, explicit dependencies, no deep cross-package relative imports. | `../../other-package/src/...` imports; hidden coupling through root deps. | medium |
| ARCH-014 | **Appropriate distribution**: services split along business capabilities, not technical layers; no distributed monolith. | Services that must deploy together; chatty synchronous calls for every request; shared DB between services. | high |
| ARCH-015 | **Configuration and environment isolated at the edge** (see GEN-100). | Env reads scattered through modules. | low |
| ARCH-016 | **Error-handling strategy is uniform**: domain errors mapped to transport errors in one place. | Each layer invents its own error shapes. | medium |
| ARCH-017 | **Extensibility points are deliberate**: plugin/strategy patterns only where variation actually exists. | Frameworks-within-the-framework for a single use. | low |
| ARCH-018 | **Consistent patterns**: one way to do data fetching, state management, DI, etc. | Three state libraries; two ORMs; mixed callback/promise/async styles. | medium |
| ARCH-019 | **Testability is designed in**: core logic can be unit tested in isolation; integration seams exist. | Testing anything requires booting the whole app. | medium |
| ARCH-020 | **Scalability/operability assumptions are explicit**: statelessness of app servers, idempotent jobs, where state lives. | In-memory sessions/caches in horizontally scaled services; cron jobs that break if two instances run. | medium |

## Common architecture styles — quick reference

- **Layered (n-tier)**: presentation → application → domain → infrastructure. Watch for "sinkhole"
  layers that only pass calls through, and for skipping layers.
- **Hexagonal / Ports & Adapters / Clean / Onion**: domain at the center defines ports (interfaces);
  adapters implement them. The test: can you run the domain's tests with no framework installed?
- **Feature-sliced / vertical slices**: each feature folder holds its UI, logic and data access.
  Watch for slices importing each other's internals instead of a public API.
- **Modular monolith**: modules with enforced boundaries inside one deployable. Check for a
  boundary-enforcement mechanism (eslint `no-restricted-imports`, dependency-cruiser, Rust crate
  visibility/workspace crates, Nx module boundaries).
- **Microservices**: independent deployability, own data, async where possible. Flag distributed
  monolith signs (ARCH-014).
- **Library/crate**: small public API, internal modules private, semver discipline, no global state,
  no logging/printing to stdout by default, feature flags for optional deps.

## Suggested tooling to recommend (when missing and the project is large enough)

- TS/JS: `dependency-cruiser` or `eslint-plugin-boundaries` / Nx `enforce-module-boundaries`,
  `madge --circular`, `knip` (unused files/exports/deps).
- Rust: workspace crates for hard boundaries, `cargo-modules` for module graphs, `cargo-udeps`
  (unused deps), `cargo-deny` (deps policy).
- Architecture fitness functions: tests that assert dependency rules (e.g. ArchUnit-style checks).
