# Report Template

`scripts/merge_findings.py` renders `report.md` in this structure. Sections marked
**(orchestrator)** contain `<!-- ORCHESTRATOR: ... -->` placeholders you must replace with your own
synthesis; everything else is generated from the findings files.

```markdown
# Codebase Audit — {repo name}

Date: {date} · Commit: {git sha if available} · Reviewers: {n} · Findings: {n}
(critical {n} · high {n} · medium {n} · low {n} · info {n})

## 1. Executive summary  (orchestrator)
3–6 sentences: overall health, the 2–3 most important risks, the single highest-leverage
improvement, and what the codebase already does well.

## 2. Scorecard  (orchestrator)
| Area | Grade (A–E) | Summary |
|---|---|---|
| Architecture & design | | |
| Code quality & smells | | |
| Error handling & reliability | | |
| Testing | | |
| Security | | |
| Dependencies & supply chain | | |
| Tooling & CI | | |
| Documentation | | |
Grades: A = exemplary, B = solid with minor gaps, C = workable with notable debt,
D = significant risk/debt, E = critical problems. Base grades on findings, not impressions.

## 3. Themes  (orchestrator)
Group related findings by root cause. For each theme: one paragraph, the finding IDs it covers,
and a suggested epic title.

## 4. Architecture as found
(from the architecture reviewer: summary + mermaid diagram)

## 5. Test portfolio
(from the testing reviewer: counts by type, untested critical modules)

## 6. Findings overview
### P0 — fix now
| ID | Title | Severity | Confidence | Effort | Category | Main location |
### P1 — next
### P2 — planned
### P3 — opportunistic

## 7. Finding details
One section per finding, identical to the issue body (below), headed `### AUD-001 · {title}`.

## 8. Strengths
Bullets collected from reviewers (deduplicated).

## 9. Coverage & method
Reviewers and scopes, files reviewed, skipped paths and why, stacks without a dedicated reference,
tools run. Findings are point-in-time and evidence-based; each cites rule IDs from the skill's
references.

## Appendix — Rule index
| Rule ID | Findings |
```

## Issue body (also written to `issues/AUD-xxx.md` and `issues.json`)

```markdown
**Severity:** high · **Confidence:** high · **Effort:** S · **Category:** error-handling
**Rules:** GEN-040, SMELL-055

### Problem
{impact}

### Evidence
- `path/to/file.ts:88-97`
- (… up to 10 locations; "+N more occurrences" if applicable)

```
{evidence}
```

### Recommendation
{recommendation}

### Acceptance criteria
- [ ] {criterion 1}
- [ ] {criterion 2}

<sub>Found by codebase-audit ({reviewer ids}) on {date}. ID: AUD-001</sub>
```

`issues.json` entries:

```json
{
  "id": "AUD-001",
  "title": "Propagate payment provider errors instead of swallowing them",
  "body": "<the markdown above>",
  "labels": ["audit", "severity:high", "category:error-handling", "effort:S", "lang:typescript"],
  "priority": "P0",
  "severity": "high",
  "confidence": "high",
  "effort": "S",
  "rule_ids": ["GEN-040", "SMELL-055"],
  "locations": [{"path": "...", "start_line": 88, "end_line": 97}],
  "reviewers": ["module-3"]
}
```

Creating GitHub issues from it (only when the user asks):

```bash
jq -c '.[]' issues.json | while read -r it; do
  id=$(jq -r .id <<<"$it")
  gh issue create --title "$(jq -r .title <<<"$it")" \
    --body-file "issues/$id.md" \
    $(jq -r '.labels[] | "--label \(.)"' <<<"$it")
done
```
(Labels must exist first: `gh label create severity:high` etc., or drop `--label`.)
