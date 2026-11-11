#!/usr/bin/env python3
"""Render the spdd-* skill templates from a project profile.

Usage:
    python3 render.py --profile profile.json --out <skills-dir>
                      [--commands <commands-dir>] [--dry-run] [--force]

Profile (JSON):
    {
      "flags":  {"issue": true, "ephemeral": true, "sync": false, ...},
      "values": {"PROJECT": "Acme", "FINGERPRINT_FILES": ["- Read `package.json` ..."], ...}
    }

Every flag used by the templates must be declared as true or false. A value
may be a string or a list of lines. A value slot alone on its line is indented
to that line's indentation, line by line.

The run writes <skills-dir>/spdd.profile.json: the profile, a hash of the
templates and a hash of each generated file. That record is itself a valid
--profile, so a re-run starts from it. A later run refuses to overwrite
a generated file whose hash no longer matches that record (a hand edit) unless
--force is given.

Exit codes: 0 rendered, 1 profile or template error, 2 hand edits found.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "references" / "templates"
RECORD = "spdd.profile.json"
DIRECTIVE = re.compile(r"\A<!-- spdd-bootstrap: render-if (\^?)([a-z]+) -->\n")
STANDALONE_SECTION = re.compile(r"^[ \t]*(\{\{[#^/][a-z]+\}\})[ \t]*\n", re.M)
SECTION = re.compile(r"\{\{([#^])([a-z]+)\}\}((?:(?!\{\{[#^]\2\}\}).)*?)\{\{/\2\}\}", re.S)
STANDALONE_VALUE = re.compile(r"^([ \t]*)\{\{([A-Z_]+)\}\}[ \t]*$", re.M)
INLINE_VALUE = re.compile(r"\{\{([A-Z_]+)\}\}")
ANY_FLAG = re.compile(r"\{\{[#^/]([a-z]+)\}\}")
FOREIGN_WORDS = ("cosmo", "sefaz", "nfc-e", "turso")


class RenderError(Exception):
    pass


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def load_profile(path: Path) -> tuple[dict[str, bool], dict[str, str]]:
    data = json.loads(path.read_text())
    flags = data.get("flags", {})
    bad = [k for k, v in flags.items() if not isinstance(v, bool)]
    if bad:
        raise RenderError(f"flags must be true or false: {', '.join(bad)}")
    values = {}
    for key, value in data.get("values", {}).items():
        values[key] = "\n".join(value) if isinstance(value, list) else str(value)
    return flags, values


def resolve_sections(text: str, flags: dict[str, bool]) -> str:
    text = STANDALONE_SECTION.sub(r"\1", text)
    while True:
        new = SECTION.sub(lambda m: m.group(3) if flags[m.group(2)] == (m.group(1) == "#") else "", text)
        if new == text:
            return new
        text = new


def substitute(text: str, values: dict[str, str], used: set[str]) -> str:
    def standalone(m: re.Match) -> str:
        indent, name = m.group(1), m.group(2)
        used.add(name)
        return "\n".join(indent + line if line else line for line in lookup(name).split("\n"))

    def inline(m: re.Match) -> str:
        name = m.group(1)
        used.add(name)
        value = lookup(name)
        if "\n" in value:
            raise RenderError(f"multi-line value {name} is used inside a sentence")
        return value

    def lookup(name: str) -> str:
        if name not in values:
            raise RenderError(f"value {name} is used but not in the profile")
        return values[name]

    return INLINE_VALUE.sub(inline, STANDALONE_VALUE.sub(standalone, text))


def render(template: str, flags: dict[str, bool], values: dict[str, str], used: set[str]) -> str:
    text = substitute(resolve_sections(template, flags), values, used)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    if "{{" in text:
        raise RenderError("unresolved {{ left after rendering")
    return text


def polish_notes(text: str) -> list[str]:
    """Spots that rendering left for a human pass: empty sub-steps, gaps in step letters."""
    notes = []
    lines = text.split("\n")
    for i, line in enumerate(lines):
        step = re.match(r"^(\s*)([a-z])\. .*:$", line)
        if step and i + 2 < len(lines) and lines[i + 1] == "" and re.match(rf"^{step.group(1)}([a-z]\. |\d+\. |\S)", lines[i + 2]):
            notes.append(f"line {i + 1}: sub-step {step.group(2)}. is empty; drop it")
    expected = None
    for i, line in enumerate(lines):
        if re.match(r"^\d+\. ", line):
            expected = "a"
        letter = re.match(r"^ {3}([a-z])\. ", line)
        if letter and expected:
            if letter.group(1) != expected:
                notes.append(f"line {i + 1}: sub-step {letter.group(1)}. should be {expected}.")
            expected = chr(ord(letter.group(1)) + 1)
    return notes


def command_mirror(skill: str) -> str:
    _, front, body = skill.split("---", 2)
    name = re.search(r"^name: (.+)$", front, re.M).group(1)
    description = re.search(r"^description: (.+)$", front, re.M).group(1)
    return f"---\nname: /{name}\nid: {name}\ncategory: Development\ndescription: {description}\n---{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True, help="the project's skills directory")
    parser.add_argument("--commands", type=Path, help="also mirror each skill as <dir>/<name>.md")
    parser.add_argument("--dry-run", action="store_true", help="report, write nothing")
    parser.add_argument("--force", action="store_true", help="overwrite hand-edited files")
    args = parser.parse_args()

    try:
        flags, values = load_profile(args.profile)
        templates = {p.stem: p.read_text() for p in sorted(TEMPLATES.glob("*.md"))}
        declared = set(flags)
        needed = {f for t in templates.values() for f in ANY_FLAG.findall(t)}
        if needed - declared:
            raise RenderError(f"flags missing from the profile: {', '.join(sorted(needed - declared))}")
        if declared - needed:
            raise RenderError(f"unknown flags in the profile: {', '.join(sorted(declared - needed))}")

        outputs: dict[Path, str] = {}
        used: set[str] = set()
        for name, template in templates.items():
            directive = DIRECTIVE.match(template)
            if directive:
                negate, flag = directive.groups()
                if flags[flag] == bool(negate):
                    print(f"skip   {name} (render-if {negate}{flag})")
                    continue
                template = template[directive.end():]
            try:
                skill = render(template, flags, values, used)
            except RenderError as err:
                raise RenderError(f"{name}: {err}") from err
            outputs[args.out / name / "SKILL.md"] = skill
            if args.commands:
                outputs[args.commands / f"{name}.md"] = command_mirror(skill)
    except (RenderError, json.JSONDecodeError, KeyError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 1

    for name in sorted(set(values) - used):
        print(f"warn   value {name} is in the profile but used by no rendered template")
    profile_text = " ".join(values.values()).lower()
    for path, text in outputs.items():
        for note in polish_notes(text):
            print(f"polish {path}: {note}")
        foreign = [w for w in FOREIGN_WORDS if w in text.lower() and w not in profile_text]
        if foreign:
            print(f"warn   {path}: mentions {', '.join(foreign)} (left over from the Cosmo example?)")

    for path, text in outputs.items():
        description = re.search(r'^description: "(.*)"$', text, re.M)
        if not description or '"' in description.group(1):
            print(f"error: {path}: description is not one double-quoted line (a value holds a quote?)", file=sys.stderr)
            return 1

    record_path = args.out / RECORD
    old = json.loads(record_path.read_text()) if record_path.exists() else {}
    previous = old.get("generated", {})
    templates_sha = sha256("".join(templates[k] for k in sorted(templates)))
    if old and old.get("templates_sha256") != templates_sha:
        print("info   the templates changed since the last render; review the diff of the regenerated skills")

    def key_of(path: Path) -> str:
        return os.path.relpath(path, args.out)

    edited = []
    for path in outputs:
        key = key_of(path)
        if path.exists() and key in previous and sha256(path.read_text()) != previous[key]:
            edited.append(str(path))
        elif path.exists() and key not in previous:
            edited.append(f"{path} (not generated by spdd-bootstrap)")
    if edited and not args.force:
        print("hand edits would be lost; rerun with --force after reviewing them:", file=sys.stderr)
        for key in edited:
            print(f"  {key}", file=sys.stderr)
        return 2

    current = {key_of(p) for p in outputs}
    for key in sorted(set(previous) - current):
        if (args.out / key).exists():
            print(f"stale  {args.out / key} was generated before but not now; delete it if that is intended")

    for path, text in outputs.items():
        print(f"{'would write' if args.dry_run else 'write'}  {path}")
        if not args.dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    if args.dry_run:
        return 0

    record = {
        "flags": flags,
        "values": {k: v.split("\n") if "\n" in v else v for k, v in values.items()},
        "templates_sha256": templates_sha,
        "generated": {key_of(p): sha256(t) for p, t in outputs.items()},
    }
    record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    print(f"write  {record_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
