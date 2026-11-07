# Next.js (NEXT-*)

Applies when `next` is a dependency. Read together with `../index.md` (TS-*) and `../lib/react.md`
(REACT-*). Most rules target the **App Router** (`app/`); Pages Router (`pages/`) notes are marked.
Next.js evolves quickly (caching defaults, `middleware.ts` → `proxy.ts`, `"use cache"`): check the
installed version in `package.json`/lockfile and judge against the docs for **that** version. When
unsure whether a behavior applies to the installed version, lower `confidence` rather than guess.

## Contents
1. Tooling & config
2. Server vs Client Components
3. Data fetching & data access
4. Caching & rendering
5. Mutations: Server Actions & Route Handlers
6. Auth & security
7. Routing conventions & UX states
8. Performance
9. Testing
10. Quick grep list

---

## 1. Tooling & config

| ID | Practice | Check | Sev |
|---|---|---|---|
| NEXT-001 | **Builds fail on type and lint errors**: no `typescript.ignoreBuildErrors: true` or `eslint.ignoreDuringBuilds: true` in `next.config.*`. | Either flag set. | high |
| NEXT-002 | **Next.js ESLint rules on** (`eslint-config-next` / `@next/eslint-plugin-next` incl. `core-web-vitals`). | Missing. | low |
| NEXT-003 | **Next and React kept on patched versions** — the RSC stack has had critical advisories (e.g. the December 2025 React Server Components RCE affecting Next 15/16). | Version behind a security release; no update automation. | critical if a known advisory applies, else low |
| NEXT-004 | **One router per area**: App Router and Pages Router coexist only during an explicit migration. | Duplicate routes or patterns across `app/` and `pages/` with no migration plan. | low |
| NEXT-005 | **Security headers configured** (`headers()` in config or middleware/proxy): CSP (nonce-based for dynamic pages), HSTS, `X-Content-Type-Options`, `Referrer-Policy`, `frame-ancestors`. | None. | medium |

## 2. Server vs Client Components

| ID | Practice | Check | Sev |
|---|---|---|---|
| NEXT-010 | **Server Components by default; `"use client"` pushed to the leaves** (interactive islands). Layouts and pages stay server unless they truly need client state. | `"use client"` at the top of layouts/pages or large subtrees; most of `app/` is client. | medium |
| NEXT-011 | **Server-only code is guarded with `import "server-only"`** (DB clients, secrets, data-access modules) so accidental client import fails the build; `client-only` for browser-only modules. | Data-access modules without `server-only`. | medium |
| NEXT-012 | **Props crossing to Client Components are minimal, serializable DTOs** — never whole DB records, user objects with sensitive fields, or secrets. | Passing ORM entities/`user` rows to client components. | high |
| NEXT-013 | **No server secrets in client bundles**: only `NEXT_PUBLIC_*` vars are referenced in client code, and nothing secret is named `NEXT_PUBLIC_*` (SEC-002). | `NEXT_PUBLIC_*SECRET*`, `*KEY*` of private APIs; `process.env.X` in `"use client"` files. | critical |
| NEXT-014 | **Composition over boundary-crossing**: pass Server Components as `children` to Client Components instead of importing server code into client files. | Client components importing server modules. | medium |
| NEXT-015 | **Context providers wrapped in a small client component** placed as deep as possible. | Root layout made client to host providers. | low |

## 3. Data fetching & data access

| ID | Practice | Check | Sev |
|---|---|---|---|
| NEXT-020 | **Fetch on the server, close to where data is used** (Server Components); avoid client-side `useEffect` fetching for initial data. | `useEffect(() => fetch(...))` for page data. | medium |
| NEXT-021 | **Server Components don't call the app's own Route Handlers over HTTP** — call the data function directly. | `fetch("http://localhost:3000/api/...")` or `fetch(`${baseUrl}/api`)` in server code. | medium |
| NEXT-022 | **Centralized Data Access Layer (DAL)**: one server-only module per domain that performs auth checks and returns DTOs; pages/actions call it instead of querying the DB directly. | ORM calls scattered across pages, components and actions (ARCH-005). | medium |
| NEXT-023 | **No request waterfalls**: independent fetches started in parallel (`Promise.all`, or start promises then await), sequential only when dependent; use Suspense to stream slow parts. | Sequential `await`s of independent data in one component; nested components each awaiting in series. | medium |
| NEXT-024 | **Request-level deduplication** for data used in several components (`React.cache` for non-fetch calls). | Same DB query run several times per request. | low |
| NEXT-025 | **Client-side data fetching uses a proper library** (TanStack Query, SWR) when needed for interactivity — not hand-rolled effect state. | Hand-rolled loading/error state machines in effects (REACT-030). | low |

## 4. Caching & rendering

| ID | Practice | Check | Sev |
|---|---|---|---|
| NEXT-030 | **Caching is explicit and intentional for the installed version** (`fetch` cache options, `revalidate`, `"use cache"` + `cacheLife`/`cacheTag`, `unstable_cache`), documented near the data function. | Reliance on implicit defaults that changed between versions; nobody can say what's cached. | medium |
| NEXT-031 | **Per-user or sensitive data is never cached across users** (shared caches keyed without user identity; static rendering of personalized pages). | Cached functions returning session-dependent data; `force-static` on authenticated pages. | critical |
| NEXT-032 | **Mutations invalidate caches** (`revalidatePath`/`revalidateTag`/`updateTag`, `router.refresh()` client-side) consistently. | Writes with no revalidation → stale UI; or `revalidatePath("/", "layout")` everywhere (cache nuked). | medium |
| NEXT-033 | **Route segment config used deliberately**: `export const dynamic = "force-dynamic"` / `revalidate = 0` only where needed, not sprinkled to "fix" bugs. | Many segments forced dynamic with no comment. | low |
| NEXT-034 | **Static generation where possible** (`generateStaticParams` for known params; ISR for slowly-changing content). | Fully dynamic marketing/docs pages. | low |

## 5. Mutations: Server Actions & Route Handlers

| ID | Practice | Check | Sev |
|---|---|---|---|
| NEXT-040 | **Every Server Action is treated as a public HTTP endpoint**: it validates input with a schema and performs **authentication and authorization inside the action** (or the DAL it calls). | Actions trusting `formData`/args; actions relying only on the page being protected. | critical |
| NEXT-041 | **Server Actions return typed results** (`{ ok: true, data } \| { ok: false, error }`) for expected failures; don't throw for validation; never return raw errors/stack traces. | `throw new Error` for validation; returning `err.message` from DB errors. | medium |
| NEXT-042 | **Forms use progressive enhancement** (`<form action={action}>`, `useActionState`, `useFormStatus`), with pending/disabled states to prevent double submits. | `onClick` + manual fetch for simple forms; no pending state. | low |
| NEXT-043 | **Route Handlers (`route.ts`)** validate input, check auth, return correct status codes and a consistent error shape, set caching headers intentionally. | `return NextResponse.json({ error }, { status: 200 })`; no validation. | high |
| NEXT-044 | **Webhooks verify signatures** using the raw body before parsing. | Stripe/GitHub webhook handlers without signature verification. | critical |
| NEXT-045 | **Server Actions defined in dedicated `"use server"` modules** (e.g. `actions.ts` per feature), not inline closures capturing large scopes. | Inline actions closing over sensitive values (they're serialized/encrypted, but still a design smell). | low |

## 6. Auth & security

| ID | Practice | Check | Sev |
|---|---|---|---|
| NEXT-050 | **Middleware/proxy is not the only auth check.** It may redirect optimistically, but authorization must be enforced in the DAL/Server Actions/Route Handlers (middleware bypasses have happened, e.g. CVE-2025-29927, and matchers miss routes). | Auth only in `middleware.ts`/`proxy.ts`; pages/actions with no checks. | critical |
| NEXT-051 | **Session handling via a vetted library** (Auth.js, Clerk, Lucia-style patterns, iron-session) with secure cookie flags. | Hand-rolled JWT in cookies without verification/rotation. | high |
| NEXT-052 | **Object-level authorization in data access** (user can only read/mutate their own resources). | `getOrder(params.id)` without ownership check (IDOR). | critical |
| NEXT-053 | **`dangerouslySetInnerHTML` only with sanitized content** (REACT-060). | — | high |
| NEXT-054 | **Dynamic route params and search params validated** (they're user input; in recent versions they're async — `await params`). | `params.id` used directly in queries; unvalidated `searchParams`. | high |
| NEXT-055 | **Image optimization config restricts remote hosts** (`images.remotePatterns` specific, not wildcard). | `hostname: "**"`. | medium |
| NEXT-056 | **Redirect targets are validated** (no open redirects from `?next=` params). | `redirect(searchParams.next)`. | medium |

## 7. Routing conventions & UX states

| ID | Practice | Check | Sev |
|---|---|---|---|
| NEXT-060 | **`loading.tsx` / Suspense boundaries** for slow segments; **`error.tsx`** per significant segment (Client Component with reset); **`global-error.tsx`** at root; **`not-found.tsx`** + `notFound()` for missing resources. | Missing error boundaries → whole app error page; `return null` for missing entities. | medium |
| NEXT-061 | **Route groups and private folders** (`(group)`, `_components`) keep `app/` organized; colocate feature components, keep route files thin. | Business logic and large components inside `page.tsx` (ARCH-005). | low |
| NEXT-062 | **Metadata API** (`metadata`/`generateMetadata`) for titles/OG/canonical; `sitemap.ts`, `robots.ts` for public sites. | Hard-coded `<head>` tags; missing titles. | low |
| NEXT-063 | **`<Link>` for internal navigation**; `useRouter` only for programmatic cases. | `<a href="/internal">` for in-app routes; `router.push` in onClick for plain links. | low |
| NEXT-064 | *(Pages Router)* **`getServerSideProps` returns only needed, serializable fields** (everything returned is shipped to the client); API routes validate and auth like Route Handlers. | Returning full DB rows. | high |

## 8. Performance

| ID | Practice | Check | Sev |
|---|---|---|---|
| NEXT-070 | **`next/image`** with explicit sizes/`sizes` prop for responsive images; `priority`/`preload` for LCP image. | Raw `<img>` for content images (eslint `no-img-element`). | low |
| NEXT-071 | **`next/font`** for fonts (self-hosted, no layout shift). | `<link>` to Google Fonts in head. | low |
| NEXT-072 | **`next/script` with an appropriate `strategy`** for third-party scripts. | Blocking third-party scripts. | low |
| NEXT-073 | **Heavy client-only components lazy-loaded** (`next/dynamic`) and big libraries kept out of client bundles (check with `@next/bundle-analyzer`). | Charting/editor libs imported in shared client components. | medium |
| NEXT-074 | **Streaming** with Suspense to show shell fast; avoid blocking the whole page on the slowest query. | Single top-level await of everything. | low |

## 9. Testing

| ID | Practice | Check | Sev |
|---|---|---|---|
| NEXT-080 | **Business logic extracted from route files** into plain modules with unit tests (DAL, services, validators). | Logic only testable by rendering pages. | medium |
| NEXT-081 | **Server Actions and Route Handlers have tests** for validation errors, unauthenticated/unauthorized access, and success. | No tests calling actions/handlers. | high |
| NEXT-082 | **Client Components tested with Testing Library** (Vitest/Jest + jsdom/happy-dom); async Server Components covered by **E2E (Playwright)** since unit runners support them poorly. | No coverage of key pages at any level. | medium |
| NEXT-083 | **E2E runs against a production build** (`next build && next start`) in CI, not just `next dev`. | Playwright `webServer` uses `next dev` in CI. | low |
| NEXT-084 | **Network mocked with MSW**; `next/navigation` hooks mocked consistently in component tests. | Ad-hoc mocks per test file. | low |

## 10. Quick grep list

```bash
rg -l '^["'\'']use client["'\'']' app src | wc -l                      # NEXT-010 (ratio vs total)
rg -n '^["'\'']use client["'\'']' -g '**/layout.tsx' -g '**/page.tsx'   # NEXT-010
rg -n 'NEXT_PUBLIC_[A-Z_]*(SECRET|PRIVATE|TOKEN|KEY)'                   # NEXT-013
rg -n 'ignoreBuildErrors|ignoreDuringBuilds' next.config.*             # NEXT-001
rg -n '"use server"|'\''use server'\''' -l                              # NEXT-040 (then read each action)
rg -n 'fetch\([^)]*(localhost|/api/)' app src                           # NEXT-021
rg -n 'force-dynamic|force-static|revalidate\s*=' app                   # NEXT-031/033
rg -n 'remotePatterns|hostname:\s*["'\'']\*\*'                           # NEXT-055
rg -n 'redirect\((searchParams|params|req)'                             # NEXT-056
rg -n '<img ' -g '*.tsx'                                                # NEXT-070
```
