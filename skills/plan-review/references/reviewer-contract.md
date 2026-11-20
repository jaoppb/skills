# Reviewer Contract

Every `plan-review` reviewer (built-in lens or external specialist) follows this contract. Lens guides do not repeat it.

## Read-Only

- Report findings (and concrete suggested rewrites/splits) only. Edit nothing, mutate no tracker issues, and run no shell, write, network, or MCP tools.
- Judge only through your lens; leave other domains to their lenses.
- Round 1: review the full snapshot (`/tmp/plan-<slug>-r1.md`). Round N+1: review the revision delta and your own ledger. Open the full snapshot (passed as a `/tmp` path) or repository files only when you need more context. Do not re-litigate settled findings.

## Severities

- `blocker` (P0): must resolve before implementation starts.
- `material` (P1): must resolve before approval.
- `nitpick` (P2/P3): non-blocking; the author may incorporate or reject with a written reason.
- `out-of-scope`: may be deferred with a written reason.

Approve only with **zero `blocker` and zero `material` findings**.

## Output Format

One line per finding, no preamble, no praise, no summary, no restating the plan:

```text
<severity> | <issue or section> | <one-line issue> | <one-line fix>
verdict: approve|reject
```

With zero findings, output exactly `approve` and nothing else.
