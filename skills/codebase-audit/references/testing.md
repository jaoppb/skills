# Testing Practices (TEST-*)

## Contents
1. How the testing reviewer works
2. Strategy & portfolio
3. Test types — what each is for
4. Test design techniques (AAA, boundaries, partitions, properties…)
5. Test doubles
6. Test smells
7. Integration & E2E specifics
8. Coverage, mutation testing & CI

---

## 1. How the testing reviewer works

1. **Map tests to code.** From the inventory, list source modules and the test files that exercise
   them (co-located `*.test.ts`, `__tests__/`, Rust `#[cfg(test)] mod tests`, `tests/` integration
   dir, `e2e/`, `playwright/`, `cypress/`). Produce a table: module → unit? integration? e2e?
2. **Find the gaps that matter.** Rank untested or weakly tested modules by criticality (auth,
   payments, data writes, core domain rules, parsing of external input) and by complexity/churn.
   Missing tests on critical code is a high-severity finding; missing tests on a trivial getter is
   not worth filing.
3. **Sample test quality.** Read a representative sample (at least ~10 tests, more in big suites;
   always include tests of the most critical modules). Check them against §4–§6.
4. **Check the harness.** Test runner config, CI job, coverage config/thresholds, test data
   strategy (fixtures/factories), isolation (DB reset, mocks reset), parallelism, flakiness markers
   (`retry`, `.skip`, `#[ignore]`, `test.fixme`).
5. **Report** portfolio shape (rough counts per type), gaps, and quality issues as findings.

## 2. Strategy & portfolio

| ID | Practice | Check | Sev |
|---|---|---|---|
| TEST-001 | **Tests exist and run in CI on every PR; failures block merge.** | No test script; CI doesn't run tests; `continue-on-error`. | high |
| TEST-002 | **Healthy shape**: many fast unit tests for logic, a meaningful layer of integration tests for IO seams, a thin layer of E2E for critical journeys (pyramid; for UI-heavy apps a "testing trophy" weighted to integration/component tests is also fine). | Only E2E (slow, flaky, poor localization); or only mocked units (false confidence). | medium |
| TEST-003 | **Critical paths and business rules are covered.** | No tests touching auth, payments, permissions, money math, core state transitions. | high |
| TEST-004 | **Regression test accompanies each bug fix.** | Fix commits/PRs with no test (check history if available; otherwise note as recommendation). | low |
| TEST-005 | **Tests are first-class code**: same lint/type rules, refactored, reviewed. | Tests excluded from lint/tsc; `any` everywhere in tests; giant copy-pasted setups. | low |
| TEST-006 | **Fast feedback**: unit suite runs in seconds–a minute; slow tests are separated and tagged. | Unit tests hitting network/DB; whole suite only runnable as one slow job. | medium |

## 3. Test types — what each is for

Reviewers use this to judge whether the right kind of test exists for each risk.

| Type | Purpose | Good signs | Common misuse |
|---|---|---|---|
| **Unit** | Verify a unit of behavior (function/class/module) in isolation, in ms. | Pure inputs → outputs; no IO; doubles only at true boundaries. | Mocking every collaborator so the test mirrors the implementation. |
| **Integration** | Verify components work together across a real seam (DB, queue, HTTP, FS). | Real DB in a container/ephemeral instance; transaction rollback or truncation between tests. | Called "integration" but everything mocked; or sharing state across tests. |
| **Contract** | Verify a provider and consumer agree on an API (Pact, schema tests, OpenAPI validation). | Consumer-driven contracts in multi-service systems. | Absent in microservices → breakages found only in staging. |
| **Component (UI)** | Render a component with real children, interact like a user, assert on visible output. | Testing Library queries by role/label; user-event. | Asserting on internal state or implementation details. |
| **End-to-end** | Verify a critical user journey through the deployed stack. | A handful of journeys (login, checkout); stable selectors; seeded data. | Hundreds of E2E tests duplicating unit coverage; sleeps. |
| **Snapshot** | Detect unintended changes in serialized output. | Small, focused snapshots; reviewed when updated; inline snapshots. | Huge snapshots blindly updated with `-u`. |
| **Property-based** | Check invariants across generated inputs (proptest/quickcheck, fast-check). | Round-trip (encode/decode), idempotence, ordering, algebraic laws. | Absent for parsers, serializers, and math-heavy code where it shines. |
| **Fuzz** | Find crashes/UB on arbitrary input (cargo-fuzz, jazzer.js). | Targets for parsers and untrusted-input handlers. | Absent on security-sensitive parsing. |
| **Mutation** | Measure whether tests detect injected bugs (cargo-mutants, Stryker). | Used periodically on core modules to find assertion-weak tests. | — (rarely present; recommend for core logic). |
| **Performance / load** | Verify latency/throughput budgets (criterion, k6). | Benchmarks for hot paths; budgets in CI. | Micro-benchmarks with no baseline. |
| **Smoke** | Quick check that a deployment is alive. | Post-deploy health checks. | — |
| **Doc tests / examples** | Keep documentation examples compiling (Rust doctests). | Public API examples tested. | — |

| ID | Practice | Check | Sev |
|---|---|---|---|
| TEST-010 | **Each IO seam has integration tests** (DB queries/repositories, external API clients with recorded or fake servers, message handlers). | Repositories only tested via mocks of the ORM. | medium |
| TEST-011 | **Multi-service/API-consumer systems have contract or schema tests.** | Client and server types drift; no shared schema validation. | medium |
| TEST-012 | **Critical user journeys have E2E coverage** (few, stable). | No E2E at all for a product with login/checkout; or E2E only. | low–medium |
| TEST-013 | **Parsers, serializers, and algorithmic code have property-based or table-driven tests.** | Single happy-path example tests on complex input handling. | low |
| TEST-014 | **Untrusted-input parsers have fuzz targets** (security-relevant code). | No fuzzing of file/protocol parsers. | low |

## 4. Test design techniques

### 4.1 Structure: Arrange–Act–Assert (Given–When–Then)

```text
// Arrange — build inputs and the system under test (SUT)
// Act     — exactly one action on the SUT
// Assert  — verify outcome (return value, state, or observable interaction)
```

| ID | Practice | Check | Sev |
|---|---|---|---|
| TEST-020 | **AAA structure is visible**: setup, single act, assertions — separated (blank lines or comments). | Acts and asserts interleaved; multiple acts per test. | low |
| TEST-021 | **One behavior per test** (may have several asserts about that one behavior). | Tests named `test_everything`, `works`, or asserting unrelated outcomes. | low |
| TEST-022 | **Descriptive names state scenario and expectation**: `returns 404 when order does not exist`, `rejects_negative_quantity`. | `test1`, `should work`, `handles case`. | low |
| TEST-023 | **Test behavior through the public API, not implementation details.** | Tests reaching into private fields, asserting call order of internals, breaking on every refactor. | medium |
| TEST-024 | **Assertions are specific and meaningful.** | `expect(result).toBeTruthy()`, `assert!(res.is_ok())` without checking value; tests with no assertions. | medium |
| TEST-025 | **Assert on outcomes before interactions**: prefer checking returned values/state; verify calls only for true side effects (email sent, event published). | Mock-call assertions as the only check. | low |
| TEST-026 | **Test data is minimal and intention-revealing** (builders/factories with defaults; override only what matters). | Giant fixtures where the relevant field is hidden; shared mutable fixture files. | low |

### 4.2 Choosing inputs: limits and partitions

**Equivalence partitioning** — split the input domain into classes the code should treat the same
way; test one representative per class (valid and invalid).

**Boundary value analysis (limits)** — bugs cluster at edges. For each boundary test:
`min − 1`, `min`, `min + 1`, a nominal value, `max − 1`, `max`, `max + 1`.

Checklist of boundaries reviewers look for in tests of non-trivial logic:
- **Numbers**: 0, negative, 1, max/min of type, overflow, NaN/Infinity (JS), precision (0.1 + 0.2), rounding .5 cases.
- **Collections/strings**: empty, one element, many, duplicates, very large, unsorted/sorted, whitespace-only, Unicode (multi-byte, emoji, RTL, combining chars), max length ± 1.
- **Optional/absent**: `null`/`undefined`/`None`, missing keys, empty object.
- **Time**: leap day, DST transitions, timezone boundaries, end of month/year, epoch, far future, clock skew, ordering of equal timestamps.
- **State**: first/last item, transitions out of each state, repeated operations (idempotency), concurrent operations.
- **External**: timeouts, partial failures, retries, malformed responses, 4xx/5xx, slow responses.
- **Permissions**: unauthenticated, wrong role, owner vs non-owner, expired token.

**Decision tables** — for logic with combinations of conditions, enumerate condition combinations
and expected actions; ensure each column has a test (use table-driven/parameterized tests).

**State-transition testing** — for workflows/state machines, test every valid transition and at
least one invalid transition from each state.

**Error guessing / negative testing** — invalid input, error paths, exceptions, error messages.

**Property-based testing** — assert invariants over generated input: round-trips, idempotence,
commutativity, "output is sorted", "never panics".

| ID | Practice | Check | Sev |
|---|---|---|---|
| TEST-030 | **Boundary values are tested** for logic with limits (ranges, sizes, quotas, pagination, dates). | Only nominal values tested for code with explicit limits/comparisons (`<`, `<=`). | medium |
| TEST-031 | **Each equivalence class has a representative, including invalid classes.** | Only happy path tested; no invalid-input tests for validators. | medium |
| TEST-032 | **Error paths are tested** (what happens when the DB/API fails, input is malformed). | No tests for `Err`/`catch`/rejection branches of critical code. | medium |
| TEST-033 | **Parameterized / table-driven tests** for many similar cases instead of copy-paste. | Ten near-identical tests differing only in literals. | low |
| TEST-034 | **State machines have transition coverage**, including invalid transitions. | Order/payment status flows tested only for the golden path. | medium |
| TEST-035 | **Authorization rules have negative tests** (forbidden for other users/roles). | Only "admin can do X" tested, never "user cannot". | high |

### 4.3 F.I.R.S.T. properties

| ID | Property | Violation signs | Sev |
|---|---|---|---|
| TEST-040 | **Fast** | Unit tests with real network, sleeps, large fixtures. | medium |
| TEST-041 | **Independent / isolated** — any order, any subset, in parallel. | Shared mutable module state; tests depending on previous test's DB rows; global mocks not reset. | high |
| TEST-042 | **Repeatable / deterministic** | `Math.random`, `Date.now`, real clock, unseeded RNG, timezone of CI machine, network calls, port collisions. | high |
| TEST-043 | **Self-validating** | Tests that print output for a human to check; no assertions. | medium |
| TEST-044 | **Timely** — written with the code. | Large untested modules with tests only for old code (inferred from coverage gaps). | low |

## 5. Test doubles

| Double | What it is | Use when |
|---|---|---|
| Dummy | Placeholder passed but never used. | Satisfying a signature. |
| Stub | Returns canned answers. | Controlling indirect inputs (a repository returning a fixed user). |
| Spy | Records calls for later assertion. | Verifying a side effect happened. |
| Mock | Pre-programmed expectations verified automatically. | Verifying protocol with an external collaborator. Use sparingly. |
| Fake | Working lightweight implementation (in-memory repo, fake clock, fake HTTP server). | Usually the best choice for repositories, clocks, queues. |

| ID | Practice | Check | Sev |
|---|---|---|---|
| TEST-050 | **Don't mock what you don't own**: wrap third-party APIs in an adapter you own, mock/fake the adapter, and integration-test the adapter against the real thing (or a recorded server). | Tests mocking `axios`, `fetch`, `reqwest`, ORM internals in dozens of places. | medium |
| TEST-051 | **Never mock the system under test** or its internals (partial mocks of the same class). | `jest.spyOn(service, 'privateHelper')` in service's own tests. | medium |
| TEST-052 | **Prefer fakes for time, randomness, IO** (injected clock, seeded RNG, in-memory store). | Tests patch globals (`Date`, `Math.random`) ad hoc and inconsistently. | low |
| TEST-053 | **Mocks are reset/restored between tests.** | Missing `restoreMocks`/`clearMocks` config; leaked spies. | medium |
| TEST-054 | **Over-mocking**: if setting up doubles takes more lines than the test, the design is too coupled (see ARCH-007). | Tests with 30 lines of mocks for 2 lines of act. | medium |

## 6. Test smells

| ID | Smell | Signs |
|---|---|---|
| TEST-060 | **Flaky test** | `retry`, `sleep`/`setTimeout` waits, tests marked skip "because flaky", order dependence. |
| TEST-061 | **Skipped / ignored tests left behind** | `.skip`, `xit`, `#[ignore]`, `test.todo` without an issue link. |
| TEST-062 | **Assertion roulette** | Many asserts without messages in one test; unclear which failed. |
| TEST-063 | **Eager test** | Tests many behaviors in one test. |
| TEST-064 | **Mystery guest** | Depends on external files/data not visible in the test. |
| TEST-065 | **Conditional test logic** | `if`/loops in tests that make the assertions vary. |
| TEST-066 | **Testing the framework / trivial code** | Tests asserting getters, constants, or that React renders a div. |
| TEST-067 | **Sensitive equality / over-specified snapshots** | Huge snapshots; asserting on whole serialized objects including timestamps/ids. |
| TEST-068 | **Duplicated setup** | Same 20-line arrange block copy-pasted; no builders. |
| TEST-069 | **Liar test** | Test passes regardless (async not awaited, assertion in a callback never called, `expect` without matcher call). |
| TEST-070 | **Commented-out assertions** | Asserts disabled to make tests pass. |

Report test smells with the relevant TEST ID; default severity `medium` for flaky/liar/isolation
problems, `low` for readability smells.

## 7. Integration & E2E specifics

| ID | Practice | Check | Sev |
|---|---|---|---|
| TEST-080 | **Real dependencies in integration tests** where feasible (Testcontainers, docker-compose test DB, ephemeral DB per run). | Integration tests against SQLite while prod is Postgres (dialect gaps) — flag as risk; or against a shared dev DB. | medium |
| TEST-081 | **Clean state per test**: transaction rollback, truncate, unique schema per worker. | Tests failing when run twice; reliance on seeded order. | high |
| TEST-082 | **External HTTP replaced by a local fake server or recorded fixtures** (MSW, wiremock, `httpmock`, `wiremock-rs`). | Tests calling real third-party APIs. | medium |
| TEST-083 | **E2E uses resilient selectors** (roles, labels, `data-testid`) and explicit waits for conditions, never fixed sleeps. | CSS-path selectors; `waitForTimeout(3000)`. | medium |
| TEST-084 | **Test environment config is explicit** (`.env.test`, test profiles) and doesn't touch real services or production data. | Tests reading prod-like env vars; risk of hitting real resources. | high |
| TEST-085 | **Migrations are exercised** in integration tests (schema created by the real migration path). | Tests creating schema via ORM sync differently from prod. | low |

## 8. Coverage, mutation testing & CI

| ID | Practice | Check | Sev |
|---|---|---|---|
| TEST-090 | **Coverage is measured** (line + branch) and visible in CI. | No coverage tooling (`c8`/`istanbul`/`vitest --coverage`, `cargo llvm-cov`/`tarpaulin`). | low |
| TEST-091 | **Coverage thresholds protect critical modules** (ratchet up; don't chase 100% globally). | No thresholds; or 100% mandated causing trivial tests. | low |
| TEST-092 | **Coverage is not mistaken for quality**: use mutation testing on core modules periodically. | High coverage but weak assertions (TEST-024) — recommend cargo-mutants/Stryker. | info |
| TEST-093 | **Tests run in parallel and are sharded** when the suite is large. | Serial long-running suite. | low |
| TEST-094 | **Flaky tests are tracked and fixed**, not auto-retried indefinitely. | Global retries in CI/test config. | medium |
| TEST-095 | **Test reports are published** (JUnit XML, coverage summary) for PR visibility. | — | info |
