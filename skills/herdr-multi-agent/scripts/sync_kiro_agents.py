#!/usr/bin/env python3
"""Sync specialized Kiro custom agents into ~/.kiro/agents/ for herdr-multi-agent.

Usage:
    python3 sync_kiro_agents.py [--check] [--dry-run] [--force]
                                [--out-dir ~/.kiro/agents]
                                [--code-review-dir <path>]
                                [--opus-model <slug>] [--sonnet-model <slug>]
                                [--models-json <path>] [--allow-auto-fallback]
                                [--print-models]

Renders and installs the namespaced Kiro custom agent profiles managed by
herdr-multi-agent (`herdr-coordinator.md`, `herdr-worker.md`, and read-only
`review-<lens>.md` wrappers embedding `code-review/references/lenses/<lens>.md`)
into `~/.kiro/agents/` without touching task git worktrees or non-namespaced
user agents.

Each managed `.md` file embeds an HTML provenance comment immediately after its
YAML frontmatter (`<!-- herdr-multi-agent-managed: sha256=<digest> -->`; no
sidecar `.json` files are written into `~/.kiro/agents/`).

Exit codes:
    0  All managed profiles synced (or verified up-to-date under --check).
    1  Missing or stale profiles under --check, or model/lens/template/I/O error.
    2  Hand-edited/unmanaged conflict in --out-dir (rerun with --force), or
       unsafe symlink/non-directory/non-regular target refused.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_DIR / "references" / "kiro-agents"
DEFAULT_CODE_REVIEW_DIR = SKILL_DIR.parent / "code-review"
DEFAULT_OUT_DIR = Path.home() / ".kiro" / "agents"

MODEL_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
LENS_NAME_RE = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
LENS_TIER_RE = re.compile(r"^-\s*\*\*Tier\*\*:\s*`(flagship|fast/balanced)`\s*$", re.M)
PROVENANCE_RE = re.compile(
    r"\A(---\n.*?\n---\n)<!-- herdr-multi-agent-managed: sha256=([0-9a-f]{64}) -->\n",
    re.S,
)
FRONTMATTER_SPLIT_RE = re.compile(r"\A(---\n.*?\n---\n)", re.S)
DATE_TOKEN_RE = re.compile(r"^(?:19|20)\d{6}$")
PROVIDER_REV_RE = re.compile(r"(?:-v\d+)?(?::\d+)?$", re.I)
PLACEHOLDER_RE = re.compile(r"\{\{([A-Z_]+)\}\}")


class SyncError(Exception):
    """Raised when model resolution, lens lookup, or template rendering fails."""


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_model_id(slug: str, source: str) -> str:
    if not isinstance(slug, str) or not MODEL_ID_RE.match(slug):
        raise SyncError(f"invalid model identifier from {source}: {slug!r}")
    return slug


def extract_model_ids(payload: object) -> list[str]:
    """Extract validated model slug strings from kiro-cli --list-models JSON."""
    items: object = payload
    if isinstance(payload, dict):
        for key in ("models", "availableModels", "items", "data"):
            if isinstance(payload.get(key), list):
                items = payload[key]
                break
        else:
            raise SyncError("unrecognized --list-models JSON object (expected a 'models' list)")
    if not isinstance(items, list):
        raise SyncError("unrecognized --list-models JSON format (expected list or object)")

    seen: set[str] = set()
    models: list[str] = []
    for entry in items:
        candidate: str | None = None
        if isinstance(entry, str):
            candidate = entry
        elif isinstance(entry, dict):
            for key in ("id", "modelId", "model_id", "slug", "name"):
                val = entry.get(key)
                if isinstance(val, str) and val:
                    candidate = val
                    break
        if candidate and MODEL_ID_RE.match(candidate) and candidate not in seen:
            seen.add(candidate)
            models.append(candidate)
    return models


def rank_family_slug(
    slug: str, family: str
) -> tuple[tuple[int, ...], int, int, int, bool, int, str]:
    """Return a comparison key ranking higher versions first and canonical slugs over dated/preview ones."""
    prefix = f"claude-{family}-"
    raw_rest = slug[len(prefix):]
    rest = PROVIDER_REV_RE.sub("", raw_rest)
    has_provider_rev = rest != raw_rest

    tokens = [tok for tok in re.split(r"[-._]", rest) if tok]
    raw_ver: list[int] = []
    idx = 0
    while idx < len(tokens) and tokens[idx].isdigit() and not DATE_TOKEN_RE.match(tokens[idx]):
        raw_ver.append(int(tokens[idx]))
        idx += 1

    while len(raw_ver) > 1 and raw_ver[-1] == 0:
        raw_ver.pop()
    version = tuple(raw_ver) if raw_ver else (0,)

    remaining = tokens[idx:]
    dates = [int(tok) for tok in remaining if DATE_TOKEN_RE.match(tok)]
    others = [tok for tok in remaining if not DATE_TOKEN_RE.match(tok)]

    if others:
        stability_rank = 0
    elif dates:
        stability_rank = 1
    else:
        stability_rank = 2

    date_num = max(dates) if dates else 0
    return (
        version,
        stability_rank,
        0 if has_provider_rev else 1,
        date_num,
        "." in rest,
        -len(rest),
        slug,
    )


def select_family_model(catalog: list[str], family: str) -> str | None:
    prefix = f"claude-{family}-"
    candidates = [m for m in catalog if m.lower().startswith(prefix)]
    if not candidates:
        return None
    return max(candidates, key=lambda s: rank_family_slug(s, family))


def query_kiro_models(kiro_bin: str = "kiro-cli") -> list[str]:
    try:
        proc = subprocess.run(
            [kiro_bin, "chat", "--list-models", "--format", "json"],
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
    except FileNotFoundError as err:
        raise SyncError(
            f"'{kiro_bin}' not found on PATH; install kiro-cli or pass both "
            "--opus-model and --sonnet-model (or --models-json)"
        ) from err
    except subprocess.TimeoutExpired as err:
        raise SyncError(f"'{kiro_bin} chat --list-models --format json' timed out after 15s") from err

    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip().splitlines()
        msg = detail[0] if detail else f"exit code {proc.returncode}"
        raise SyncError(f"'{kiro_bin} chat --list-models --format json' failed: {msg}")

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as err:
        raise SyncError(f"invalid JSON from '{kiro_bin} chat --list-models --format json': {err}") from err

    models = extract_model_ids(payload)
    if not models:
        raise SyncError(f"'{kiro_bin} chat --list-models --format json' returned zero usable model IDs")
    return models


def resolve_models(
    *,
    opus_override: str | None = None,
    sonnet_override: str | None = None,
    models_json: Path | None = None,
    allow_auto_fallback: bool = False,
    kiro_bin: str = "kiro-cli",
) -> tuple[str, str]:
    """Resolve (opus_model, sonnet_model) according to precedence, overrides, and fallback policy."""
    if opus_override is not None:
        validate_model_id(opus_override, "--opus-model")
    if sonnet_override is not None:
        validate_model_id(sonnet_override, "--sonnet-model")

    catalog: list[str] | None = None
    if models_json is not None:
        try:
            payload = json.loads(models_json.read_text(encoding="utf-8"))
        except OSError as err:
            raise SyncError(f"cannot read --models-json '{models_json}': {err}") from err
        except json.JSONDecodeError as err:
            raise SyncError(f"invalid JSON in --models-json '{models_json}': {err}") from err
        catalog = extract_model_ids(payload)
        if not catalog:
            raise SyncError(f"--models-json '{models_json}' contains zero usable model IDs")
    elif opus_override and sonnet_override and shutil.which(kiro_bin) is None:
        return opus_override, sonnet_override
    else:
        try:
            catalog = query_kiro_models(kiro_bin=kiro_bin)
        except SyncError as err:
            if not allow_auto_fallback:
                raise
            print(f"warn   {err}; falling back to 'auto' (--allow-auto-fallback)", file=sys.stderr)
            return opus_override or "auto", sonnet_override or "auto"

    resolved: dict[str, str] = {}
    for family, override in (("opus", opus_override), ("sonnet", sonnet_override)):
        if override is not None:
            picked = override if override in catalog else None
            missing_msg = f"--{family}-model '{override}' is not in kiro-cli model catalog"
            fatal_msg = f"{missing_msg} ({', '.join(catalog)})"
        else:
            picked = select_family_model(catalog, family)
            missing_msg = f"no 'claude-{family}-*' model available in kiro-cli catalog"
            fatal_msg = f"{missing_msg} (pass --{family}-model or --allow-auto-fallback)"

        if picked is not None:
            resolved[family] = picked
        elif allow_auto_fallback:
            print(f"warn   {missing_msg}; falling back to 'auto' (--allow-auto-fallback)", file=sys.stderr)
            resolved[family] = "auto"
        else:
            raise SyncError(fatal_msg)

    return resolved["opus"], resolved["sonnet"]


def load_code_review_lenses(code_review_dir: Path) -> dict[str, tuple[str, str]]:
    """Load (tier, body) for every lens guide in <code-review-dir>/references/lenses/*.md."""
    lenses_dir = code_review_dir / "references" / "lenses"
    if not lenses_dir.is_dir():
        raise SyncError(
            f"companion code-review lenses directory not found at '{lenses_dir}' "
            "(install 'code-review' alongside 'herdr-multi-agent' or pass --code-review-dir)"
        )

    try:
        lens_files = sorted(p for p in lenses_dir.glob("*.md") if p.is_file())
    except OSError as err:
        raise SyncError(f"cannot list lenses directory '{lenses_dir}': {err}") from err

    if not lens_files:
        raise SyncError(f"no lens guide (.md) files found in '{lenses_dir}'")

    lenses: dict[str, tuple[str, str]] = {}
    for lens_path in lens_files:
        lens_name = lens_path.stem
        if not LENS_NAME_RE.match(lens_name):
            raise SyncError(f"invalid lens filename '{lens_path.name}' in '{lenses_dir}'")
        try:
            body = lens_path.read_text(encoding="utf-8").strip()
        except OSError as err:
            raise SyncError(f"cannot read lens guide '{lens_path}': {err}") from err
        tier_match = LENS_TIER_RE.search(body)
        if not tier_match:
            raise SyncError(
                f"lens guide '{lens_path}' is missing '- **Tier**: `flagship`' or '- **Tier**: `fast/balanced`'"
            )
        lenses[lens_name] = (tier_match.group(1), body)

    return lenses


def render_with_provenance(template: str, values: dict[str, str]) -> str:
    stripped_template = PLACEHOLDER_RE.sub("", template)
    if "{{" in stripped_template or "}}" in stripped_template:
        raise SyncError("malformed '{{' or '}}' placeholder in agent template")

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            raise SyncError(f"missing template value '{key}'")
        return values[key]

    unmarked = PLACEHOLDER_RE.sub(replace, template).strip() + "\n"
    fm_match = FRONTMATTER_SPLIT_RE.match(unmarked)
    if not fm_match:
        raise SyncError("rendered agent profile is missing leading YAML frontmatter")
    digest = sha256(unmarked)
    header = fm_match.group(1)
    rest = unmarked[fm_match.end():]
    return f"{header}<!-- herdr-multi-agent-managed: sha256={digest} -->\n{rest}"


def build_expected_profiles(
    *,
    opus_model: str,
    sonnet_model: str,
    code_review_dir: Path = DEFAULT_CODE_REVIEW_DIR,
    templates_dir: Path = TEMPLATES_DIR,
) -> dict[str, str]:
    """Render all managed Kiro custom agent files in memory."""
    validate_model_id(opus_model, "opus_model")
    validate_model_id(sonnet_model, "sonnet_model")

    coord_tpl_path = templates_dir / "herdr-coordinator.md"
    worker_tpl_path = templates_dir / "herdr-worker.md"
    lens_tpl_path = templates_dir / "review-lens.md"
    for path in (coord_tpl_path, worker_tpl_path, lens_tpl_path):
        if not path.is_file():
            raise SyncError(f"missing Kiro agent template: {path}")

    try:
        coord_tpl = coord_tpl_path.read_text(encoding="utf-8")
        worker_tpl = worker_tpl_path.read_text(encoding="utf-8")
        lens_template = lens_tpl_path.read_text(encoding="utf-8")
    except OSError as err:
        raise SyncError(f"cannot read Kiro agent template: {err}") from err

    lenses = load_code_review_lenses(code_review_dir)

    common = {"OPUS_MODEL": opus_model, "SONNET_MODEL": sonnet_model}
    profiles: dict[str, str] = {
        "herdr-coordinator.md": render_with_provenance(coord_tpl, common),
        "herdr-worker.md": render_with_provenance(worker_tpl, common),
    }

    for lens_name, (tier, lens_body) in sorted(lenses.items()):
        agent_name = f"review-{lens_name}"
        model = opus_model if tier == "flagship" else sonnet_model
        rendered = render_with_provenance(
            lens_template,
            {
                "AGENT_NAME": agent_name,
                "LENS_NAME": lens_name,
                "TIER": tier,
                "MODEL": model,
                "LENS_BODY": lens_body,
            },
        )
        profiles[f"{agent_name}.md"] = rendered

    return profiles


def inspect_target(path: Path, expected_text: str) -> tuple[str, str]:
    """Inspect a managed target path.

    Returns (status, detail) where status is one of:
      - 'ok': matches expected_text
      - 'missing': file does not exist
      - 'stale': untouched managed file with older content
      - 'conflict': unmanaged or hand-edited regular file (overwritable with --force)
      - 'unsafe': symlink or directory at target path (never overwritten)
    """
    if path.is_symlink():
        return "unsafe", f"{path} (symlink target refused)"
    if not path.exists():
        return "missing", str(path)
    if not path.is_file():
        return "unsafe", f"{path} (not a regular file)"

    try:
        disk_text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "conflict", f"{path} (non-UTF-8 file not generated by sync_kiro_agents.py)"
    except OSError as err:
        raise SyncError(f"cannot read '{path}': {err}") from err

    prov = PROVENANCE_RE.match(disk_text)
    if not prov:
        return "conflict", f"{path} (unmanaged file not generated by sync_kiro_agents.py)"

    recorded_sha = prov.group(2)
    unmarked_disk = prov.group(1) + disk_text[prov.end():]
    if sha256(unmarked_disk) != recorded_sha:
        return "conflict", f"{path} (hand-edited since last sync)"
    if disk_text == expected_text:
        return "ok", str(path)
    return "stale", str(path)


def current_file_mode() -> int:
    umask = os.umask(0o077)
    os.umask(umask)
    return 0o666 & ~umask


def atomic_write(path: Path, content: str, mode: int) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    except OSError as err:
        raise SyncError(f"cannot create temporary file in '{path.parent}': {err}") from err
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.chmod(tmp_name, mode)
        os.replace(tmp_name, path)
    except BaseException as err:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        if isinstance(err, OSError):
            raise SyncError(f"cannot write '{path}': {err}") from err
        raise


def is_managed_namespace(filename: str) -> bool:
    return filename.endswith(".md") and (
        filename.startswith("herdr-") or filename.startswith("review-")
    )


def sync_profiles(
    expected: dict[str, str],
    *,
    out_dir: Path,
    check: bool = False,
    dry_run: bool = False,
    force: bool = False,
) -> int:
    if out_dir.is_symlink() or (out_dir.exists() and not out_dir.is_dir()):
        print(
            f"error: output directory '{out_dir}' is a symlink or not a directory",
            file=sys.stderr,
        )
        return 2

    statuses: dict[str, tuple[str, str]] = {}
    for filename in sorted(expected):
        if "/" in filename or "\\" in filename or filename in (".", ".."):
            raise SyncError(f"unsafe managed filename: {filename!r}")
        statuses[filename] = inspect_target(out_dir / filename, expected[filename])

    unsafe = [detail for status, detail in statuses.values() if status == "unsafe"]
    if unsafe:
        print("error: unsafe target path(s) in output directory:", file=sys.stderr)
        for item in unsafe:
            print(f"  {item}", file=sys.stderr)
        return 2

    conflicts = [detail for status, detail in statuses.values() if status == "conflict"]
    if conflicts and (check or not force):
        print(
            "hand edits or unmanaged files detected; rerun with --force after reviewing them:",
            file=sys.stderr,
        )
        for item in conflicts:
            print(f"  {item}", file=sys.stderr)
        return 2

    if out_dir.is_dir():
        try:
            existing_entries = sorted(out_dir.iterdir())
        except OSError as err:
            raise SyncError(f"cannot list output directory '{out_dir}': {err}") from err
        for existing in existing_entries:
            if (
                existing.name not in expected
                and is_managed_namespace(existing.name)
                and existing.is_file()
                and not existing.is_symlink()
            ):
                try:
                    text = existing.read_text(encoding="utf-8", errors="replace")
                except OSError as err:
                    raise SyncError(f"cannot read '{existing}': {err}") from err
                if PROVENANCE_RE.match(text):
                    print(
                        f"stale  {existing} was generated by an older herdr-multi-agent version; "
                        "delete it if obsolete"
                    )

    if check:
        drift = False
        for filename in sorted(expected):
            status, _ = statuses[filename]
            target = out_dir / filename
            print(f"{status:<7} {target}")
            if status != "ok":
                drift = True
        return 1 if drift else 0

    mode = current_file_mode()
    for filename in sorted(expected):
        status, _ = statuses[filename]
        target = out_dir / filename
        if status == "ok":
            print(f"ok     {target}")
            continue
        if dry_run:
            print(f"would write  {target} ({status})")
        else:
            atomic_write(target, expected[filename], mode)
            print(f"write  {target}")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="target Kiro agents directory (default: ~/.kiro/agents)",
    )
    parser.add_argument(
        "--code-review-dir",
        type=Path,
        default=DEFAULT_CODE_REVIEW_DIR,
        help="path to companion code-review skill directory",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify managed profiles are present, unedited, and current; write nothing",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="report planned writes without modifying disk",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite hand-edited or pre-existing unmanaged herdr-*.md / review-*.md files",
    )
    parser.add_argument(
        "--opus-model",
        help="explicit model slug override for flagship / Top tier (herdr-worker and deep review lenses)",
    )
    parser.add_argument(
        "--sonnet-model",
        help="explicit model slug override for Middle / Fast / advisory tier (herdr-coordinator and advisory lenses)",
    )
    parser.add_argument(
        "--models-json",
        type=Path,
        help="read kiro-cli chat --list-models --format json output from a file instead of invoking kiro-cli",
    )
    parser.add_argument(
        "--allow-auto-fallback",
        action="store_true",
        help="fall back to 'auto' with a stderr warning when kiro-cli or a required tier is unavailable",
    )
    parser.add_argument(
        "--print-models",
        action="store_true",
        help="print resolved {'opus': ..., 'sonnet': ...} JSON to stdout and exit",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        opus_model, sonnet_model = resolve_models(
            opus_override=args.opus_model,
            sonnet_override=args.sonnet_model,
            models_json=args.models_json,
            allow_auto_fallback=args.allow_auto_fallback,
        )
        if args.print_models:
            print(json.dumps({"opus": opus_model, "sonnet": sonnet_model}))
            return 0

        expected = build_expected_profiles(
            opus_model=opus_model,
            sonnet_model=sonnet_model,
            code_review_dir=args.code_review_dir,
        )
        return sync_profiles(
            expected,
            out_dir=args.out_dir,
            check=args.check,
            dry_run=args.dry_run,
            force=args.force,
        )
    except SyncError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
