#!/usr/bin/env python3
"""Merge reviewer findings into a report and issue-ready files.

Usage:
    python3 merge_findings.py <audit-dir>

Reads   <audit-dir>/findings/*.json  (+ optional <audit-dir>/inventory.json)
Writes  <audit-dir>/report.md
        <audit-dir>/issues.json
        <audit-dir>/issues/AUD-xxx.md
        <audit-dir>/validation.md   (only if some findings were malformed)

Standard library only. See references/finding-format.md for the input schema.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

SEVERITIES = ["critical", "high", "medium", "low", "info"]
SEV_W = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}
CONF_W = {"high": 1.0, "medium": 0.8, "low": 0.5}
EFFORTS = ["S", "M", "L"]
CATEGORIES = {"architecture", "maintainability", "code-smell", "error-handling", "testing",
              "security", "performance", "concurrency", "data-integrity", "types", "dependencies",
              "tooling", "observability", "documentation", "accessibility"}
RULE_RE = re.compile(r"^[A-Z]+-\d{3}$")
MAX_LOCATIONS = 10


def band(priority: float) -> str:
    if priority >= 4.0:
        return "P0"
    if priority >= 3.0:
        return "P1"
    if priority >= 2.0:
        return "P2"
    return "P3"


# ------------------------------------------------------------------------------------------
# Loading & validation
# ------------------------------------------------------------------------------------------

def validate(f: dict, src: str, idx: int, problems: list[str]) -> dict | None:
    where = f"{src} finding #{idx + 1}"
    errs = []
    title = str(f.get("title", "")).strip()
    if not title:
        errs.append("missing title")
    rules = f.get("rule_ids") or []
    if isinstance(rules, str):
        rules = [rules]
    bad_rules = [r for r in rules if not RULE_RE.match(str(r))]
    if not rules:
        errs.append("missing rule_ids")
    elif bad_rules:
        problems.append(f"{where}: unusual rule ids {bad_rules} (kept)")
    sev = str(f.get("severity", "")).lower()
    if sev not in SEV_W:
        errs.append(f"invalid severity {sev!r}")
    conf = str(f.get("confidence", "medium")).lower()
    if conf not in CONF_W:
        problems.append(f"{where}: invalid confidence {conf!r}, using medium")
        conf = "medium"
    eff = str(f.get("effort", "M")).upper()
    if eff not in EFFORTS:
        problems.append(f"{where}: invalid effort {eff!r}, using M")
        eff = "M"
    cat = str(f.get("category", "maintainability")).lower()
    if cat not in CATEGORIES:
        problems.append(f"{where}: unknown category {cat!r}, using maintainability")
        cat = "maintainability"
    locs = []
    for loc in f.get("locations") or []:
        if isinstance(loc, str):
            m = re.match(r"^(.*?):(\d+)(?:-(\d+))?$", loc)
            loc = {"path": m.group(1), "start_line": int(m.group(2)),
                   "end_line": int(m.group(3) or m.group(2))} if m else {"path": loc}
        if isinstance(loc, dict) and loc.get("path"):
            locs.append({k: loc[k] for k in ("path", "start_line", "end_line") if k in loc})
    if not locs:
        errs.append("no locations")
    for key in ("impact", "recommendation"):
        if not str(f.get(key, "")).strip():
            errs.append(f"missing {key}")
    if errs:
        problems.append(f"{where}: DROPPED ({'; '.join(errs)}) — title: {title[:80]!r}")
        return None
    ac = f.get("acceptance_criteria") or []
    if isinstance(ac, str):
        ac = [ac]
    if not ac:
        problems.append(f"{where}: no acceptance_criteria")
    return {
        "title": title,
        "rule_ids": sorted({str(r) for r in rules}),
        "category": cat,
        "severity": sev,
        "confidence": conf,
        "effort": eff,
        "locations": locs,
        "occurrences": max(int(f.get("occurrences") or len(locs)), len(locs)),
        "evidence": str(f.get("evidence", "")).strip(),
        "impact": str(f["impact"]).strip(),
        "recommendation": str(f["recommendation"]).strip(),
        "acceptance_criteria": [str(a).strip() for a in ac if str(a).strip()],
        "tags": sorted({str(t) for t in (f.get("tags") or [])}),
        "reviewers": [src],
    }


def load(audit: Path):
    problems: list[str] = []
    findings: list[dict] = []
    meta: dict[str, dict] = {}
    fdir = audit / "findings"
    files = sorted(fdir.glob("*.json")) if fdir.is_dir() else []
    if not files:
        problems.append(f"no findings files in {fdir}")
    for path in files:
        try:
            data = json.loads(path.read_text())
        except Exception as e:  # noqa: BLE001
            problems.append(f"{path.name}: invalid JSON ({e}) — reviewer should be re-run")
            continue
        if isinstance(data, list):
            data = {"findings": data}
        src = str(data.get("reviewer") or path.stem)
        meta[src] = {k: v for k, v in data.items() if k != "findings"}
        for i, f in enumerate(data.get("findings") or []):
            if not isinstance(f, dict):
                problems.append(f"{path.name} finding #{i + 1}: not an object")
                continue
            v = validate(f, src, i, problems)
            if v:
                findings.append(v)
    return findings, meta, problems


# ------------------------------------------------------------------------------------------
# Dedupe
# ------------------------------------------------------------------------------------------

def norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", t.lower()).strip()


def overlaps(a: dict, b: dict) -> bool:
    for la in a["locations"]:
        for lb in b["locations"]:
            if la["path"] != lb["path"]:
                continue
            if "start_line" not in la or "start_line" not in lb:
                return True
            a1, a2 = la["start_line"], la.get("end_line", la["start_line"])
            b1, b2 = lb["start_line"], lb.get("end_line", lb["start_line"])
            if a1 <= b2 + 3 and b1 <= a2 + 3:
                return True
    return False


def same(a: dict, b: dict) -> bool:
    shared_rule = bool(set(a["rule_ids"]) & set(b["rule_ids"]))
    if shared_rule and overlaps(a, b):
        return True
    return shared_rule and norm_title(a["title"]) == norm_title(b["title"])


def merge_into(a: dict, b: dict) -> None:
    a["rule_ids"] = sorted(set(a["rule_ids"]) | set(b["rule_ids"]))
    if SEV_W[b["severity"]] > SEV_W[a["severity"]]:
        a["severity"] = b["severity"]
    if CONF_W[b["confidence"]] > CONF_W[a["confidence"]]:
        a["confidence"] = b["confidence"]
    if EFFORTS.index(b["effort"]) > EFFORTS.index(a["effort"]):
        a["effort"] = b["effort"]
    seen = {(l["path"], l.get("start_line")) for l in a["locations"]}
    for l in b["locations"]:
        if (l["path"], l.get("start_line")) not in seen:
            a["locations"].append(l)
            seen.add((l["path"], l.get("start_line")))
    a["occurrences"] = max(a["occurrences"], b["occurrences"], len(a["locations"]))
    for key in ("evidence", "impact", "recommendation"):
        if len(b[key]) > len(a[key]):
            a[key] = b[key]
    for c in b["acceptance_criteria"]:
        if c not in a["acceptance_criteria"]:
            a["acceptance_criteria"].append(c)
    a["tags"] = sorted(set(a["tags"]) | set(b["tags"]))
    a["reviewers"] = sorted(set(a["reviewers"]) | set(b["reviewers"]))


def dedupe(findings: list[dict]) -> tuple[list[dict], int]:
    out: list[dict] = []
    merged = 0
    for f in findings:
        for g in out:
            if same(f, g):
                merge_into(g, f)
                merged += 1
                break
        else:
            out.append(f)
    return out, merged


# ------------------------------------------------------------------------------------------
# Rendering
# ------------------------------------------------------------------------------------------

def loc_str(l: dict) -> str:
    if "start_line" in l:
        end = l.get("end_line", l["start_line"])
        return f"{l['path']}:{l['start_line']}" + (f"-{end}" if end != l["start_line"] else "")
    return l["path"]


def issue_body(f: dict, today: str) -> str:
    locs = f["locations"][:MAX_LOCATIONS]
    extra = f["occurrences"] - len(locs)
    lines = [
        f"**Severity:** {f['severity']} · **Confidence:** {f['confidence']} · "
        f"**Effort:** {f['effort']} · **Category:** {f['category']} · **Priority:** {f['priority_band']}",
        f"**Rules:** {', '.join(f['rule_ids'])}",
        "",
        "### Problem",
        f["impact"],
        "",
        "### Evidence",
    ]
    lines += [f"- `{loc_str(l)}`" for l in locs]
    if extra > 0:
        lines.append(f"- … +{extra} more occurrence{'s' if extra > 1 else ''}")
    if f["evidence"]:
        fence = "````" if "```" in f["evidence"] else "```"
        lines += ["", fence, f["evidence"], fence]
    lines += ["", "### Recommendation", f["recommendation"], "", "### Acceptance criteria"]
    lines += [f"- [ ] {c}" for c in f["acceptance_criteria"]] or ["- [ ] (to be defined)"]
    lines += ["", f"<sub>Found by codebase-audit ({', '.join(f['reviewers'])}) on {today}. "
                  f"ID: {f['id']}</sub>"]
    return "\n".join(lines)


def md_cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def render_report(findings, meta, inventory, problems, merged, today) -> str:
    sev_counts = Counter(f["severity"] for f in findings)
    repo = (inventory or {}).get("repo_name", "repository")
    sha = ((inventory or {}).get("git") or {}).get("sha") or "n/a"
    out = [
        f"# Codebase Audit — {repo}",
        "",
        f"Date: {today} · Commit: {sha} · Reviewers: {len(meta)} · Findings: {len(findings)} "
        f"(" + " · ".join(f"{s} {sev_counts.get(s, 0)}" for s in SEVERITIES) + ")",
        "",
        "## 1. Executive summary",
        "",
        "<!-- ORCHESTRATOR: 3–6 sentences — overall health, the 2–3 most important risks, the single "
        "highest-leverage improvement, and what the codebase does well. -->",
        "",
        "## 2. Scorecard",
        "",
        "<!-- ORCHESTRATOR: grade each area A–E based on the findings below. -->",
        "",
        "| Area | Grade | Summary |",
        "|---|---|---|",
    ]
    for area in ["Architecture & design", "Code quality & smells", "Error handling & reliability",
                 "Testing", "Security", "Dependencies & supply chain", "Tooling & CI",
                 "Documentation"]:
        out.append(f"| {area} | ? | |")
    out += ["", "Grades: A exemplary · B solid, minor gaps · C workable, notable debt · "
                "D significant risk/debt · E critical problems.", "",
            "## 3. Themes", "",
            "<!-- ORCHESTRATOR: group related findings by root cause; per theme one paragraph, the "
            "AUD ids it covers, and a suggested epic title. -->", ""]

    # Architecture
    out += ["## 4. Architecture as found", ""]
    arch = [m for m in meta.values() if m.get("architecture_summary")]
    if arch:
        for m in arch:
            out += [m["architecture_summary"], ""]
            if m.get("architecture_mermaid"):
                diagram = m["architecture_mermaid"].strip()
                if not diagram.startswith("```"):
                    diagram = f"```mermaid\n{diagram}\n```"
                out += [diagram, ""]
    else:
        out += ["_No architecture reviewer output._", ""]

    # Tests
    out += ["## 5. Test portfolio", ""]
    tp = [m["test_portfolio"] for m in meta.values() if m.get("test_portfolio")]
    if tp:
        t = tp[0]
        out += ["| Unit files | Integration files | E2E files | Other |", "|---|---|---|---|",
                f"| {t.get('unit_files', '?')} | {t.get('integration_files', '?')} | "
                f"{t.get('e2e_files', '?')} | {t.get('other', '?')} |", ""]
        if t.get("untested_critical_modules"):
            out += ["Untested critical modules:", ""]
            out += [f"- `{p}`" for p in t["untested_critical_modules"]] + [""]
        if t.get("notes"):
            out += [t["notes"], ""]
    elif inventory:
        out += [f"From inventory (heuristic): {json.dumps(inventory.get('tests', {}))}", ""]
    else:
        out += ["_No testing reviewer output._", ""]

    # Overview tables
    out += ["## 6. Findings overview", ""]
    titles = {"P0": "P0 — fix now", "P1": "P1 — next", "P2": "P2 — planned",
              "P3": "P3 — opportunistic"}
    for b in ["P0", "P1", "P2", "P3"]:
        group = [f for f in findings if f["priority_band"] == b]
        out += [f"### {titles[b]} ({len(group)})", ""]
        if not group:
            out += ["_None._", ""]
            continue
        out += ["| ID | Title | Severity | Confidence | Effort | Category | Main location |",
                "|---|---|---|---|---|---|---|"]
        for f in group:
            out.append(f"| [{f['id']}](#{f['id'].lower()}) | {md_cell(f['title'])} | {f['severity']} | "
                       f"{f['confidence']} | {f['effort']} | {f['category']} | "
                       f"`{md_cell(loc_str(f['locations'][0]))}` |")
        out.append("")

    # Details
    out += ["## 7. Finding details", ""]
    for f in findings:
        out += [f'<a id="{f["id"].lower()}"></a>', f"### {f['id']} · {f['title']}", "", f["body"], ""]

    # Strengths
    out += ["## 8. Strengths", ""]
    strengths = []
    for m in meta.values():
        for s in m.get("strengths") or []:
            if s and s not in strengths:
                strengths.append(s)
    out += ([f"- {s}" for s in strengths] or ["_None reported._"]) + [""]

    # Coverage
    out += ["## 9. Coverage & method", "", "| Reviewer | Scope | Files reviewed | Skipped |",
            "|---|---|---|---|"]
    for name, m in sorted(meta.items()):
        cov = m.get("coverage") or {}
        scope = m.get("scope") or []
        scope_s = ", ".join(f"`{s}`" for s in scope[:4]) + (f" +{len(scope) - 4}" if len(scope) > 4 else "")
        skipped = cov.get("skipped") or []
        skipped_s = "; ".join(f"`{s.get('path')}` ({s.get('reason')})" if isinstance(s, dict) else str(s)
                              for s in skipped[:5]) + (f" +{len(skipped) - 5}" if len(skipped) > 5 else "")
        out.append(f"| {name} | {md_cell(scope_s) or '-'} | {cov.get('files_reviewed', '?')} | "
                   f"{md_cell(skipped_s) or '-'} |")
    out.append("")
    if inventory:
        t = inventory.get("totals", {})
        out.append(f"Repository: {t.get('loc')} LOC in {t.get('code_files')} code files "
                   f"({t.get('generated_files_excluded', 0)} generated files excluded).")
        if inventory.get("languages_without_reference"):
            out.append("Languages without a dedicated reference (generic rules only): "
                       + ", ".join(inventory["languages_without_reference"]) + ".")
        nr = sorted({d for p in inventory.get("packages", []) for d in p.get("notable_without_reference", [])})
        if nr:
            out.append("Frameworks/libraries without a dedicated reference: " + ", ".join(nr) + ".")
        out.append("")
    out += [f"Findings were deduplicated across reviewers ({merged} merged). Each finding cites "
            "rule IDs from the codebase-audit references and is point-in-time evidence.", ""]
    if problems:
        out += [f"{len(problems)} validation notes — see `validation.md`.", ""]

    # Rule index
    rules = defaultdict(list)
    for f in findings:
        for r in f["rule_ids"]:
            rules[r].append(f["id"])
    out += ["## Appendix — Rule index", "", "| Rule ID | Findings |", "|---|---|"]
    for r in sorted(rules):
        out.append(f"| {r} | {', '.join(rules[r])} |")
    out.append("")
    return "\n".join(out)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    audit = Path(sys.argv[1]).resolve()
    inventory = None
    inv_path = audit / "inventory.json"
    if inv_path.exists():
        try:
            inventory = json.loads(inv_path.read_text())
        except Exception:  # noqa: BLE001
            inventory = None
    today = (inventory or {}).get("date") or date.today().isoformat()

    findings, meta, problems = load(audit)
    findings, merged = dedupe(findings)
    for f in findings:
        f["priority"] = round(SEV_W[f["severity"]] * CONF_W[f["confidence"]], 2)
        f["priority_band"] = band(f["priority"])
    findings.sort(key=lambda f: (-f["priority"], EFFORTS.index(f["effort"]),
                                 SEVERITIES.index(f["severity"]), f["title"]))
    for i, f in enumerate(findings, 1):
        f["id"] = f"AUD-{i:03d}"
        f["locations"] = f["locations"][:MAX_LOCATIONS] if len(f["locations"]) > MAX_LOCATIONS \
            else f["locations"]
        f["body"] = issue_body(f, today)

    issues_dir = audit / "issues"
    issues_dir.mkdir(parents=True, exist_ok=True)
    for old in issues_dir.glob("AUD-*.md"):
        old.unlink()
    issues = []
    for f in findings:
        (issues_dir / f"{f['id']}.md").write_text(f["body"] + "\n")
        labels = ["audit", f"severity:{f['severity']}", f"category:{f['category']}",
                  f"effort:{f['effort']}", f"priority:{f['priority_band']}"] + \
                 [t for t in f["tags"] if t.startswith(("lang:", "framework:", "lib:"))]
        issues.append({
            "id": f["id"], "title": f["title"], "body": f["body"], "labels": labels,
            "priority": f["priority_band"], "priority_score": f["priority"],
            "severity": f["severity"], "confidence": f["confidence"], "effort": f["effort"],
            "category": f["category"], "rule_ids": f["rule_ids"], "locations": f["locations"],
            "occurrences": f["occurrences"], "reviewers": f["reviewers"],
        })
    (audit / "issues.json").write_text(json.dumps(issues, indent=2) + "\n")
    (audit / "report.md").write_text(render_report(findings, meta, inventory, problems, merged, today))
    vpath = audit / "validation.md"
    if problems:
        vpath.write_text("# Validation notes\n\n" + "\n".join(f"- {p}" for p in problems) + "\n")
    elif vpath.exists():
        vpath.unlink()

    sev = Counter(f["severity"] for f in findings)
    bands = Counter(f["priority_band"] for f in findings)
    print(f"reviewers: {len(meta)}  findings: {len(findings)} (merged {merged} duplicates)")
    print("severity: " + ", ".join(f"{s}={sev.get(s, 0)}" for s in SEVERITIES))
    print("priority: " + ", ".join(f"{b}={bands.get(b, 0)}" for b in ["P0", "P1", "P2", "P3"]))
    dropped = sum(1 for p in problems if "DROPPED" in p or "invalid JSON" in p)
    if problems:
        print(f"validation notes: {len(problems)} ({dropped} dropped/unreadable) -> {vpath}")
    print(f"wrote {audit / 'report.md'}, {audit / 'issues.json'}, {issues_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
