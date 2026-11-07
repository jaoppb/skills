# Generic Software-Engineering Practices (GEN-*)

Language-agnostic practices every reviewer applies. Language, framework and library files refine
these; when they conflict, the more specific file wins.

**Columns**
- **Practice** — what good looks like.
- **Check** — how a reviewer detects a violation without running the code.
- **Sev** — default severity when violated (see the rubric in `finding-format.md`); adjust for context.

Deeper catalogues: `code-smells.md` (SMELL-*), `architecture.md` (ARCH-*), `testing.md` (TEST-*),
`security.md` (SEC-*). This table links to them rather than repeating them.

## Contents
1. Design & modularity
2. Readability & naming
3. Functions & control flow
4. Error handling
5. State, data & immutability
6. Concurrency
7. Performance & resources
8. API & interface design
9. Persistence & data integrity
10. Configuration & environments
11. Observability
12. Dependencies & supply chain
13. Testing (summary)
14. Security (summary)
15. Tooling, CI & automation
16. Version control & collaboration
17. Documentation
18. UI-facing code (when applicable)

---

## 1. Design & modularity

| ID | Practice | Check | Sev |
|---|---|---|---|
| GEN-001 | **Single Responsibility**: each module/class/function has one reason to change. | Names joined with "And"/"Manager"/"Utils"/"Helper"; files mixing IO, business rules and formatting; >1 unrelated reason a change would touch the file. | medium |
| GEN-002 | **High cohesion, low coupling**: things that change together live together; modules depend on few, stable others. | Feature changes would touch many directories; import fan-out > ~15 for a non-entrypoint; circular imports. | medium |
| GEN-003 | **Depend on abstractions at boundaries** (DIP): business logic doesn't import concrete DB/HTTP/FS clients directly. | Domain code importing ORM, SDK, `fetch`, `std::fs`, env vars. | medium |
| GEN-004 | **Open/closed for variation**: new variants added by extension, not by editing a growing switch. | `switch`/`match`/if-chains on a type tag repeated in several places (shotgun). | low |
| GEN-005 | **Liskov / interface honesty**: implementations honor the contract; no "not implemented" stubs. | Overrides that throw `NotImplemented`/`todo!()`/`unimplemented!()` in prod paths; subtype narrowing preconditions. | medium |
| GEN-006 | **Interface segregation**: consumers depend only on the methods they use. | Traits/interfaces with >~7 methods where implementors leave many no-ops. | low |
| GEN-007 | **Composition over inheritance**; inheritance depth ≤ 2–3. | Deep class hierarchies; base classes used only for code sharing. | low |
| GEN-008 | **DRY for knowledge, not for text**: one source of truth for each business rule; don't merge coincidentally similar code. | Same constant/regex/validation rule duplicated; or wrong abstraction with boolean flags to diverge behavior. | medium |
| GEN-009 | **YAGNI / KISS**: no speculative generality, plugin systems with one plugin, unused parameters. | Abstractions with a single implementation and no test double need; unused config knobs. | low |
| GEN-010 | **Explicit module public API**: internals are private; consumers import from the module's entry, not deep paths. | Deep imports into another module's internals; everything exported/`pub`. | low |
| GEN-011 | **No dead code**: unused functions, files, flags, commented-out blocks are removed (VCS keeps history). | Unreferenced exports; large commented blocks; feature flags permanently on/off. | low |

## 2. Readability & naming

| ID | Practice | Check | Sev |
|---|---|---|---|
| GEN-020 | **Intention-revealing names** in the domain's vocabulary (ubiquitous language). | `data`, `info`, `tmp`, `obj`, `handle2`, single letters outside tiny scopes; same concept named differently across modules. | low |
| GEN-021 | **Consistent conventions** (casing, file naming, folder structure) enforced by tooling. | Mixed `camelCase`/`snake_case` for the same kind of thing; mixed file naming schemes. | low |
| GEN-022 | **No magic numbers/strings**: named constants or enums with units in the name (`timeoutMs`). | Literal numbers in logic other than 0/1/-1; repeated string literals used as keys/states. | low |
| GEN-023 | **Comments explain why, not what**; no stale or lying comments. | Comments restating code; comments contradicting code; TODO/FIXME without owner or issue link. | low |
| GEN-024 | **Small files**: a file fits a reader's head (rule of thumb < 400–500 lines of non-generated code). | Inventory "largest files" list. | low |
| GEN-025 | **Formatter-enforced style**: one formatter, run in CI, no style debates in review. | No formatter config; formatter not in CI; diffs full of whitespace churn. | low |

## 3. Functions & control flow

| ID | Practice | Check | Sev |
|---|---|---|---|
| GEN-030 | **Short, focused functions** (guide: ≤ ~40 lines, one level of abstraction). | Long functions mixing high-level steps with low-level detail. | low |
| GEN-031 | **Low cyclomatic/cognitive complexity** (guide: cyclomatic ≤ 10, nesting ≤ 3). | Deep nesting, long if/else ladders, many early-continue branches. | medium |
| GEN-032 | **Few parameters** (≤ 3–4); group related ones into a value object/options struct. | Long parameter lists; repeated parameter clumps across functions. | low |
| GEN-033 | **No boolean flag arguments** that switch behavior. | `doThing(x, true)` call sites; functions with `if (flag)` splitting the body. | low |
| GEN-034 | **Guard clauses / early return** instead of arrow code. | `if (ok) { ... huge block ... } else { return err }`. | low |
| GEN-035 | **Command–query separation**: functions either change state or return data, and names say which. | `getX()` that writes, caches globally or sends requests with side effects. | medium |
| GEN-036 | **Pure core, impure shell**: computation separated from IO so it can be tested without mocks. | Business calculations interleaved with DB/HTTP calls. | medium |

## 4. Error handling

| ID | Practice | Check | Sev |
|---|---|---|---|
| GEN-040 | **Never swallow errors**: every catch/match either handles, adds context and rethrows, or reports. | Empty `catch {}`, `catch (e) { console.log(e) }` then continue, `let _ = fallible()`, `.ok()` discarding errors. | high |
| GEN-041 | **Errors carry context** (what operation, which input) and preserve the cause chain. | `throw new Error("failed")`; re-wrapping that drops `cause`/source. | medium |
| GEN-042 | **Typed/structured errors at module boundaries**, distinguishing expected (validation, not found) from unexpected (bugs, infra). | Stringly-typed errors; callers parsing error messages; one catch-all error type. | medium |
| GEN-043 | **Fail fast on invalid input and broken invariants**; validate at system edges, trust internally. | Validation scattered deep in the core; or no validation at the edge at all. | medium |
| GEN-044 | **No panics/crashes for recoverable conditions** in library and request paths. | `unwrap()`/`expect()`/`!` non-null assertions/`process.exit` on user-controlled input. | high |
| GEN-045 | **Resource cleanup on all paths** (finally/defer/RAII/using). | Files, connections, locks, timers not released on error paths. | medium |
| GEN-046 | **Retries are bounded, backed off, and only for idempotent operations.** | Infinite retry loops; retries on POST without idempotency keys; no jitter. | medium |
| GEN-047 | **User-facing errors are safe**: no stack traces, SQL or secrets in responses. | Error handlers returning `err.message`/`err.stack` to clients. | high |

## 5. State, data & immutability

| ID | Practice | Check | Sev |
|---|---|---|---|
| GEN-050 | **Prefer immutability**; mutate only where it's local and obvious. | Shared mutable objects passed around and modified by callees. | medium |
| GEN-051 | **No hidden global mutable state** (singletons, module-level caches) without clear ownership and lifecycle. | Module-level `let`/`static mut`/global maps mutated at runtime. | medium |
| GEN-052 | **Make illegal states unrepresentable**: use sum types/discriminated unions over flag combinations. | Objects with `isLoading`, `isError`, `data` booleans that can contradict; optional fields that are "required when X". | medium |
| GEN-053 | **Value objects for domain primitives** (money, email, ids) instead of bare strings/numbers. | Money as float; ids of different entities interchangeable as `string`. | medium |
| GEN-054 | **Correct numeric handling**: no floats for money, explicit rounding, overflow considered. | `price * 0.1` on floats; unchecked integer arithmetic on external input. | high |
| GEN-055 | **Time handled explicitly**: UTC storage, timezone-aware conversion, injectable clock. | `new Date()`/`SystemTime::now()` inside business logic; local-time storage; string date math. | medium |

## 6. Concurrency

| ID | Practice | Check | Sev |
|---|---|---|---|
| GEN-060 | **No data races**: shared state is synchronized or confined. | Shared mutation across threads/async tasks without locks/channels. | critical |
| GEN-061 | **No check-then-act races** on external state (TOCTOU). | `if (!exists) create`, read-modify-write without transaction/optimistic lock. | high |
| GEN-062 | **Locks are short and never held across await/IO**; consistent lock ordering. | Mutex guard alive across `.await`; nested locks in varying order. | high |
| GEN-063 | **Async work is awaited or deliberately detached with error handling.** | Floating promises; spawned tasks whose errors/results are ignored. | high |
| GEN-064 | **Bounded concurrency and backpressure**: no unbounded queues or `Promise.all` over unbounded input. | `Promise.all(items.map(fetch))` over user-sized arrays; unbounded channels. | medium |
| GEN-065 | **Timeouts and cancellation** on every network/IO call. | HTTP/DB clients without timeouts; no AbortSignal/cancellation token propagation. | medium |

## 7. Performance & resources

| ID | Practice | Check | Sev |
|---|---|---|---|
| GEN-070 | **No N+1 queries / calls in loops.** | DB/HTTP call inside a loop over a collection. | medium |
| GEN-071 | **Appropriate data structures and complexity** (no accidental O(n²) on large inputs). | Nested loops / `includes` / `find` inside loops over the same large collection. | medium |
| GEN-072 | **Pagination / streaming for unbounded data.** | Endpoints or queries returning entire tables; reading whole files into memory. | medium |
| GEN-073 | **Caching is explicit, bounded and invalidated.** | Unbounded in-memory maps used as caches; no TTL/eviction. | medium |
| GEN-074 | **No premature optimization** that hurts clarity without a measured need. | Hand-rolled micro-optimizations with no benchmark or comment justifying them. | info |
| GEN-075 | **Benchmarks or perf budgets exist for hot paths** (where performance matters). | Performance-critical code with no benchmark; no bundle/latency budget. | low |

## 8. API & interface design

| ID | Practice | Check | Sev |
|---|---|---|---|
| GEN-080 | **Contract-first, documented APIs** (OpenAPI/GraphQL schema/typed RPC), versioned. | Handlers with no schema; breaking changes without versioning. | medium |
| GEN-081 | **Validate and parse all inbound data at the boundary** into typed structures. | Request bodies used as untyped/any; no schema validation. | high |
| GEN-082 | **Consistent conventions**: resource naming, status codes, error envelope, pagination shape. | Mixed error formats; 200 with `{error}`; inconsistent casing between endpoints. | low |
| GEN-083 | **Idempotency for retried mutations** (idempotency keys, PUT semantics). | Payment/creation endpoints with no protection against double submit. | high |
| GEN-084 | **Least surprise**: functions do what their names and types say; no hidden side effects. | Getters with side effects; functions returning different shapes based on input. | medium |
| GEN-085 | **Backward compatibility** for public libraries: semver respected, deprecations before removals. | Public API changes in minor/patch versions; no CHANGELOG. | medium |

## 9. Persistence & data integrity

| ID | Practice | Check | Sev |
|---|---|---|---|
| GEN-090 | **Schema changes via versioned, reviewed migrations**; reversible where possible. | Manual SQL in README; ORM `sync`/auto-migrate in production. | high |
| GEN-091 | **Constraints in the database** (NOT NULL, FK, UNIQUE, CHECK), not only in app code. | Uniqueness checked only in code; nullable everything. | medium |
| GEN-092 | **Transactions around multi-step writes.** | Several dependent writes without a transaction. | high |
| GEN-093 | **Parameterized queries only** (see SEC-010). | String-concatenated SQL. | critical |
| GEN-094 | **Indexes for query patterns**; no unbounded scans on hot paths. | Filters/sorts on unindexed columns in frequent queries (if schema visible). | medium |
| GEN-095 | **Repository/data-access layer isolates the ORM/driver** from domain logic. | ORM models used as API responses and domain objects everywhere. | low |

## 10. Configuration & environments

| ID | Practice | Check | Sev |
|---|---|---|---|
| GEN-100 | **Config from environment, validated at startup** into a typed config object (12-factor). | `process.env.X`/`env::var` read deep in code; no validation; crashes far from startup. | medium |
| GEN-101 | **No secrets in the repo** (code, configs, tests, history). | Keys/tokens/passwords in files; `.env` committed (see SEC-001). | critical |
| GEN-102 | **`.env.example` (or equivalent) documents every required variable.** | Required vars only discoverable by reading code. | low |
| GEN-103 | **Dev/prod parity**; environment differences are config, not code branches. | `if (env === "production")` logic scattered through business code. | low |
| GEN-104 | **Feature flags have owners and expiry.** | Stale flags; flags read in many places without central definition. | low |

## 11. Observability

| ID | Practice | Check | Sev |
|---|---|---|---|
| GEN-110 | **Structured logging** with levels, through one logger, no `print`/`console.log` in prod paths. | `console.log`/`println!` in services; logs as free-text concatenation. | low |
| GEN-111 | **No sensitive data in logs** (PII, tokens, passwords, full request bodies). | Logging whole request/user objects or headers. | high |
| GEN-112 | **Correlation/trace IDs** propagated across requests and async boundaries (services). | No request id in logs; no tracing middleware. | low |
| GEN-113 | **Metrics and health checks** for services (liveness/readiness, RED/USE metrics). | No `/health`; no metrics for latency/errors. | low |
| GEN-114 | **Errors reported to an error tracker** with context. | Unhandled rejections/panics not captured. | low |

## 12. Dependencies & supply chain

| ID | Practice | Check | Sev |
|---|---|---|---|
| GEN-120 | **Lockfile committed** and used in CI (`npm ci`, `cargo build --locked`). | Missing lockfile; CI uses `npm install`. | medium |
| GEN-121 | **No known-vulnerable dependencies** (audit tooling in CI). | `npm audit`/`cargo audit` findings; no audit step. | high (if exploitable) |
| GEN-122 | **Automated updates** (Dependabot/Renovate) and reasonably current major versions. | Dependencies several majors behind; no update bot. | low |
| GEN-123 | **Minimal dependencies**: no packages for trivial functions; no duplicates doing the same job. | Two date libs, two HTTP clients, `left-pad`-style deps. | low |
| GEN-124 | **Runtime vs dev dependencies separated.** | Test/build tools in production dependencies. | low |
| GEN-125 | **Licenses compatible** with the project's license. | Copyleft deps in proprietary distributables (flag for human review). | medium |
| GEN-126 | **Pinned toolchain** (`rust-toolchain.toml`, `.nvmrc`/`engines`, `packageManager`). | Builds depend on whatever is installed locally. | low |

## 13. Testing (summary — details in `testing.md`)

| ID | Practice | Check | Sev |
|---|---|---|---|
| GEN-130 | A **test suite exists, runs in CI, and blocks merges**. | No tests; tests not in CI; CI allowed to fail. | high |
| GEN-131 | **Balanced test portfolio** (many fast unit tests, fewer integration, few E2E). | Only E2E; or only unit tests with heavy mocks and no integration. | medium |
| GEN-132 | **Critical paths covered** (auth, payments, data writes, core domain rules). | No tests near the most important modules. | high |
| GEN-133 | **Tests are deterministic, isolated, readable** (AAA, one behavior each, no sleeps). | See TEST-0xx. | medium |

## 14. Security (summary — details in `security.md`)

| ID | Practice | Check | Sev |
|---|---|---|---|
| GEN-140 | **Input validation and output encoding** at every trust boundary. | See SEC-01x. | high |
| GEN-141 | **Authentication and authorization enforced server-side on every protected operation.** | See SEC-02x. | critical |
| GEN-142 | **Secrets managed outside code**; rotation possible. | See SEC-001. | critical |
| GEN-143 | **Least privilege** for tokens, DB users, CI permissions, containers. | See SEC-05x. | medium |

## 15. Tooling, CI & automation

| ID | Practice | Check | Sev |
|---|---|---|---|
| GEN-150 | **CI runs on every PR**: build, lint, type-check, tests, audit. | Missing CI config; jobs missing one of these. | high |
| GEN-151 | **Linter configured with a strict, shared ruleset**, warnings treated as errors in CI. | No linter config; many disable comments; warnings ignored. | medium |
| GEN-152 | **Type checking enforced in CI** (for typed languages / TS). | `tsc` not in CI; `skipLibCheck` hiding real issues is fine, `noEmit` check absent is not. | medium |
| GEN-153 | **Reproducible, one-command setup** (`make dev`, `npm run dev`, devcontainer, docker compose). | README setup is long manual steps. | low |
| GEN-154 | **Pre-commit hooks** for fast checks (format, lint-staged) — optional but helpful. | None; or hooks that are slow and get skipped. | info |
| GEN-155 | **Build artifacts and generated code** are either committed deliberately (and marked) or generated in CI, never both. | Generated files edited by hand; stale generated code. | low |
| GEN-156 | **CI is fast and cached**; flaky jobs are tracked, not retried forever. | Long CI with no caching; `retry: 3` on tests. | low |
| GEN-157 | **Release process automated** (versioning, changelog, tags). | Manual version bumps; no CHANGELOG. | low |

## 16. Version control & collaboration

| ID | Practice | Check | Sev |
|---|---|---|---|
| GEN-160 | **Meaningful `.gitignore`**; no build output, dependencies, IDE files or env files tracked. | `node_modules`, `target/`, `.env`, `.DS_Store` in repo. | medium |
| GEN-161 | **Large binaries not in git** (use LFS/artifact storage). | Big media/archives in tree. | low |
| GEN-162 | **Code ownership and review rules** (`CODEOWNERS`, branch protection) for team repos. | No CODEOWNERS in multi-team repo (can't verify branch protection — note as assumption). | info |
| GEN-163 | **PR/issue templates** guide contributors (team/OSS repos). | Absent in active collaborative repos. | info |

## 17. Documentation

| ID | Practice | Check | Sev |
|---|---|---|---|
| GEN-170 | **README** explains what it is, how to run, test, configure and deploy. | Missing sections; outdated commands. | low |
| GEN-171 | **Architecture overview and decisions** recorded (diagram, ADRs) for non-trivial systems. | No docs on how components fit; decisions only in people's heads. | low |
| GEN-172 | **Public APIs documented** (doc comments / generated docs). | Exported functions/types in libraries without docs. | low |
| GEN-173 | **CONTRIBUTING / coding conventions** for team or OSS projects. | Conventions implicit. | info |
| GEN-174 | **Docs live next to code and are updated with it.** | Docs referencing removed files/commands. | low |

## 18. UI-facing code (when applicable)

| ID | Practice | Check | Sev |
|---|---|---|---|
| GEN-180 | **Accessibility**: semantic elements, labels, keyboard support, focus management, contrast (WCAG 2.2 AA). | `div` buttons, images without alt, inputs without labels. | medium |
| GEN-181 | **Internationalization-ready** when the product needs it: no hard-coded user-facing strings, locale-aware formatting. | Concatenated sentences; manual date/number formatting. | low |
| GEN-182 | **Performance budgets** (bundle size, Core Web Vitals) tracked. | No budgets; huge client bundles. | low |
| GEN-183 | **Loading, empty and error states** handled for every async view. | Views that render nothing or crash on error/empty data. | medium |
