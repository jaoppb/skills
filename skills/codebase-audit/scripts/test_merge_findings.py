#!/usr/bin/env python3
"""Tests for merge_findings.py."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import merge_findings as mf  # noqa: E402


def make_finding(
    *,
    title: str = "Fix issue",
    rule_ids: list[str] | None = None,
    category: str = "maintainability",
    severity: str = "medium",
    confidence: str = "medium",
    effort: str = "M",
    locations: list[dict] | None = None,
    evidence: str = "ev",
    impact: str = "imp",
    recommendation: str = "rec",
    reviewers: list[str] | None = None,
) -> dict:
    locs = locations if locations is not None else [{"path": "src/a.rs", "start_line": 10, "end_line": 12}]
    return {
        "title": title,
        "rule_ids": rule_ids if rule_ids is not None else ["RS-001"],
        "category": category,
        "severity": severity,
        "confidence": confidence,
        "effort": effort,
        "locations": locs,
        "occurrences": len(locs),
        "evidence": evidence,
        "impact": impact,
        "recommendation": recommendation,
        "acceptance_criteria": ["Check passes"],
        "tags": [],
        "reviewers": reviewers if reviewers is not None else ["rev-1"],
    }


class DedupeTests(unittest.TestCase):
    def test_secondary_location_overlap_does_not_merge(self) -> None:
        a = make_finding(
            title="Move module-tree rules out of CrankyApp",
            rule_ids=["ARCH-002"],
            severity="medium",
            locations=[
                {"path": "src/app/mod.rs", "start_line": 10, "end_line": 20},
                {"path": "src/app/state.rs", "start_line": 50, "end_line": 55},
            ],
            reviewers=["architecture"],
        )
        b = make_finding(
            title="Load system font database once",
            rule_ids=["ARCH-002"],
            severity="high",
            locations=[
                {"path": "src/app/state.rs", "start_line": 52, "end_line": 60},
            ],
            reviewers=["module-1"],
        )
        out, merged = mf.dedupe([a, b])
        self.assertEqual(merged, 0)
        self.assertEqual(len(out), 2)
        self.assertEqual({f["severity"] for f in out}, {"medium", "high"})

    def test_primary_location_overlap_with_specific_rule_merges(self) -> None:
        a = make_finding(
            title="Cache font database",
            rule_ids=["PERF-001"],
            locations=[{"path": "src/fonts.rs", "start_line": 20, "end_line": 25}],
            reviewers=["rev-1"],
        )
        b = make_finding(
            title="Avoid reloading system fonts on clone",
            rule_ids=["PERF-001"],
            locations=[{"path": "src/fonts.rs", "start_line": 27, "end_line": 30}],
            reviewers=["rev-2"],
        )
        out, merged = mf.dedupe([a, b])
        self.assertEqual(merged, 1)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["reviewers"], ["rev-1", "rev-2"])

    def test_no_cascading_merges(self) -> None:
        a = make_finding(
            title="Shared title",
            rule_ids=["RS-001"],
            locations=[{"path": "src/a.rs", "start_line": 10, "end_line": 12}],
            reviewers=["rev-1"],
        )
        b = make_finding(
            title="Shared title",
            rule_ids=["RS-001", "RS-002"],
            locations=[{"path": "src/b.rs", "start_line": 100, "end_line": 105}],
            reviewers=["rev-2"],
        )
        # C overlaps B's primary location and shares RS-002, but does NOT match A's original loc/rule.
        c = make_finding(
            title="Unrelated finding on b.rs",
            rule_ids=["RS-002"],
            locations=[{"path": "src/b.rs", "start_line": 102, "end_line": 106}],
            reviewers=["rev-3"],
        )
        out, merged = mf.dedupe([a, b, c])
        self.assertEqual(merged, 1)
        self.assertEqual(len(out), 2)

    def test_common_rules_excluded_from_location_overlap_but_not_exact_title(self) -> None:
        # 6 findings cite GEN-008 (> threshold 5), two share primary location.
        findings = [
            make_finding(
                title=f"Distinct issue {i}",
                rule_ids=["GEN-008"],
                locations=[{"path": f"src/f{i}.rs", "start_line": 10, "end_line": 12}],
                reviewers=[f"rev-{i}"],
            )
            for i in range(5)
        ]
        f_hot1 = make_finding(
            title="Hot file issue A",
            rule_ids=["GEN-008"],
            locations=[{"path": "src/hot.rs", "start_line": 10, "end_line": 12}],
            reviewers=["rev-a"],
        )
        f_hot2 = make_finding(
            title="Hot file issue B",
            rule_ids=["GEN-008"],
            locations=[{"path": "src/hot.rs", "start_line": 11, "end_line": 13}],
            reviewers=["rev-b"],
        )
        f_gen000_1 = make_finding(
            title="Same exact title",
            rule_ids=["GEN-000"],
            locations=[{"path": "src/x.rs", "start_line": 1, "end_line": 2}],
            reviewers=["rev-c"],
        )
        f_gen000_2 = make_finding(
            title="Same exact title!",
            rule_ids=["GEN-000"],
            locations=[{"path": "src/y.rs", "start_line": 50, "end_line": 55}],
            reviewers=["rev-d"],
        )
        out, merged = mf.dedupe(findings + [f_hot1, f_hot2, f_gen000_1, f_gen000_2])
        # Only the exact-title GEN-000 pair should merge; hot1 and hot2 must stay separate.
        self.assertEqual(merged, 1)
        self.assertEqual(len(out), 8)

    def test_file_level_primary_locations_match_only_file_level(self) -> None:
        file_only_1 = make_finding(
            title="Split god module",
            rule_ids=["ARCH-003"],
            locations=[{"path": "src/state.rs"}],
            reviewers=["rev-1"],
        )
        file_only_2 = make_finding(
            title="Decompose state module",
            rule_ids=["ARCH-003"],
            locations=[{"path": "src/state.rs"}],
            reviewers=["rev-2"],
        )
        line_specific = make_finding(
            title="Extract helper from parse_config",
            rule_ids=["ARCH-003"],
            locations=[{"path": "src/state.rs", "start_line": 40, "end_line": 60}],
            reviewers=["rev-3"],
        )
        out, merged = mf.dedupe([file_only_1, line_specific, file_only_2])
        self.assertEqual(merged, 1)
        self.assertEqual(len(out), 2)

    def test_winner_keeps_prose_and_category_coherent(self) -> None:
        low_long = make_finding(
            title="Low title",
            rule_ids=["RS-005"],
            category="code-smell",
            severity="low",
            confidence="high",
            locations=[{"path": "src/lib.rs", "start_line": 10, "end_line": 15}],
            evidence="very long evidence " * 10,
            impact="very long impact " * 10,
            recommendation="very long rec " * 10,
            reviewers=["rev-1"],
        )
        high_short = make_finding(
            title="High title",
            rule_ids=["RS-005"],
            category="security",
            severity="high",
            confidence="medium",
            locations=[{"path": "src/lib.rs", "start_line": 11, "end_line": 14}],
            evidence="short ev",
            impact="short imp",
            recommendation="short rec",
            reviewers=["rev-2"],
        )
        out, merged = mf.dedupe([low_long, high_short])
        self.assertEqual(merged, 1)
        self.assertEqual(out[0]["title"], "High title")
        self.assertEqual(out[0]["category"], "security")
        self.assertEqual(out[0]["evidence"], "short ev")
        self.assertEqual(out[0]["impact"], "short imp")
        self.assertEqual(out[0]["recommendation"], "short rec")
        self.assertEqual(out[0]["severity"], "high")
        self.assertEqual(out[0]["confidence"], "high")
        self.assertEqual(out[0]["locations"][0]["start_line"], 11)

    def test_winner_tie_breaks_on_confidence_then_prose_length(self) -> None:
        a = make_finding(
            title="First short",
            rule_ids=["RS-005"],
            severity="medium",
            confidence="medium",
            evidence="a",
            impact="b",
            recommendation="c",
            reviewers=["rev-1"],
        )
        b = make_finding(
            title="Second richer",
            rule_ids=["RS-005"],
            severity="medium",
            confidence="medium",
            evidence="longer evidence",
            impact="longer impact",
            recommendation="longer rec",
            reviewers=["rev-2"],
        )
        out, merged = mf.dedupe([a, b])
        self.assertEqual(merged, 1)
        self.assertEqual(out[0]["title"], "Second richer")


class EndToEndTests(unittest.TestCase):
    def _write_reviewer_file(self, fdir: Path, name: str, findings: list[dict]) -> None:
        (fdir / f"{name}.json").write_text(json.dumps({"reviewer": name, "findings": findings}))

    def test_manual_groups_and_merges_md_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            audit = Path(tmp)
            fdir = audit / "findings"
            fdir.mkdir()
            self._write_reviewer_file(
                fdir,
                "tooling",
                [
                    {
                        "title": "Add CI workflow that runs cargo test",
                        "rule_ids": ["GEN-010"],
                        "category": "tooling",
                        "severity": "high",
                        "confidence": "high",
                        "effort": "S",
                        "locations": [{"path": ".github/workflows"}],
                        "impact": "No automated tests on PRs.",
                        "recommendation": "Add GitHub Actions CI.",
                        "acceptance_criteria": ["CI runs tests"],
                    }
                ],
            )
            self._write_reviewer_file(
                fdir,
                "testing",
                [
                    {
                        "title": "Configure automated test execution in CI",
                        "rule_ids": ["TEST-001"],
                        "category": "testing",
                        "severity": "medium",
                        "confidence": "high",
                        "effort": "S",
                        "locations": [{"path": "Cargo.toml"}],
                        "impact": "Regressions go unnoticed.",
                        "recommendation": "Run tests in CI.",
                        "acceptance_criteria": ["PRs fail on test failure"],
                    }
                ],
            )
            (audit / "merge-groups.json").write_text(
                json.dumps([["Add CI workflow", {"reviewer": "testing", "title": "Configure automated test"}]])
            )
            rc = mf.main([str(audit)])
            self.assertEqual(rc, 0)

            issues = json.loads((audit / "issues.json").read_text())
            self.assertEqual(len(issues), 1)
            self.assertEqual(issues[0]["title"], "Add CI workflow that runs cargo test")
            self.assertEqual(issues[0]["reviewers"], ["testing", "tooling"])

            merges_md = (audit / "merges.md").read_text()
            self.assertIn("AUD-001 · Add CI workflow that runs cargo test", merges_md)
            self.assertIn("Configure automated test execution in CI", merges_md)
            self.assertIn("reason: manual group", merges_md)

    def test_merges_md_written_when_zero_merges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            audit = Path(tmp)
            fdir = audit / "findings"
            fdir.mkdir()
            self._write_reviewer_file(
                fdir,
                "rev-1",
                [
                    {
                        "title": "Validate input",
                        "rule_ids": ["SEC-001"],
                        "category": "security",
                        "severity": "high",
                        "confidence": "high",
                        "effort": "S",
                        "locations": [{"path": "src/api.rs", "start_line": 10}],
                        "impact": "Bad input accepted.",
                        "recommendation": "Validate at boundary.",
                        "acceptance_criteria": ["Invalid input returns 400"],
                    }
                ],
            )
            rc = mf.main([str(audit)])
            self.assertEqual(rc, 0)
            merges_md = (audit / "merges.md").read_text()
            self.assertIn("_No findings merged._", merges_md)

    def test_missing_explicit_groups_file_returns_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            audit = Path(tmp)
            (audit / "findings").mkdir()
            rc = mf.main([str(audit), "--groups", str(audit / "nope.json")])
            self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
