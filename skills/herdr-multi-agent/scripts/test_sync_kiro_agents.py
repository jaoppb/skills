#!/usr/bin/env python3
"""Tests for sync_kiro_agents.py."""

from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync_kiro_agents as ska  # noqa: E402


def write_fake_kiro_cli(directory: Path, body: str) -> Path:
    script = directory / "kiro-cli"
    script.write_text(f"#!/usr/bin/env bash\nset -euo pipefail\n{body}\n", encoding="utf-8")
    script.chmod(0o755)
    return script


class ModelResolutionTests(unittest.TestCase):
    def test_version_precedence_picks_highest_semantic_version_and_canonical_over_dated_or_preview(self) -> None:
        catalog = [
            "auto",
            "claude-opus-4.5",
            "claude-opus-4-6-20260201",
            "claude-opus-4.6-preview",
            "claude-opus-4-6",
            "claude-opus-4.6",
            "claude-sonnet-4-5-20250929",
            "claude-sonnet-4.6.0",
            "claude-sonnet-4.6-20260301",
            "claude-sonnet-4.6",
            "claude-haiku-4.5",
        ]
        self.assertEqual(ska.select_family_model(catalog, "opus"), "claude-opus-4.6")
        self.assertEqual(ska.select_family_model(catalog, "sonnet"), "claude-sonnet-4.6")

    def test_patch_release_beats_lower_minor_and_newer_date_wins_among_dated_only(self) -> None:
        self.assertEqual(
            ska.select_family_model(["claude-opus-4.6", "claude-opus-4.6.1"], "opus"),
            "claude-opus-4.6.1",
        )
        self.assertEqual(
            ska.select_family_model(
                ["claude-sonnet-4-5-20250901", "claude-sonnet-4-5-20251115"],
                "sonnet",
            ),
            "claude-sonnet-4-5-20251115",
        )

    def test_extract_model_ids_supports_list_and_wrapped_object_schemas(self) -> None:
        self.assertEqual(
            ska.extract_model_ids(["auto", "claude-opus-4.6"]),
            ["auto", "claude-opus-4.6"],
        )
        self.assertEqual(
            ska.extract_model_ids(
                {
                    "models": [
                        {"id": "claude-opus-4.6", "provider": "anthropic"},
                        {"modelId": "claude-sonnet-4.6"},
                        {"name": "bad\ninjection"},
                    ]
                }
            ),
            ["claude-opus-4.6", "claude-sonnet-4.6"],
        )

    def test_rejects_yaml_injection_in_model_overrides(self) -> None:
        with self.assertRaises(ska.SyncError):
            ska.resolve_models(
                opus_override="claude-opus-4.6\ntools: ['*']",
                sonnet_override="claude-sonnet-4.6",
                kiro_bin="definitely-missing-kiro-cli-binary",
            )

    def test_offline_dual_overrides_succeed_when_kiro_cli_missing(self) -> None:
        opus, sonnet = ska.resolve_models(
            opus_override="claude-opus-4.6",
            sonnet_override="claude-sonnet-4.6",
            kiro_bin="definitely-missing-kiro-cli-binary",
        )
        self.assertEqual((opus, sonnet), ("claude-opus-4.6", "claude-sonnet-4.6"))

    def test_live_kiro_cli_validates_overrides_and_fails_loud_without_auto_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp)
            fake = write_fake_kiro_cli(
                bin_dir,
                'printf \'%s\\n\' \'{"models":[{"id":"auto"},{"id":"claude-sonnet-4.6"}]}\'',
            )
            # Free-tier simulation: Sonnet exists, Opus missing -> fails loud by default
            with self.assertRaises(ska.SyncError):
                ska.resolve_models(kiro_bin=str(fake))

            # Explicit --allow-auto-fallback warns on stderr and substitutes 'auto' for Opus only
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                opus, sonnet = ska.resolve_models(
                    allow_auto_fallback=True,
                    kiro_bin=str(fake),
                )
            self.assertEqual(opus, "auto")
            self.assertEqual(sonnet, "claude-sonnet-4.6")
            self.assertIn("warn", stderr.getvalue())

            # Invalid explicit override fails loud against live catalog without fallback
            with self.assertRaises(ska.SyncError):
                ska.resolve_models(
                    opus_override="claude-opus-9.9",
                    sonnet_override="claude-sonnet-4.6",
                    kiro_bin=str(fake),
                )


class SyncAndProvenanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmp.name)
        self.out_dir = self.tmp_path / "agents"
        self.models_json = self.tmp_path / "models.json"
        self.models_json.write_text(
            json.dumps(
                {
                    "models": [
                        {"id": "auto"},
                        {"id": "claude-opus-4.5"},
                        {"id": "claude-opus-4.6"},
                        {"id": "claude-sonnet-4.5"},
                        {"id": "claude-sonnet-4.6"},
                    ]
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_cli(self, *extra_args: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = ska.main(
                [
                    "--out-dir",
                    str(self.out_dir),
                    "--models-json",
                    str(self.models_json),
                    *extra_args,
                ]
            )
        return code, stdout.getvalue(), stderr.getvalue()

    def test_sync_installs_13_profiles_with_strict_readonly_reviewers_and_no_sidecar_json(self) -> None:
        # Before first sync, --check exits 1 (missing)
        code, out, _ = self.run_cli("--check")
        self.assertEqual(code, 1)
        self.assertIn("missing", out)

        # Dry-run writes nothing
        code, out, _ = self.run_cli("--dry-run")
        self.assertEqual(code, 0)
        self.assertIn("would write", out)
        self.assertFalse(self.out_dir.exists())

        # Real sync writes exactly 13 .md files and zero .json files
        code, _, err = self.run_cli()
        self.assertEqual(code, 0, msg=err)
        written = sorted(p.name for p in self.out_dir.iterdir())
        self.assertEqual(len(written), 13)
        self.assertTrue(all(name.endswith(".md") for name in written))
        self.assertIn("herdr-coordinator.md", written)
        self.assertIn("herdr-worker.md", written)

        # --check now exits 0
        code, _, err = self.run_cli("--check")
        self.assertEqual(code, 0, msg=err)

        # Verify coordinator & worker models and subagent capability
        coord = (self.out_dir / "herdr-coordinator.md").read_text(encoding="utf-8")
        worker = (self.out_dir / "herdr-worker.md").read_text(encoding="utf-8")
        self.assertTrue(coord.startswith("---\nname: herdr-coordinator\n"))
        self.assertIn("\nmodel: claude-sonnet-4.6\n", coord)
        self.assertIn("  - subagent\n", coord)
        self.assertTrue(worker.startswith("---\nname: herdr-worker\n"))
        self.assertIn("\nmodel: claude-opus-4.6\n", worker)
        self.assertIn("  - subagent\n", worker)

        # Verify every review-<lens>.md is structurally read-only, tier-mapped, and embeds its lens guide
        forbidden_tools = ("fs_write", "fs_append", "str_replace", "delete_file", "  - write", "  - shell", "  - subagent")
        for lens_name, tier in ska.LENS_TIERS.items():
            path = self.out_dir / f"review-{lens_name}.md"
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith(f"---\nname: review-{lens_name}\n"))
            _, frontmatter, body = text.split("---", 2)

            expected_model = "claude-opus-4.6" if tier == "flagship" else "claude-sonnet-4.6"
            self.assertIn(f"\nmodel: {expected_model}\n", frontmatter)
            self.assertIn("\ntools:\n  - read\n", frontmatter)
            for forbidden in ("  - write", "  - shell", "  - subagent", "str_replace", "delete_file", "fs_append"):
                self.assertNotIn(forbidden, frontmatter)
            self.assertIn("capability: fs_read", frontmatter)
            self.assertIn('"/tmp/**"', frontmatter)
            self.assertIn("capability: fs_write\n      match:\n        - \"**\"\n      effect: deny", frontmatter)
            self.assertIn("not an external specialist override", frontmatter)

            # Embedded lens rubric from skills/code-review/references/lenses/<lens>.md must be present
            lens_src = (ska.DEFAULT_CODE_REVIEW_DIR / "references" / "lenses" / f"{lens_name}.md").read_text(encoding="utf-8").strip()
            self.assertIn(lens_src, body)
            self.assertTrue(any(tok in body for tok in forbidden_tools) or "Edit nothing" in body)

    def test_idempotent_rerun_and_drift_detection_for_model_or_lens_changes(self) -> None:
        self.assertEqual(self.run_cli()[0], 0)
        target = self.out_dir / "review-code-quality.md"
        mtime_before = target.stat().st_mtime_ns

        # Second run is a no-op and preserves mtime
        code, out, _ = self.run_cli()
        self.assertEqual(code, 0)
        self.assertIn("ok     ", out)
        self.assertEqual(target.stat().st_mtime_ns, mtime_before)

        # Model upgrade makes untouched managed files cleanly stale (exit 1 on --check, 0 on re-sync)
        self.models_json.write_text(
            json.dumps(["claude-opus-4.7", "claude-sonnet-4.6"]),
            encoding="utf-8",
        )
        code, out, _ = self.run_cli("--check")
        self.assertEqual(code, 1)
        self.assertIn("stale", out)

        code, _, _ = self.run_cli()
        self.assertEqual(code, 0)
        self.assertIn("\nmodel: claude-opus-4.7\n", target.read_text(encoding="utf-8"))
        self.assertEqual(self.run_cli("--check")[0], 0)

    def test_preserves_non_namespaced_user_agents_and_guards_hand_edits(self) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        user_agent = self.out_dir / "my-custom-architect.md"
        user_agent.write_text("---\nname: my-custom-architect\n---\nCustom prompt.\n", encoding="utf-8")

        self.assertEqual(self.run_cli()[0], 0)
        self.assertEqual(
            user_agent.read_text(encoding="utf-8"),
            "---\nname: my-custom-architect\n---\nCustom prompt.\n",
        )

        # Hand-edit a managed file -> both --check and sync refuse with exit 2 unless --force
        managed = self.out_dir / "review-security.md"
        managed.write_text(managed.read_text(encoding="utf-8") + "\nHand edit!\n", encoding="utf-8")

        code_check, _, err_check = self.run_cli("--check")
        self.assertEqual(code_check, 2)
        self.assertIn("hand-edited", err_check)

        code_sync, _, err_sync = self.run_cli()
        self.assertEqual(code_sync, 2)
        self.assertIn("--force", err_sync)
        self.assertIn("Hand edit!", managed.read_text(encoding="utf-8"))

        # --force restores clean managed profile
        self.assertEqual(self.run_cli("--force")[0], 0)
        self.assertNotIn("Hand edit!", managed.read_text(encoding="utf-8"))
        self.assertEqual(self.run_cli("--check")[0], 0)

    def test_unmanaged_namespaced_file_and_symlink_target_are_refused(self) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        unmanaged = self.out_dir / "herdr-worker.md"
        unmanaged.write_text("---\nname: herdr-worker\n---\nUser-authored.\n", encoding="utf-8")

        code, _, err = self.run_cli()
        self.assertEqual(code, 2)
        self.assertIn("unmanaged file", err)

        # Replace with a symlink -> refused even with --force (prevents symlink clobber)
        victim = self.tmp_path / "victim.txt"
        victim.write_text("do not touch", encoding="utf-8")
        unmanaged.unlink()
        os.symlink(victim, unmanaged)

        code_force, _, err_force = self.run_cli("--force")
        self.assertEqual(code_force, 2)
        self.assertIn("symlink target refused", err_force)
        self.assertEqual(victim.read_text(encoding="utf-8"), "do not touch")

    def test_missing_code_review_dir_fails_loud_and_print_models_outputs_json(self) -> None:
        code, out, _ = self.run_cli("--print-models")
        self.assertEqual(code, 0)
        self.assertEqual(
            json.loads(out),
            {"opus": "claude-opus-4.6", "sonnet": "claude-sonnet-4.6"},
        )

        bad_cr = self.tmp_path / "missing-code-review"
        code_bad, _, err_bad = self.run_cli("--code-review-dir", str(bad_cr))
        self.assertEqual(code_bad, 1)
        self.assertIn("code-review", err_bad)

    def test_lens_content_drift_and_unmapped_lens_detection(self) -> None:
        cr_copy = self.tmp_path / "code-review"
        lenses_copy = cr_copy / "references" / "lenses"
        lenses_copy.mkdir(parents=True)
        src_lenses = ska.DEFAULT_CODE_REVIEW_DIR / "references" / "lenses"
        for src in src_lenses.glob("*.md"):
            (lenses_copy / src.name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

        self.assertEqual(self.run_cli("--code-review-dir", str(cr_copy))[0], 0)
        self.assertEqual(self.run_cli("--code-review-dir", str(cr_copy), "--check")[0], 0)

        # Updating a single lens guide makes --check report stale (exit 1) until re-synced
        (lenses_copy / "testing.md").write_text("# Updated Testing Rubric\nNew rule.\n", encoding="utf-8")
        code, out, _ = self.run_cli("--code-review-dir", str(cr_copy), "--check")
        self.assertEqual(code, 1)
        self.assertIn("stale   " + str(self.out_dir / "review-testing.md"), out)

        self.assertEqual(self.run_cli("--code-review-dir", str(cr_copy))[0], 0)
        self.assertIn(
            "# Updated Testing Rubric",
            (self.out_dir / "review-testing.md").read_text(encoding="utf-8"),
        )

        # Adding an unmapped lens file fails loud so LENS_TIERS cannot silently drift
        (lenses_copy / "accessibility.md").write_text("# Extra\n", encoding="utf-8")
        code_extra, _, err_extra = self.run_cli("--code-review-dir", str(cr_copy), "--check")
        self.assertEqual(code_extra, 1)
        self.assertIn("accessibility", err_extra)

    def test_out_dir_symlink_and_obsolete_managed_profile_warning(self) -> None:
        real_dir = self.tmp_path / "real-agents"
        real_dir.mkdir()
        link_dir = self.tmp_path / "symlink-agents"
        os.symlink(real_dir, link_dir)

        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = ska.main(["--out-dir", str(link_dir), "--models-json", str(self.models_json)])
        self.assertEqual(code, 2)
        self.assertIn("symlink", stderr.getvalue())

        # Obsolete managed review-*.md file triggers a non-destructive stale notice
        self.assertEqual(self.run_cli()[0], 0)
        obsolete = self.out_dir / "review-legacy.md"
        obsolete.write_text(
            ska.render_with_provenance("---\nname: review-legacy\n---\nOld.\n", {}),
            encoding="utf-8",
        )
        code_obs, out_obs, _ = self.run_cli("--check")
        self.assertEqual(code_obs, 0)
        self.assertIn("review-legacy.md was generated by an older herdr-multi-agent version", out_obs)
        self.assertTrue(obsolete.exists())

    def test_kiro_cli_nonzero_exit_fails_loud_or_warns_with_fallback(self) -> None:
        fake = write_fake_kiro_cli(self.tmp_path, 'echo "not logged in" >&2; exit 1')
        with self.assertRaises(ska.SyncError):
            ska.resolve_models(kiro_bin=str(fake))

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            opus, sonnet = ska.resolve_models(allow_auto_fallback=True, kiro_bin=str(fake))
        self.assertEqual((opus, sonnet), ("auto", "auto"))
        self.assertIn("not logged in", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
