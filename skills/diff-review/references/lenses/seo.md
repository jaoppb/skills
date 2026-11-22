# SEO Lens

- **Role**: Technical SEO Engineer — crawlability, metadata, structured data, canonicals, and Core Web Vitals.
- **Tier**: `fast/balanced`
- **Activation Trigger**: Diff touches public-facing web pages, SSR/SSG routes, HTML `<head>`/metadata, OpenGraph/Twitter tags, `sitemap*`, `robots.txt`, canonicals, redirects, or JSON-LD structured data. Stay off for authenticated-only apps, APIs, CLIs, or internal tooling.
- **Delta Re-run Invalidation**:
  - Public routes/pages, layout/head components, `**/robots.txt`, `**/sitemap*`, metadata/OG builders, JSON-LD schemas
  - Redirect/rewrite configs (`next.config.*`, `vercel.json`, `_redirects`)
  - *Conservative fallback*: re-run whenever uncertain whether a fix alters public page rendering, URLs, or metadata.

## Check

- **Crawlability & indexing**: Are public pages accidentally marked `noindex` or blocked in `robots.txt`? Are private/auth/preview pages properly excluded?
- **Metadata & social cards**: Unique, descriptive `<title>` and `<meta name="description">`, plus valid OpenGraph / Twitter card tags (`og:title`, `og:description`, `og:image`, `og:url`)?
- **Canonicals & redirects**: Do pages emit self-referencing or intentional `<link rel="canonical">` without query-param duplication? Are URL renames backed by `301`/`308` redirects?
- **Structured data (JSON-LD)**: Does JSON-LD match visible page content and valid schema.org types without syntax errors?
- **SSR & Core Web Vitals**: Is critical indexable content server-rendered rather than hidden behind client-only fetch? Are hero images sized with explicit dimensions / `fetchpriority` to avoid CLS and LCP regressions?

## Presumptive Blockers

- **`blocker` (P0)**: Accidental `noindex` / `robots.txt` block on production public pages, broken canonicals pointing to wrong/localhost URLs, or broken URL migration without redirects.
- **`material` (P1)**: Missing/duplicate `<title>` or description on new public routes, invalid JSON-LD, client-only rendering of primary SEO content, or severe LCP/CLS regression.
