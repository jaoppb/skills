# TypeScript (TS-*)

Applies to code detected via `tsconfig.json`, `.ts/.tsx` files, or `typescript` in `package.json`.
Most rules also apply to modern JavaScript; for plain-JS projects, the first recommendation is
usually to adopt TypeScript or at least `// @ts-check` + JSDoc types (file as TS-001).

Framework and library specifics live in subfolders:
- `framework/nextjs.md` (NEXT-*)
- `lib/react.md` (REACT-*)

Add new ones as `framework/<name>.md` (e.g. `nestjs.md`, `express.md`, `remix.md`) and
`lib/<name>.md` (e.g. `prisma.md`, `tanstack-query.md`, `zod.md`).

## Contents
1. Tooling baseline
2. Compiler strictness
3. Type-system usage
4. Validation at boundaries
5. Async & promises
6. Error handling
7. Modules & project structure
8. Runtime pitfalls
9. Node.js server specifics
10. Testing
11. Security specifics
12. Documentation
13. Quick grep list

---

## 1. Tooling baseline

| ID | Practice | Check | Sev |
|---|---|---|---|
| TS-001 | **TypeScript (or checked JS) for non-trivial code.** | Large plain-JS codebase without `checkJs`. | medium |
| TS-002 | **`tsc --noEmit` (or `tsc -b`) runs in CI**; the build doesn't rely solely on a transpiler (esbuild/swc/babel strip types without checking). | No type-check script/job. | high |
| TS-003 | **ESLint with `typescript-eslint` type-aware configs** (`strictTypeChecked` + `stylisticTypeChecked`, or at least `recommendedTypeChecked`), or Biome with equivalent rules; zero warnings in CI. | No linter; non-type-aware config; `eslint-disable` sprinkled without reasons. | medium |
| TS-004 | **Formatter** (Prettier or Biome) enforced in CI. | None; or competing formatters. | low |
| TS-005 | **Package manager and Node version pinned** (`packageManager` field / Corepack, `.nvmrc` or `engines`), single lockfile, CI uses frozen install (`npm ci`, `pnpm i --frozen-lockfile`, `yarn --immutable`). | Multiple lockfiles; `npm install` in CI. | medium |
| TS-006 | **Unused code/deps detection** (`knip`, `ts-prune`, `depcheck`). | Many unused exports/deps found by inspection. | low |
| TS-007 | **Dependency boundaries / cycles checked** (`madge --circular`, `dependency-cruiser`) in larger codebases. | Known cycles via barrel files. | low |

## 2. Compiler strictness

Recommended `tsconfig` flags (check `tsconfig*.json`, including `extends` chains):

```jsonc
{
  "strict": true,                         // TS-010
  "noUncheckedIndexedAccess": true,       // TS-011
  "exactOptionalPropertyTypes": true,     // optional, stricter
  "noImplicitOverride": true,
  "noImplicitReturns": true,
  "noFallthroughCasesInSwitch": true,
  "noPropertyAccessFromIndexSignature": true,
  "useUnknownInCatchVariables": true,     // included in strict
  "forceConsistentCasingInFileNames": true,
  "isolatedModules": true,                // required by most bundlers
  "verbatimModuleSyntax": true,           // explicit `import type`
  "skipLibCheck": true                    // acceptable
}
```

| ID | Practice | Check | Sev |
|---|---|---|---|
| TS-010 | **`strict: true`** in every tsconfig that compiles app code (no per-flag downgrades like `strictNullChecks: false`). | Missing or overridden. | high |
| TS-011 | **`noUncheckedIndexedAccess`** for code indexing arrays/records with dynamic keys. | Off; code assumes `arr[i]` defined. | low |
| TS-012 | **Test and script files are type-checked too** (included in a tsconfig used by CI). | `tests/` excluded from all tsconfigs. | low |

## 3. Type-system usage

| ID | Practice | Check | Sev |
|---|---|---|---|
| TS-020 | **No `any`** (explicit or implicit). Use `unknown` and narrow, generics, or precise types. `@typescript-eslint/no-explicit-any` + `no-unsafe-*` rules on. | `: any`, `as any`, `any[]`, untyped `JSON.parse` results flowing around. | medium |
| TS-021 | **Minimal type assertions (`as`)** — prefer narrowing, type guards, `satisfies`. Never double-assert (`as unknown as T`). | `as Foo` on external data; `as unknown as`. | medium |
| TS-022 | **No non-null assertions (`!`)** on values that can really be null; handle the case. | `user!.id`, `document.getElementById(...)!` in logic paths. | medium |
| TS-023 | **No `@ts-ignore`**; `@ts-expect-error` only with a reason comment. | `@ts-ignore`/`@ts-nocheck` occurrences. | medium |
| TS-024 | **Discriminated unions for variants and states**; exhaustive `switch` with a `never` check (`assertNever(x)`) or `@typescript-eslint/switch-exhaustiveness-check`. | Optional-field soup; `default:` swallowing new cases. | medium |
| TS-025 | **Branded/nominal types for ids and validated values** (`type UserId = string & { __brand: "UserId" }`) where mix-ups are plausible. | `string` ids of several entities passed interchangeably. | low |
| TS-026 | **`readonly` and `as const`** for data that shouldn't change; `ReadonlyArray` in parameters. | Functions mutating input arrays/objects. | low |
| TS-027 | **Prefer union literal types or `as const` objects over `enum`**; avoid `const enum` (breaks with isolatedModules) and numeric enums (reverse mapping, accepts any number). | Numeric enums for domain states; `const enum` in libraries. | low |
| TS-028 | **Explicit return types on exported/public functions** (stable contracts, faster checking); inference fine for locals. | Exported functions whose inferred return type is a complex/accidental union. | low |
| TS-029 | **Types derived, not duplicated**: `z.infer`, `typeof`, `ReturnType`, `Pick`/`Omit`, generated types from OpenAPI/GraphQL/Prisma. | Hand-written interfaces duplicating schemas, drifting. | medium |
| TS-030 | **Utility-type gymnastics kept readable**; complex types named and documented. | Unreadable conditional types in app code. | info |
| TS-031 | **`interface` vs `type` used consistently** (team convention; `consistent-type-definitions`). | Mixed without reason. | info |
| TS-032 | **Optional vs `| undefined` vs `null`** used consistently; one "absence" convention per codebase. | Mixed `null`/`undefined` checks (`== null` hacks). | low |

## 4. Validation at boundaries

| ID | Practice | Check | Sev |
|---|---|---|---|
| TS-040 | **Runtime validation of all external data** (HTTP bodies, query params, env vars, `localStorage`, third-party API responses, webhooks, file contents) with a schema library (Zod, Valibot, ArkType, TypeBox) — TS types alone don't exist at runtime. | `req.body as CreateUser`; `await res.json() as T`. | high |
| TS-041 | **Parse, don't validate**: validation returns typed data used downstream; no re-checking inside the core. | `isValid()` booleans followed by unsafe casts. | low |
| TS-042 | **Env vars validated once at startup** into a typed config (e.g. `@t3-oss/env-*`, Zod). | `process.env.X!` scattered. | medium |

## 5. Async & promises

| ID | Practice | Check | Sev |
|---|---|---|---|
| TS-050 | **No floating promises**: every promise awaited, returned, or explicitly `void`-ed with error handling (`no-floating-promises`). | Calls to async functions without `await` in non-fire-and-forget contexts. | high |
| TS-051 | **No async callbacks where a void callback is expected** (`no-misused-promises`): `arr.forEach(async ...)`, async event handlers whose rejection is lost. | `forEach(async`. | high |
| TS-052 | **Concurrent independent work with `Promise.all`/`allSettled`**, sequential `await` in loops only when order/rate requires it — and bounded concurrency (`p-limit`) for large inputs. | `for (...) await fetch()` over hundreds of items; unbounded `Promise.all`. | medium |
| TS-053 | **Cancellation and timeouts** with `AbortController`/`AbortSignal.timeout()` for fetches and long operations. | `fetch` without timeout in server code. | medium |
| TS-054 | **No mixing callbacks/`.then` chains/`async` styles** within the same module. | `.then` inside `async` functions. | low |
| TS-055 | **Global handlers for `unhandledRejection`/`uncaughtException`** in Node services (log + exit/restart), not used to swallow errors. | Handlers that log and continue. | medium |

## 6. Error handling

| ID | Practice | Check | Sev |
|---|---|---|---|
| TS-060 | **Throw `Error` instances (or subclasses)**, never strings/objects (`only-throw-error`). | `throw "bad"`; `throw { code }`. | medium |
| TS-061 | **Preserve causes**: `new Error("Saving order failed", { cause: err })`. | Re-throws losing the original error. | low |
| TS-062 | **Narrow `unknown` in catch** before use (`err instanceof Error`). | `catch (e: any)`; `e.message` on unknown. | low |
| TS-063 | **Expected failures as values** where it clarifies control flow (discriminated `Result` types, or libraries like `neverthrow`), exceptions for the unexpected — applied consistently. | Exceptions for normal validation flow everywhere *and* ad-hoc `{ error }` returns elsewhere. | low |
| TS-064 | **Custom error classes** set `name` and carry structured data for mapping to HTTP/UI. | `if (err.message.includes("not found"))`. | medium |

## 7. Modules & project structure

| ID | Practice | Check | Sev |
|---|---|---|---|
| TS-070 | **ES modules** with consistent `type: module`/extensions setup; no CJS/ESM interop hacks scattered. | `require` mixed with `import` in TS source. | low |
| TS-071 | **Barrel files (`index.ts`) used sparingly** — they cause cycles, slow tooling, and hurt tree-shaking in apps. | Deep re-export chains; `export *` everywhere. | low |
| TS-072 | **`import type` for type-only imports** (`verbatimModuleSyntax`/`consistent-type-imports`). | Runtime imports of type-only modules causing cycles/side effects. | info |
| TS-073 | **Path aliases consistent** between tsconfig, bundler and test runner. | Aliases resolving differently in tests. | low |
| TS-074 | **Monorepo packages** declare their own deps, have their own tsconfig with project references or a build tool (Turborepo/Nx), and import each other by package name. | `../../packages/x/src` imports. | medium |
| TS-075 | **Named exports preferred** for refactorability (default exports where frameworks require them — e.g. Next.js pages/layouts). | Inconsistent default exports in library code. | info |

## 8. Runtime pitfalls

| ID | Practice | Check | Sev |
|---|---|---|---|
| TS-080 | **Strict equality** (`===`), except deliberate `== null`. | `==` with mixed types. | low |
| TS-081 | **No floating-point money**; integer minor units or a decimal library. | `price * 1.1` on currency. | high |
| TS-082 | **Dates via a proper library or `Temporal`/`Intl`**; no manual string parsing of dates; UTC storage. | `new Date("2024-01-02")` timezone assumptions; manual month math. | medium |
| TS-083 | **No mutation of function arguments / shared objects**; spread/`structuredClone` deliberately. | Functions editing params; `Object.assign(existing, …)`. | low |
| TS-084 | **No `delete` on hot objects / dynamic shape changes** in performance-sensitive code. | — | info |
| TS-085 | **Truthiness checks don't eat valid falsy values** (`0`, `""`): use `??` and explicit comparisons (`prefer-nullish-coalescing`, `strict-boolean-expressions`). | `value || default` where 0 is valid. | medium |

## 9. Node.js server specifics

| ID | Practice | Check | Sev |
|---|---|---|---|
| TS-090 | **No blocking the event loop** on request paths: sync fs (`readFileSync`), `crypto` sync hashing, CPU-heavy loops → async APIs, worker threads, or queues. | `*Sync(` calls in handlers. | high |
| TS-091 | **Graceful shutdown** (SIGTERM: stop accepting, drain, close DB pools). | No signal handling in long-running services. | medium |
| TS-092 | **Connection pools reused** (one Prisma/DB client per process, not per request). | Clients created inside handlers. | high |
| TS-093 | **Body size limits and request timeouts** configured on servers. | Defaults unbounded. | medium |

## 10. Testing

Apply testing.md; TS-specific conventions:

| ID | Practice | Check | Sev |
|---|---|---|---|
| TS-100 | **Modern runner**: Vitest (or Jest with proper TS transform / `node:test`); config restores mocks between tests (`restoreMocks: true` / `mockReset`). | Leaky mocks; outdated `ts-jest` configs slowing tests. | low |
| TS-101 | **HTTP mocked at the network layer with MSW** (or nock/undici `MockAgent`) rather than mocking `fetch`/axios per test. | `vi.mock('axios')` scattered (TEST-050). | low |
| TS-102 | **Type-level tests for public types/generics** in libraries (`expectTypeOf` in Vitest, `tsd`, `@ts-expect-error` assertions). | Complex exported generics with no type tests. | info |
| TS-103 | **Fake timers** (`vi.useFakeTimers()`, `vi.setSystemTime`) instead of real waits; reset after each test. | `await new Promise(r => setTimeout(r, 1000))` in tests. | medium |
| TS-104 | **Integration tests with real infra** (Testcontainers for Postgres/Redis; Prisma/Drizzle against a test DB). | DB layer only tested with mocks. | medium |
| TS-105 | **Property-based tests with `fast-check`** for parsers, formatters, reducers. | — | info |
| TS-106 | **E2E with Playwright** (or Cypress) using role/label locators and web-first assertions (`await expect(locator).toBeVisible()`). | `page.waitForTimeout`; CSS selectors. | medium |
| TS-107 | **Mutation testing (Stryker)** on core logic packages periodically. | — | info |

## 11. Security specifics

| ID | Practice | Check | Sev |
|---|---|---|---|
| TS-110 | **No `eval`/`new Function`/`setTimeout(string)`**. | Occurrences. | high |
| TS-111 | **Prototype-pollution-safe merges** (use `structuredClone`, schema-parsed objects, `Object.create(null)` maps, or `Map`). | Custom deep merge on request data. | medium |
| TS-112 | **Lifecycle scripts audited**; consider `ignore-scripts` / pnpm `onlyBuiltDependencies`. | Unknown packages with `postinstall`. | low |

## 12. Documentation

| ID | Practice | Check | Sev |
|---|---|---|---|
| TS-120 | **TSDoc on exported library APIs** (`@param`, `@returns`, `@throws`, `@example`); generated docs (TypeDoc) for published packages. | Public exports undocumented. | low |

## 13. Quick grep list

```bash
rg -n ':\s*any\b|as any|<any>' -g '*.ts' -g '*.tsx'                  # TS-020
rg -n 'as unknown as'                                                 # TS-021
rg -n '@ts-ignore|@ts-nocheck|eslint-disable'                         # TS-023, TS-003
rg -n '[a-zA-Z_\)\]]!\.' -g '*.ts' -g '*.tsx'                         # TS-022 (noisy; confirm)
rg -n 'forEach\(async'                                                # TS-051
rg -n 'catch\s*\([^)]*\)\s*\{\s*\}'                                   # GEN-040
rg -n 'throw ["'\''`]'                                                # TS-060
rg -n 'readFileSync|writeFileSync|execSync' -g '!**/scripts/**'       # TS-090
rg -n 'JSON\.parse\(|\.json\(\)\s*as '                                # TS-040
rg -n 'process\.env\.' -g '*.ts' -g '*.tsx'                           # TS-042 (count call sites)
rg -n 'console\.(log|debug)' -g '!**/*.test.*'                        # GEN-110
rg -n '\.only\(|\.skip\(|\bxit\(|test\.fixme'                         # TEST-061
```
