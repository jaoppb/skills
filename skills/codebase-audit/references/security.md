# Secure Coding & Supply Chain (SEC-*)

A defensive code-review checklist aligned with the OWASP Top 10 (2021/2025), OWASP ASVS and the
CWE Top 25. The reviewer's job is to spot weaknesses and recommend fixes — never to write or run
exploits, probe live systems, or use any secret it finds. If a secret is found, report its
**location and type only**, never its value, and recommend rotation.

## How to review

1. Identify trust boundaries: HTTP handlers, server actions, CLI args, file uploads, message
   consumers, webhooks, env/config, third-party API responses, deserialization points.
2. For each boundary check validation, authentication, authorization, output encoding, and error
   handling.
3. Scan manifests/lockfiles and run available audit tools (`npm audit --json`, `cargo audit`,
   `cargo deny check`) if allowed; report only advisories that plausibly affect this code.
4. Grep for high-signal patterns (listed per rule) and confirm by reading the surrounding code.

## Checks

| ID | Area | Practice | Detection hints | Sev |
|---|---|---|---|---|
| SEC-001 | Secrets | No credentials, tokens, private keys or connection strings in code, config, tests, fixtures, or committed `.env`. | Patterns: `-----BEGIN`, `AKIA`, `sk_live_`, `ghp_`, `xox[bp]-`, `password\s*=`, `api[_-]?key`, JWTs (`eyJ`), URLs with `user:pass@`. Check `.gitignore` covers `.env*`. | critical |
| SEC-002 | Secrets | Client bundles never contain server secrets. | Secrets in `NEXT_PUBLIC_*`/`VITE_*` vars; server keys imported in client components. | critical |
| SEC-010 | Injection | Parameterized queries / query builders only. | String concatenation or template literals into SQL (`` `SELECT ... ${` ``, `format!("SELECT ... {}`), raw query APIs with interpolation. | critical |
| SEC-011 | Injection | No shell command construction from input. | `exec`, `execSync`, `spawn` with `shell: true`, `std::process::Command::new("sh").arg("-c")` with interpolated input. | critical |
| SEC-012 | Injection | No dynamic code evaluation of input. | `eval`, `new Function`, `vm.runInContext`, template engines with user templates. | high |
| SEC-013 | XSS | Output is encoded by default; raw HTML only after sanitization. | `dangerouslySetInnerHTML`, `innerHTML =`, `v-html`, markdown rendered without sanitizer (DOMPurify). | high |
| SEC-014 | Path traversal | File paths from input are normalized and constrained to a base dir. | `path.join(base, userInput)` without check; `fs.readFile(req.query...)`; Rust `Path::join` with input. | high |
| SEC-015 | SSRF | Outbound requests to user-supplied URLs are allow-listed. | `fetch(req.body.url)`, image proxies, webhooks without host validation. | high |
| SEC-016 | Deserialization | No unsafe deserialization of untrusted data; schema-validate parsed JSON. | `yaml.load` unsafe modes, `pickle`-like formats, `JSON.parse` result used without validation. | high |
| SEC-017 | Prototype pollution (JS) | Deep merge / object assignment from input guards `__proto__`, `constructor`. | Custom deep-merge utilities; `Object.assign(target, req.body)`. | medium |
| SEC-018 | ReDoS | Regexes on untrusted input avoid catastrophic backtracking. | Nested quantifiers `(a+)+`, `(.*)*` applied to request data. | medium |
| SEC-020 | AuthN | Authentication via a vetted library/provider; passwords hashed with argon2/bcrypt/scrypt. | Hand-rolled JWT verification; `md5`/`sha1`/`sha256` for passwords; `jwt.decode` without verify; `alg: none` accepted. | critical |
| SEC-021 | AuthZ | Authorization checked server-side on every protected operation, per resource (object-level). | Handlers fetching by id without ownership check (IDOR); checks only in UI/middleware matching paths; server actions without auth. | critical |
| SEC-022 | Sessions | Cookies `HttpOnly`, `Secure`, `SameSite`; session rotation on login; CSRF protection for cookie-auth state changes. | Cookie set without flags; state-changing GET endpoints. | high |
| SEC-023 | Rate limiting | Login, signup, password reset, expensive endpoints are rate-limited. | No limiter middleware on auth routes. | medium |
| SEC-030 | Crypto | Standard libraries and algorithms; secure randomness for tokens. | `Math.random()`/`rand::random` (non-CSPRNG) for tokens/ids; custom crypto; ECB mode; hard-coded IVs/keys. | high |
| SEC-031 | Transport | TLS everywhere; certificate verification never disabled. | `rejectUnauthorized: false`, `NODE_TLS_REJECT_UNAUTHORIZED=0`, `danger_accept_invalid_certs(true)`. | high |
| SEC-040 | Headers & CORS | Security headers (CSP, HSTS, X-Content-Type-Options, frame-ancestors); CORS restricted. | `Access-Control-Allow-Origin: *` with credentials; no CSP. | medium |
| SEC-041 | Error exposure | No stack traces/internal details to clients (GEN-047). | Error middleware returning `err.stack`. | medium |
| SEC-042 | Logging | No secrets/PII in logs (GEN-111); security events logged (auth failures, permission denials). | Logging tokens, headers, full bodies. | high |
| SEC-043 | Uploads | File uploads size-limited, type-validated by content, stored outside web root, served with safe headers. | Trusting `Content-Type`/extension; unlimited body size. | high |
| SEC-050 | Least privilege | CI tokens, cloud roles, DB users scoped minimally; GitHub Actions `permissions:` set. | Workflows without `permissions`; `pull_request_target` checking out PR code; secrets available to fork PRs. | high |
| SEC-051 | CI supply chain | Third-party actions pinned to commit SHA; no `curl | sh` in CI from untrusted sources. | `uses: some/action@main`. | medium |
| SEC-052 | Containers | Non-root user, minimal base image, no secrets in image layers, pinned base image digest. | `USER` absent; `COPY .env`; `latest` tags. | medium |
| SEC-060 | Dependencies | No known-vulnerable deps in reachable code; audit in CI (GEN-121). | Audit output; no `npm audit`/`cargo audit`/`cargo deny` step. | high/medium |
| SEC-061 | Dependencies | Install scripts and new deps reviewed; lockfile integrity. | Typosquat-looking names; deps from git URLs/tarballs without pinning. | medium |
| SEC-070 | Memory safety (Rust/native) | `unsafe` blocks minimal, justified with `// SAFETY:` comments, and tested (Miri where possible). | See RS-040..RS-044. | high |
| SEC-080 | Data protection | PII minimized, encrypted at rest where required, retention defined. | PII in plain-text logs/caches; no deletion path. | medium |

## Recommended tooling (when missing)

- Secrets: `gitleaks` or `trufflehog` in CI and pre-commit; GitHub secret scanning/push protection.
- SAST: Semgrep (rules for TS/React/Next.js and Rust), CodeQL (JS/TS; Rust support where available), `eslint-plugin-security`.
- Dependencies: Dependabot/Renovate, `npm audit`/`pnpm audit`, `cargo audit`, `cargo deny`, OSV-Scanner.
- Containers/IaC: Trivy, Checkov.
