# Reviewer Contract

Every `diff-review` reviewer (built-in lens or external specialist) follows this contract. Lens guides do not repeat it.

## Read-Only

- Report findings only. Edit nothing, write nothing, and run no mutating commands.
- Judge only through your lens; leave other domains to their lenses.
- Round 1: review the full diff and changed-file list. Round N+1: review the delta, the changed-file list, and your own ledger. Open the full diff (passed as a `/tmp` path) or specific files only when you need more context. Do not re-litigate settled findings.

## Severities

- `blocker` (P0): must fix before approval.
- `material` (P1): must fix before approval.
- `nitpick` (P2/P3): non-blocking; the author may fix or reject with a written reason.
- `out-of-scope`: may be deferred with a written reason.

Approve only with **zero `blocker` and zero `material` findings**.

## Output Format

One line per finding, no preamble, no praise, no summary, no restating the diff:

```text
<severity> | <file>:<line> | <one-line issue> | <one-line fix>
verdict: approve|reject
```

With zero findings, output exactly `approve` and nothing else.
