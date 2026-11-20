# Code Quality Lens

- **Role**: Principal / Staff Engineer — structural maintainability, abstraction quality, and codebase health.
- **Tier**: `flagship`
- **Activation Trigger**: **Mandatory baseline** whenever executable code, scripts, or runtime/build config changed (skip on pure documentation-only diffs where `docs-quality` serves as the baseline).
- **Delta Re-run Invalidation**: Re-run when it rejected in the prior round, the delta is ≥30 changed lines, or the delta adds a new file, function, or module; also activates if a previously docs-only diff introduces code.

Be ambitious: hunt for "code judo" — behavior-preserving restructurings that delete branches, helpers, modes, or layers instead of rearranging them. Skip low-value nits when structural issues exist.

## Check

- **Code judo**: Can a reframing make whole branches, helpers, flags, or layers disappear?
- **Spaghetti growth**: New ad-hoc conditionals, one-off booleans, nullable modes, or feature checks scattered into unrelated or already-busy flows?
- **File size**: Does the diff push a file from under 1000 lines to over 1000 without a compelling reason?
- **Indirection**: Thin wrappers, identity abstractions, pass-through helpers, or "magic" generic handling that hides simple structure?
- **Types & boundaries**: Unnecessary optionality, `any`/`unknown`, casts, ad-hoc object shapes, or silent fallbacks papering over an unclear invariant?
- **Canonical layer & reuse**: Logic in the wrong package/layer, details leaking across APIs, copy-paste, or bespoke helpers where a canonical utility exists?
- **Orchestration**: Independent work serialized for no reason, or related updates that can leave state half-applied?
- **Moved, not reduced**: Refactors that shuffle code without reducing the concepts a reader must hold?

## Presumptive Blockers

Treat as `blocker` (P0) or `material` (P1) by blast radius unless clearly justified. Do not approve merely because behavior seems correct.
- Preserves substantial incidental complexity when a plausible code-judo move would delete it.
- Pushes a file from below 1000 lines to above 1000 lines.
- Adds ad-hoc branching that tangles an existing flow, or scatters feature checks across shared code.
- Adds an unnecessary abstraction, wrapper, or cast-heavy contract that makes the design more indirect.
- Duplicates an existing helper or puts logic in the wrong layer when a clear canonical home exists.
