# Rust (RS-*)

Applies to crates detected via `Cargo.toml`. Builds on generic-practices; follows the
[Rust API Guidelines](https://rust-lang.github.io/api-guidelines/), Clippy's lint groups, and
common ecosystem conventions (tokio, serde, thiserror/anyhow, tracing).

**Frameworks/libs**: add files under `references/rust/framework/` (e.g. `axum.md`, `actix-web.md`,
`bevy.md`) and `references/rust/lib/` (e.g. `tokio.md`, `sqlx.md`, `serde.md`) as needed. Until they
exist, the async and persistence sections below cover the essentials.

## Contents
1. Tooling baseline
2. Project & module structure
3. Error handling
4. Ownership, borrowing & allocation
5. Types & API design
6. Unsafe code
7. Async & concurrency
8. Performance
9. Testing
10. Security specifics
11. Documentation
12. Quick grep list

---

## 1. Tooling baseline

| ID | Practice | Check | Sev |
|---|---|---|---|
| RS-001 | `rustfmt` enforced in CI (`cargo fmt --check`); `rustfmt.toml` only if deviating. | CI lacks fmt check. | low |
| RS-002 | `cargo clippy --all-targets --all-features -- -D warnings` in CI. Lints configured centrally via `[lints]`/`[workspace.lints]` in `Cargo.toml` (not scattered `#![allow]`). Consider enabling selected `clippy::pedantic` lints and `unwrap_used`/`expect_used` for libraries. | No clippy in CI; many `#[allow(clippy::...)]` without reason. | medium |
| RS-003 | Toolchain pinned with `rust-toolchain.toml`; `rust-version` (MSRV) declared for libraries and tested in CI. | Missing; CI uses `stable` floating with no MSRV job for a published crate. | low |
| RS-004 | Current edition (2021 or 2024) used consistently across a workspace. | Mixed/old editions without reason. | low |
| RS-005 | `Cargo.lock` committed for binaries/apps (and for libraries too, per current Cargo guidance); CI builds with `--locked`. | Missing lockfile; no `--locked`. | medium |
| RS-006 | Supply-chain checks: `cargo audit` and/or `cargo deny check` (advisories, licenses, bans, sources) in CI. | Absent. | medium |
| RS-007 | Unused dependencies removed (`cargo machete`/`cargo udeps`); features minimal (`default-features = false` where sensible). | Heavy deps used for one function; all features enabled. | low |
| RS-008 | Workspace for multi-crate projects; shared versions via `[workspace.dependencies]`. | Same dep at different versions across crates; duplicated metadata. | low |

## 2. Project & module structure

| ID | Practice | Check | Sev |
|---|---|---|---|
| RS-010 | **Thin `main.rs`**: binaries parse config/args and call into `lib.rs`, so logic is testable and reusable. | Business logic in `main.rs`; `lib.rs` absent in non-trivial binaries. | medium |
| RS-011 | **Visibility is minimal**: `pub(crate)`/private by default; public API deliberately curated, re-exported from `lib.rs`. | Everything `pub`; consumers importing deep module paths. | low |
| RS-012 | **Module tree mirrors the domain**; no `utils.rs`/`helpers.rs` grab bags. | Big `utils` module imported everywhere (ARCH-010). | low |
| RS-013 | **Crate boundaries enforce architecture** in larger systems (domain crate without IO deps; adapters in separate crates). | Domain modules depending on `sqlx`/`reqwest`/`axum` (ARCH-003). | medium |
| RS-014 | **Feature flags are additive** and don't change public types incompatibly; `--no-default-features` and `--all-features` both build (check CI matrix for libraries). | Mutually exclusive features; `cfg(feature)` removing items others rely on. | medium |
| RS-015 | **No `mod.rs` vs file-name inconsistency** within a crate (pick one style). | Mixed styles. | info |

## 3. Error handling

| ID | Practice | Check | Sev |
|---|---|---|---|
| RS-020 | **Libraries expose typed errors** (enum, often via `thiserror`) that implement `std::error::Error`, are `Send + Sync + 'static`, and carry sources. **Applications** may use `anyhow`/`eyre` with `.context()`. | `anyhow::Error` in a library's public API; `String`/`Box<dyn Error>` errors everywhere; errors without `source()`. | medium |
| RS-021 | **No `unwrap()`/`expect()` on fallible operations in non-test code** unless an invariant guarantees success — then `expect("why this cannot fail")`. Never on user input, IO, network, parsing. | `grep -n "\.unwrap()"` outside tests; `expect("failed")` with uninformative messages. | high |
| RS-022 | **No `panic!`, `todo!`, `unimplemented!`, `unreachable!` on reachable paths** in production code. | Occurrences outside tests; `todo!()` in shipped code. | high |
| RS-023 | **Propagate with `?` and add context**; don't discard with `let _ =` or `.ok()` unless intentional and commented. | `let _ = tx.send(...)`, `.ok();` on writes, `.unwrap_or_default()` hiding failures. | high |
| RS-024 | **Indexing and slicing that can panic** (`v[i]`, `&s[a..b]`) are guarded or replaced with `.get()` when indices derive from input. | Direct indexing with computed/external indices; byte-slicing strings with non-ASCII input. | medium |
| RS-025 | **`Option` vs `Result` used correctly**: absence is `Option`, failure is `Result`; no sentinel values (`-1`, empty string). | Functions returning `""`/`0` for errors. | low |
| RS-026 | **Error types are not overly broad**: one giant `Error` enum for the whole crate is fine for small crates, but per-module errors improve matching in large ones. | 50-variant error enum shared by unrelated modules. | low |

## 4. Ownership, borrowing & allocation

| ID | Practice | Check | Sev |
|---|---|---|---|
| RS-030 | **Accept borrowed, general types**: `&str` not `&String`, `&[T]` not `&Vec<T>`, `impl AsRef<Path>`/`impl Into<String>` where useful (clippy `ptr_arg`). | Signatures taking `&String`, `&Vec<T>`, `&Box<T>`. | low |
| RS-031 | **No clone-to-silence-the-borrow-checker** in hot or obvious paths; restructure borrows, use references, `Rc`/`Arc` deliberately, or `std::mem::take`. | `.clone()` on large structs/collections inside loops; clones immediately borrowed. | medium |
| RS-032 | **`Arc<Mutex<T>>` is not the default architecture**: prefer ownership + message passing, or finer-grained/`RwLock`/atomics where justified. | Pervasive `Arc<Mutex<_>>` wrapping whole app state; lock contention points. | medium |
| RS-033 | **`Cow`/iterators avoid needless allocation** when returning possibly-borrowed data. | Collecting into `Vec` just to iterate once; `to_string()` on every call. | low |
| RS-034 | **Interior mutability (`RefCell`, `Cell`) is local and justified**; `RefCell` borrow panics considered. | `Rc<RefCell<_>>` graphs throughout the domain. | medium |
| RS-035 | **Lifetimes are not over-annotated**; elision used; structs holding references only when beneficial. | Explicit lifetimes everywhere they're elidable; self-referential workarounds. | info |

## 5. Types & API design

| ID | Practice | Check | Sev |
|---|---|---|---|
| RS-050 | **Newtypes for domain primitives** (`UserId(Uuid)`, `Cents(i64)`), with validation in constructors (`TryFrom`). | Bare `String`/`u64` ids interchangeable across entities (SMELL-004). | medium |
| RS-051 | **Enums model states**; exhaustive `match` without wildcard `_` arms on domain enums (so new variants force updates). | `bool` combos; `_ =>` swallowing new variants. | medium |
| RS-052 | **Public enums/structs of libraries use `#[non_exhaustive]`** where future extension is expected. | Adding a variant would be a breaking change. | low |
| RS-053 | **Common traits implemented** (C-COMMON-TRAITS): `Debug` on all public types; `Clone`, `PartialEq`, `Eq`, `Hash`, `Default`, `Display` where meaningful; `serde` behind a feature in libraries. | Public types without `Debug`. | low |
| RS-054 | **Conversions via `From`/`TryFrom`/`FromStr`**, not ad-hoc `to_x()` functions; naming per guidelines (`as_` cheap borrow, `to_` costly, `into_` consuming). | Methods named `get_x` (C-GETTER says `x()`); `to_` that consumes self. | low |
| RS-055 | **Builders for complex construction**; no constructors with many positional args. | `new(a, b, c, d, e, f)`. | low |
| RS-056 | **Generics vs trait objects chosen deliberately** (static dispatch for hot paths; `dyn` to reduce code bloat or for heterogeneous collections). | `Box<dyn Trait>` in tight loops; generics explode compile times for no benefit. | info |
| RS-057 | **Don't leak dependency types in the public API** unless intentional (semver coupling). | Public functions returning `reqwest::Response`/`sqlx::Error`. | low |
| RS-058 | **Numeric conversions are explicit and checked**: `TryFrom`/`try_into` instead of `as` when truncation/sign loss is possible (clippy `cast_possible_truncation`). | `x as u32` on `usize`/`i64` from input. | medium |
| RS-059 | **Integer overflow considered**: `checked_*`/`saturating_*`/`wrapping_*` explicit where inputs are external (release builds wrap silently). | Unchecked `+`/`*` on sizes, money, counters from input. | medium |

## 6. Unsafe code

| ID | Practice | Check | Sev |
|---|---|---|---|
| RS-040 | **`unsafe` is rare, minimal in scope, and encapsulated** behind safe abstractions. Crates without need use `#![forbid(unsafe_code)]`. | `unsafe` blocks in application code; large unsafe regions. | high |
| RS-041 | **Every `unsafe` block has a `// SAFETY:` comment** stating the invariants relied on (clippy `undocumented_unsafe_blocks`); `unsafe fn` documents `# Safety`. | Missing justification. | high |
| RS-042 | **No UB-prone patterns**: `mem::transmute` between unrelated types, creating references to uninitialized memory, aliasing `&mut`, `static mut` (use atomics/`OnceLock`/`Mutex`). | `static mut`; `transmute`; `get_unchecked` on unchecked indices. | critical |
| RS-043 | **Unsafe code is tested under Miri** (and sanitizers where feasible). | No `cargo miri test` job for crates with unsafe. | medium |
| RS-044 | **FFI boundaries** validate pointers/lengths, handle panics (`catch_unwind` at `extern "C"` boundaries), and document ownership. | Panics unwinding across FFI. | high |

## 7. Async & concurrency

| ID | Practice | Check | Sev |
|---|---|---|---|
| RS-060 | **No blocking in async contexts**: `std::fs`, `std::thread::sleep`, heavy CPU, blocking DB clients inside `async fn` → use async equivalents or `spawn_blocking`. | `std::fs::` / `thread::sleep` / `reqwest::blocking` in async code. | high |
| RS-061 | **No `std::sync::Mutex` guard (or any lock guard) held across `.await`**; use `tokio::sync::Mutex` only if truly needed, or restructure to release before awaiting (clippy `await_holding_lock`). | Guard variable alive across an await point. | high |
| RS-062 | **Spawned tasks are owned**: `JoinHandle`s awaited or tracked (`JoinSet`, `TaskTracker`); errors and panics surfaced. | `tokio::spawn` results dropped; panics silently lost. | medium |
| RS-063 | **Cancellation safety** considered in `select!` branches; graceful shutdown implemented (signal handling, `CancellationToken`). | `select!` on non-cancel-safe futures (e.g. partially-read streams) in loops; no shutdown path. | medium |
| RS-064 | **Bounded channels and concurrency limits** (`Semaphore`, `buffer_unordered(n)`). | `unbounded_channel` for external input; unbounded `join_all`. | medium |
| RS-065 | **Timeouts on all external calls** (`tokio::time::timeout`, client timeouts). | HTTP/DB clients built without timeouts. | medium |
| RS-066 | **One async runtime**, created once (`#[tokio::main]`), not nested `Runtime::new()` / `block_on` inside async. | `block_on` inside async functions. | high |
| RS-067 | **Concurrency-sensitive code tested** with `loom` or stress tests where custom sync primitives exist. | Custom lock-free code with no such tests. | low |

## 8. Performance

| ID | Practice | Check | Sev |
|---|---|---|---|
| RS-070 | **Avoid allocations in hot loops**: reuse buffers, `with_capacity`, iterate instead of collect. | `Vec::new()`/`format!` inside tight loops; `collect::<Vec<_>>()` then `.iter()` once. | low |
| RS-071 | **Use iterators idiomatically** (`iter().map().filter()`), but keep chains readable. | Manual index loops `for i in 0..v.len()` (clippy `needless_range_loop`). | low |
| RS-072 | **Release profile tuned when performance matters** (`lto`, `codegen-units`, `panic = "abort"` where acceptable) and benchmarks exist (`criterion`/`divan`). | Perf claims without benchmarks. | info |
| RS-073 | **Logging via `tracing`** with structured fields and spans, not `println!`/`eprintln!` in services/libraries; libraries never initialize a global subscriber. | `println!` in library code; `tracing_subscriber::fmt::init()` inside a lib. | low |

## 9. Testing

Conventions and tools; apply testing.md principles on top.

| ID | Practice | Check | Sev |
|---|---|---|---|
| RS-080 | **Unit tests co-located** in `#[cfg(test)] mod tests` per module; **integration tests in `tests/`** exercise the public API only. | Integration tests reaching private items via `pub` hacks; no tests dir for libraries. | medium |
| RS-081 | **Doctests on public API examples** (they compile and run). | Public functions without examples in libraries; `ignore`d doctests. | low |
| RS-082 | **Parameterized tests** with `rstest` or table-driven loops; **property tests** with `proptest`/`quickcheck` for parsers, encoders, math. | Copy-pasted test functions. | low |
| RS-083 | **Snapshot tests with `insta`** for complex outputs, reviewed via `cargo insta review`. | Huge hand-written expected strings. | info |
| RS-084 | **Mocking is sparing**: prefer trait-based fakes; `mockall` only at true boundaries. | `mockall` everywhere, including pure logic. | low |
| RS-085 | **Async tests use `#[tokio::test]`** (with `start_paused = true` + `tokio::time::advance` for time-dependent code) instead of real sleeps. | `sleep` in tests. | medium |
| RS-086 | **Integration tests for DB code** run against real databases (`sqlx::test`, testcontainers). | Repositories untested or mocked. | medium |
| RS-087 | **Test runner & coverage**: `cargo nextest` for speed/isolation; coverage via `cargo llvm-cov`; mutation testing via `cargo-mutants` on core crates. | — | info |
| RS-088 | **Tests assert values, not just `is_ok()`**; error tests match the error variant (`assert!(matches!(err, MyError::NotFound { .. }))`). | `assert!(result.is_ok())` as the only assertion. | medium |

## 10. Security specifics

| ID | Practice | Check | Sev |
|---|---|---|---|
| RS-090 | **Deserialization limits**: bounded sizes for untrusted input (body size limits, `serde` with `deny_unknown_fields` where strictness matters), no recursion bombs. | Unbounded `serde_json::from_slice` on request bodies without size limits. | medium |
| RS-091 | **SQL via `sqlx` macros/query builders with bind parameters**; never `format!` into SQL. | `format!("... WHERE id = {}", ...)` passed to `query()`. | critical |
| RS-092 | **Secrets in memory** wrapped (`secrecy::SecretString`, `zeroize`) and not `Debug`-printed. | Secrets in structs deriving `Debug` that get logged. | medium |
| RS-093 | **`Command` built with separate args**, never `sh -c` with interpolated input. | See SEC-011. | critical |

## 11. Documentation

| ID | Practice | Check | Sev |
|---|---|---|---|
| RS-095 | **Libraries enable `#![warn(missing_docs)]`** and document panics (`# Panics`), errors (`# Errors`), and safety (`# Safety`). | Public items undocumented. | low |
| RS-096 | **Crate-level docs** (`//!` in `lib.rs`) explain purpose and give a quick example; README can be included via `#![doc = include_str!("../README.md")]`. | Missing. | info |

## 12. Quick grep list

```bash
rg -n '\.unwrap\(\)|\.expect\(' --glob '!**/tests/**' --glob '!**/benches/**'   # RS-021 (then exclude #[cfg(test)] blocks by reading)
rg -n 'panic!|todo!|unimplemented!|unreachable!'                                 # RS-022
rg -n 'let _ = |\.ok\(\);'                                                       # RS-023
rg -n 'unsafe \{|unsafe fn|static mut|transmute'                                 # RS-040..042
rg -n 'std::fs::|thread::sleep|reqwest::blocking' -g '*.rs'                       # RS-060 (check if inside async)
rg -n 'Arc<Mutex<'                                                               # RS-032
rg -n ' as (u8|u16|u32|i32|usize|i64)\b'                                         # RS-058
rg -n 'format!\(.*(SELECT|INSERT|UPDATE|DELETE)'                                 # RS-091
rg -n 'println!|eprintln!|dbg!' --glob '!**/examples/**'                         # RS-073
rg -n '#\[ignore\]|#!?\[allow\('                                                 # TEST-061, RS-002
```
