# Frontend Lens

- **Role**: Frontend & Accessibility Engineer — UI correctness, interaction states, responsive layout, and WCAG 2.1 AA compliance.
- **Tier**: `fast/balanced`
- **Activation Trigger**: Diff touches UI components, templates, styles/CSS, layout, client-side state/forms, or interactive accessibility. Stay off for pure backend, CLI, or non-UI diffs.
- **Delta Re-run Invalidation**:
  - `**/*.tsx`, `**/*.jsx`, `**/*.vue`, `**/*.svelte`, `**/*.css`, `**/*.scss`, `**/*.html`, `**/components/**`, `**/pages/**`, `**/app/**`
  - Design-system tokens, theme configs, and UI state hooks
  - *Conservative fallback*: re-run whenever uncertain whether a change affects rendered UI or client state.

---

## Mode Selection: Impeccable First, Built-In Fallback

1. **Check for Impeccable**: Look for an installed Impeccable `audit` skill in the project or user skill roots (a project-local variant—such as a modified non-web one—wins over upstream `pbakaus/impeccable`; never vendor or copy Impeccable into the repo).
   - If Impeccable `audit` is installed and initialized (e.g., `PRODUCT.md` present where required), run `audit` on the UI-bearing parts of the diff and map its severities (`P0` → `blocker`, `P1` → `material`, `P2/P3` → `nitpick`).
   - `critique` (scored UX review) is **not** part of the automated review loop; it stays with the user at PR review.
2. **Built-In Fallback**: When Impeccable is not installed or not initialized (e.g., missing `PRODUCT.md`), run the built-in checklist below (unless a host workflow explicitly requires blocking on missing Impeccable setup).

---

## Built-In UI, State, Responsive & WCAG Checklist

- **Interactive states**: Are loading, empty, error, disabled, and success states handled cleanly (no frozen spinners or silent failures)?
- **Forms & validation**: Inline, accessible error messages (`aria-describedby` / `aria-invalid`), preserved user input on failure, and double-submit protection?
- **Responsive layout**: Does the layout hold at mobile (`375px`), tablet, and desktop widths without horizontal overflow, clipped text, or overlapping controls?
- **Keyboard & focus**: Full keyboard navigability (`Tab`, `Enter`, `Escape`, arrow keys where expected), visible focus rings, no keyboard traps, and proper focus restoration on modal/drawer close?
- **Semantics & WCAG 2.1 AA**: Semantic HTML (`button` vs `div`), accurate `aria-label`/headings/landmarks, sufficient text/UI contrast, and `prefers-reduced-motion` respect for animations?
- **Visual & token consistency**: Uses existing design tokens/primitives rather than hardcoded one-off colors, spacing, or z-index hacks.

---

## Severity Mapping

- **`blocker` (P0)**: Unusable core flow, keyboard trap, inaccessible primary action, or broken layout blocking interaction.
- **`material` (P1)**: Missing error/loading/empty state, WCAG AA contrast/label failure, broken mobile layout, or lost user input on form error.
- **`nitpick` (P2/P3)**: Minor spacing/alignment polish or optional micro-interaction refinements.

Approve only with **zero `blocker` and zero `material` findings**.
