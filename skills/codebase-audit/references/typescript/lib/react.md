# React (REACT-*)

Applies when `react` is a dependency. Read with `../index.md` (TS-*); for Next.js apps also
`../framework/nextjs.md`. Rules reflect React 18/19 guidance from react.dev (Rules of React,
"You Might Not Need an Effect", the React Compiler). Check the installed version: some items (e.g.
`forwardRef` deprecation, Actions, `use`) are React 19+.

## Contents
1. Tooling
2. Components & composition
3. Rules of React & hooks
4. Effects
5. State management
6. Rendering & performance
7. Forms & accessibility
8. Error handling & async UI
9. Security
10. Testing
11. Quick grep list

---

## 1. Tooling

| ID | Practice | Check | Sev |
|---|---|---|---|
| REACT-001 | **`eslint-plugin-react-hooks`** (`rules-of-hooks` error, `exhaustive-deps` on; newer versions include React Compiler-powered rules) and `eslint-plugin-jsx-a11y` enabled. | Missing; many `exhaustive-deps` disables. | medium |
| REACT-002 | **`<StrictMode>`** enabled in development to surface impure renders and effect bugs. | Absent at root (frameworks may enable it by default — check config). | low |
| REACT-003 | **React Compiler** considered/adopted for React 19 projects, reducing manual memoization (optional; note as info). | — | info |

## 2. Components & composition

| ID | Practice | Check | Sev |
|---|---|---|---|
| REACT-010 | **Small components with one responsibility**; split when a component mixes data fetching, business rules and complex markup (guide: > ~200–250 lines of TSX or many unrelated state variables). | Giant page components; components with 10+ `useState`. | medium |
| REACT-011 | **Business logic outside components** (pure functions, custom hooks, services) so it's testable without rendering. | Pricing/validation/permission logic inline in JSX handlers (ARCH-005). | medium |
| REACT-012 | **Composition over configuration**: `children`/slots instead of boolean-prop explosions (`showHeader`, `isCompact`, `variant2`). | Components with many boolean props toggling sections (SMELL-052). | low |
| REACT-013 | **Avoid deep prop drilling** (> ~3 levels of pass-through) — use composition or context for truly global concerns. | Props threaded unchanged through intermediate components. | low |
| REACT-014 | **Components are defined at module level**, never inside other components (remounts every render, loses state). | `function Inner()` / `const Row = () =>` declared inside a component body. | high |
| REACT-015 | **Custom hooks extract reusable stateful logic**, named `useX`, return a stable, minimal API. | Copy-pasted effect+state blocks across components. | low |
| REACT-016 | **Props typed explicitly** (`type Props = {...}`); `children: React.ReactNode`; event handlers typed (`React.ChangeEvent<HTMLInputElement>`); generic components where data-shaped. | `props: any`; untyped event params. | low |
| REACT-017 | **Feature-based folder structure** (components, hooks, and logic for a feature together) over giant `components/` dumps for large apps. | Hundreds of files in one flat `components/` folder. | low |
| REACT-018 | *(React 19)* **`ref` as a regular prop** in new code instead of `forwardRef`; Context as provider (`<Ctx>`) — informational for upgrades. | — | info |

## 3. Rules of React & hooks

| ID | Practice | Check | Sev |
|---|---|---|---|
| REACT-020 | **Hooks only at the top level** of components/custom hooks — never in conditions, loops, or after early returns. | Conditional hook calls. | critical |
| REACT-021 | **Renders are pure**: no side effects (fetching, subscriptions, mutations of external variables, `Math.random`/`Date.now` used for output) during render. | Assignments to module variables in render; `localStorage` writes in render. | high |
| REACT-022 | **Props and state are never mutated**; updates create new objects/arrays (`[...arr, x]`, `structuredClone`, Immer). | `state.items.push(x); setState(state)`; `props.x.y = ...`. | high |
| REACT-023 | **Dependency arrays are honest** (no omitted deps to "make it work"; fix the cause — move functions inside the effect, use `useEffectEvent`/refs where appropriate). | `// eslint-disable-next-line react-hooks/exhaustive-deps`. | medium |

## 4. Effects ("You might not need an Effect")

| ID | Practice | Check | Sev |
|---|---|---|---|
| REACT-030 | **No effects for derived data**: compute during render (memoize only if expensive). | `useEffect(() => setFullName(first + " " + last), [first, last])`. | medium |
| REACT-031 | **No effects to handle user events**: put logic in the event handler. | Effects watching a "submitted" flag to send a request. | medium |
| REACT-032 | **No effect chains** (effect sets state that triggers another effect). | Several effects in sequence updating each other's deps. | medium |
| REACT-033 | **Resetting state on prop change via `key`**, not an effect that resets state. | `useEffect(() => setX(initial), [id])`. | low |
| REACT-034 | **Data fetching in effects handles races and cleanup** (ignore stale responses / `AbortController`) — or better, use a framework/server fetch or a data library (TanStack Query/SWR). | `useEffect(() => { fetch().then(setData) }, [id])` without cleanup. | medium |
| REACT-035 | **Effects that subscribe clean up** (listeners, intervals, sockets); external stores read via `useSyncExternalStore`. | `addEventListener`/`setInterval` without return cleanup. | high |

## 5. State management

| ID | Practice | Check | Sev |
|---|---|---|---|
| REACT-040 | **Minimal state; no duplicated or derivable state.** | State mirroring props; `filteredItems` stored alongside `items` + `filter`. | medium |
| REACT-041 | **State colocated** with the components that use it; lifted only as far as needed. | Everything in a global store or root component. | low |
| REACT-042 | **Complex/related state via `useReducer`** or discriminated union state (`{status: "idle"|"loading"|"success"|"error"}`) instead of independent booleans. | `isLoading`, `isError`, `data` set separately (GEN-052). | medium |
| REACT-043 | **Server state handled by a server-state tool** (TanStack Query, SWR, RSC/framework loaders) — not copied into Redux/Zustand/Context. | API responses manually cached in global client stores with hand-rolled invalidation. | medium |
| REACT-044 | **Context is for low-frequency, widely needed values** (theme, auth, locale); values memoized; contexts split by update frequency. | One giant context with rapidly changing values re-rendering the whole tree; `value={{...}}` new object each render. | medium |
| REACT-045 | **One client state approach per app** (not Redux + MobX + Zustand + Context all at once) (ARCH-018). | Multiple state libraries for the same job. | low |
| REACT-046 | **URL holds shareable UI state** (filters, tabs, pagination) via search params. | Filters lost on refresh/share. | info |

## 6. Rendering & performance

| ID | Practice | Check | Sev |
|---|---|---|---|
| REACT-050 | **Stable, unique `key`s** from data ids for dynamic lists; never array index for lists that reorder/insert/delete; never random keys. | `key={index}` on editable/sortable lists; `key={Math.random()}`. | medium |
| REACT-051 | **Memoization (`memo`, `useMemo`, `useCallback`) used where measured or where referential stability matters** — not blanket-wrapped everywhere (or let the React Compiler handle it). | Every function wrapped in `useCallback` with no memoized consumer; or obvious expensive work recomputed per render on large data. | low |
| REACT-052 | **Long lists virtualized** (TanStack Virtual, react-window). | Rendering thousands of rows. | medium |
| REACT-053 | **Code-splitting** heavy routes/components with `lazy` + `Suspense` (or framework equivalents). | Single huge bundle (see NEXT-073). | low |
| REACT-054 | **Non-urgent updates marked** with `useTransition`/`useDeferredValue` for responsive input on heavy renders. | Laggy typing in search-filter UIs. | info |

## 7. Forms & accessibility

| ID | Practice | Check | Sev |
|---|---|---|---|
| REACT-055 | **Semantic elements**: `<button>` for actions, `<a>`/`Link` for navigation — not clickable `div`s; landmarks and heading hierarchy. | `onClick` on `div`/`span` without role/keyboard handlers. | medium |
| REACT-056 | **Every input has an accessible label**; errors announced (`aria-invalid`, `aria-describedby`); focus managed after dialogs/route changes. | Placeholder-as-label; modals without focus trap (prefer accessible primitives: Radix, React Aria, Headless UI). | medium |
| REACT-057 | **Images have meaningful `alt`** (empty `alt=""` for decorative). | Missing alt. | low |
| REACT-058 | **Forms use a consistent approach** (native forms + Actions in React 19, or React Hook Form + schema resolver) with the same schema as the server. | Divergent client/server validation rules. | low |

## 8. Error handling & async UI

| ID | Practice | Check | Sev |
|---|---|---|---|
| REACT-059 | **Error boundaries** around independent UI regions (react-error-boundary or framework `error.tsx`); errors reported to tracking. | No boundaries → white screen on any render error. | medium |
| REACT-061 | **Every async view handles loading, empty and error states** (GEN-183). | `data.map` with no loading/error branch; crashes on empty arrays. | medium |
| REACT-062 | **Optimistic updates roll back on failure** (`useOptimistic` or query library patterns). | Optimistic UI never reconciled with server errors. | low |

## 9. Security

| ID | Practice | Check | Sev |
|---|---|---|---|
| REACT-060 | **`dangerouslySetInnerHTML` only with sanitized input** (DOMPurify) and ideally never with user content. | Occurrences with user/CMS data unsanitized. | high |
| REACT-063 | **No `javascript:` URLs from data in `href`/`src`**; validate URL schemes for user-provided links. | `<a href={user.website}>` without scheme validation. | medium |
| REACT-064 | **No secrets or privileged logic in client components** (anything in the bundle is public). | API keys in client code (SEC-002). | critical |

## 10. Testing

| ID | Practice | Check | Sev |
|---|---|---|---|
| REACT-070 | **React Testing Library**: test behavior the user sees; query by role/label/text (`getByRole("button", { name: /save/i })`), `data-testid` as last resort. | `container.querySelector`, class-name selectors, Enzyme-style `instance()`/`state()`. | medium |
| REACT-071 | **`@testing-library/user-event`** for interactions (over `fireEvent`), `await` its calls. | `fireEvent.change` everywhere; un-awaited user-event calls. | low |
| REACT-072 | **Async UI asserted with `findBy*`/`waitFor`**, no manual sleeps; no `act()` warnings left in output. | `setTimeout` in tests; console full of act warnings. | medium |
| REACT-073 | **No implementation-detail tests**: don't assert hook internals, state values, or that a child component received props — assert rendered outcome. | Tests mocking child components to check props. | medium |
| REACT-074 | **Snapshot tests are small and purposeful** (or replaced with explicit assertions). | Whole-page snapshots updated reflexively (TEST-067). | low |
| REACT-075 | **Custom hooks tested via `renderHook`** or through a component using them; logic extracted to pure functions tested directly. | Complex hooks untested. | low |
| REACT-076 | **A shared `render` helper** wraps providers (router, query client, theme) so tests stay short and consistent. | Provider setup copy-pasted per test file (TEST-068). | low |
| REACT-077 | **Accessibility checks in tests** (`jest-axe`/`vitest-axe`, Playwright `@axe-core/playwright`) for key screens. | None. | info |

## 11. Quick grep list

```bash
rg -n 'key=\{(index|i|idx)\}|key=\{Math\.random'                       # REACT-050
rg -n 'eslint-disable.*react-hooks'                                     # REACT-023
rg -n 'useEffect\(' -c                                                  # REACT-030..035 (hotspots: files with many effects)
rg -n 'dangerouslySetInnerHTML'                                         # REACT-060
rg -n '<div[^>]*onClick' -g '*.tsx'                                     # REACT-055
rg -n 'querySelector|\.instance\(\)|fireEvent\.' -g '*.test.tsx'        # REACT-070/071
rg -n 'useState' -c -g '*.tsx' | sort -t: -k2 -nr | head                # REACT-010 (components with many states)
rg -n 'href=\{[a-zA-Z_.]+\}' -g '*.tsx'                                 # REACT-063 (confirm source of value)
```
