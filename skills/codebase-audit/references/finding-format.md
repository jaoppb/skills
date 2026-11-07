# Finding Format

Every reviewer writes exactly one JSON file: `<audit-dir>/findings/<reviewer>.json`.
`scripts/merge_findings.py` validates it, so stick to the schema — malformed entries are reported
back to the orchestrator and may cost a re-run.

## Schema

```json
{
  "reviewer": "module-3",
  "scope": ["packages/api/src/orders", "packages/api/src/payments"],
  "coverage": {
    "files_reviewed": 42,
    "skipped": [{ "path": "packages/api/src/generated", "reason": "generated code" }],
    "notes": "Read every non-generated file; skimmed fixtures."
  },
  "strengths": [
    "Order state machine is modeled as a discriminated union with exhaustive handling."
  ],
  "findings": [
    {
      "title": "Propagate payment provider errors instead of swallowing them",
      "rule_ids": ["GEN-040", "SMELL-055"],
      "category": "error-handling",
      "severity": "high",
      "confidence": "high",
      "effort": "S",
      "locations": [
        { "path": "packages/api/src/payments/charge.ts", "start_line": 88, "end_line": 97 }
      ],
      "occurrences": 1,
      "evidence": "catch (e) { logger.warn(e); return { ok: true } }  // charge failure reported as success",
      "impact": "A failed charge is reported to the caller as successful, so orders ship unpaid and the failure is only visible as a warning log.",
      "recommendation": "Return a typed failure (e.g. `PaymentDeclined | ProviderUnavailable`) and let the order service decide; map to 402/503 at the HTTP edge.",
      "acceptance_criteria": [
        "charge() never returns ok:true when the provider call throws",
        "Unit tests cover declined and provider-timeout cases",
        "HTTP layer maps each failure to a distinct status code"
      ],
      "tags": ["lang:typescript"]
    }
  ]
}
```

### Field rules

| Field | Rule |
|---|---|
| `title` | Imperative, issue-ready, ≤ 90 chars, says the fix not the complaint ("Add …", "Extract …", "Validate …"). |
| `rule_ids` | ≥ 1 ID from the references. Use `GEN-000` only when no rule fits, and explain in `impact`. |
| `category` | One of: `architecture`, `maintainability`, `code-smell`, `error-handling`, `testing`, `security`, `performance`, `concurrency`, `data-integrity`, `types`, `dependencies`, `tooling`, `observability`, `documentation`, `accessibility`. |
| `severity` | `critical` \| `high` \| `medium` \| `low` \| `info` — use the rubric below. |
| `confidence` | `high` (verified in code) \| `medium` (strong signals, some assumption) \| `low` (suspicion worth a look). |
| `effort` | `S` (< ½ day, local change) \| `M` (½–3 days, a few files) \| `L` (> 3 days, cross-cutting/design change). |
| `locations` | ≥ 1 entry with repo-relative `path`; `start_line`/`end_line` when the finding is about specific lines; omit lines for file- or repo-level findings. Max ~10 entries — list the most representative ones. |
| `occurrences` | Total number of places the pattern appears (≥ number of locations). |
| `evidence` | ≤ 5 lines: a short code excerpt or a concrete observation ("no file under `src/billing` has a test"). Never paste secret values — write `<redacted>`. |
| `impact` | 1–3 sentences on the concrete consequence in this codebase. |
| `recommendation` | 1–4 sentences on what to change; name the refactoring/pattern/tool. |
| `acceptance_criteria` | 1–4 verifiable checks a PR reviewer can tick. |
| `tags` | Optional: `lang:<x>`, `framework:<x>`, `lib:<x>`, `area:<path>`. |

## Severity rubric

Severity reflects **consequence × likelihood in this codebase**, not how unpleasant the code looks.

| Severity | Meaning | Examples |
|---|---|---|
| **critical** | Exploitable security hole, data loss/corruption, or production outage likely. Fix now. | SQL injection on a reachable endpoint; secrets committed; missing authz on data-mutating route; data race on shared money state. |
| **high** | Real defects likely or significant risk on important paths; blocks safe change. | Swallowed errors in payment flow; no tests for auth module; `unwrap()` on request input; N+1 on hot endpoint; no CI. |
| **medium** | Meaningful maintainability/reliability cost; will cause bugs or slow work over time. | God module on a frequently changed path; business logic in handlers; flaky test suite; missing integration tests for repositories. |
| **low** | Local quality issue; worth fixing opportunistically. | Long function in stable code; magic numbers; weak test names; missing `.env.example`. |
| **info** | Observation or optional improvement; no defect implied. | Consider mutation testing; consider ADRs. |

Lower one level when the code is unreachable, internal-only, behind a feature flag that's off, or
scheduled for removal. Raise one level when it sits on an auth/money/data-integrity path or a
high-churn file with no tests. Use `confidence` (not severity) to express uncertainty.

## Priority (computed by the merge script)

`priority = severity_weight × confidence_weight`, ties broken by smaller effort first.
Weights — severity: critical 5, high 4, medium 3, low 2, info 1; confidence: high 1.0, medium 0.8,
low 0.5. The report groups by priority band: **P0** (≥ 4.0), **P1** (≥ 3.0), **P2** (≥ 2.0), **P3** (rest).
