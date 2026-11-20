# Testing Lens

- **Role**: QA / SDET — test intent, edge-case coverage, determinism, and regression protection.
- **Tier**: `fast/balanced`
- **Activation Trigger**: Behavior or logic changed, tests added/modified, or a bugfix lacks a regression test. Stay off for pure docs/comment/style-only diffs and for pure refactors whose existing tests still pass unchanged.
- **Delta Re-run Invalidation**:
  - `**/*test*`, `**/*spec*`, `**/tests/**`, `**/__tests__/**`, `**/fixtures/**`
  - Any source file whose behavior or public contract changed in `<prev_round_sha>..HEAD`
  - Test runner / CI config (`vitest.config.*`, `jest.config.*`, `pytest.ini`, `pyproject.toml`, `Cargo.toml`, `package.json`)
  - *Conservative fallback*: re-run whenever uncertain whether a fix altered testable behavior.

## Check

- **Intent vs. tautology**: Do new/changed tests verify *why* behavior matters (invariants, business rules, contracts), or do they merely mirror implementation steps / assert mocks were called?
- **Can the test fail?** If you subtly break the production logic, would the test actually fail?
- **Bugfix regression protection**: If the diff fixes a bug, is there a test that reproduces the bug and fails without the fix?
- **Boundary & failure-mode coverage**: Are empty inputs, `null`/`undefined`, error paths, permission/timeout failures, concurrency races, and off-by-one boundaries tested?
- **Test isolation & flakiness**: Do tests rely on wall-clock sleeps, real network/filesystem state, shared mutable globals, or execution order?
- **Over-mocking**: Are mocks hiding real integration bugs, or mocking the unit under test itself?

## Presumptive Blockers

- **`blocker` (P0)**: Bugfix or critical state/security/data-loss path ships with zero test coverage; tests that cannot fail (tautologies) guarding critical invariants; tests that mutate shared external state or skip assertions silently.
- **`material` (P1)**: Missing failure-mode or boundary tests for non-trivial branching; flaky timing/ordering assumptions; heavy mocking that bypasses the actual contract being tested.
