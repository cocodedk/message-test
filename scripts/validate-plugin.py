#!/usr/bin/env python3
"""Validate the message-test plugin repository.

Checks manifest correctness, frontmatter parseability, and the wiring between
skills and the scripts they shell out to.

Run from the repository root:  python3 scripts/validate-plugin.py
Exit code 0 = clean, 1 = errors found.
"""

from __future__ import annotations

import json
import os
import py_compile
import re
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required:  pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "message-test"
SKILLS = PLUGIN / "skills"
SCRIPTS = PLUGIN / "scripts"

errors: list[str] = []
warnings: list[str] = []


def error(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def split_frontmatter(path: Path) -> dict | None:
    """Return parsed frontmatter, or None if missing or unparseable."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        error(f"{rel(path)}: no YAML frontmatter block")
        return None
    end = text.find("\n---", 3)
    if end == -1:
        error(f"{rel(path)}: frontmatter block is not terminated")
        return None
    try:
        data = yaml.safe_load(text[4:end])
    except yaml.YAMLError as exc:
        # The bug this repo shipped with: an unquoted `[a] [b]` value is two
        # juxtaposed flow sequences. The runtime drops the WHOLE block silently
        # rather than complaining, so the command loads with no description.
        error(f"{rel(path)}: frontmatter does not parse as YAML — {exc}")
        return None
    if not isinstance(data, dict):
        error(f"{rel(path)}: frontmatter is not a mapping")
        return None
    return data


def check_manifests() -> None:
    plugin_manifest = PLUGIN / ".claude-plugin" / "plugin.json"
    marketplace_manifest = ROOT / ".claude-plugin" / "marketplace.json"

    for path in (plugin_manifest, marketplace_manifest):
        if not path.is_file():
            error(f"missing {rel(path)}")
            return

    try:
        plugin = json.loads(plugin_manifest.read_text(encoding="utf-8"))
        market = json.loads(marketplace_manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        error(f"invalid JSON in a manifest — {exc}")
        return

    if "name" not in plugin:
        error(f"{rel(plugin_manifest)}: 'name' is required")
    for field in ("version", "description", "author", "license"):
        if field not in plugin:
            warn(f"{rel(plugin_manifest)}: '{field}' is absent")

    for field in ("name", "owner", "plugins"):
        if field not in market:
            error(f"{rel(marketplace_manifest)}: '{field}' is required")

    for entry in market.get("plugins", []):
        source = entry.get("source")
        if isinstance(source, str):
            target = (ROOT / source).resolve()
            if not (target / ".claude-plugin" / "plugin.json").is_file():
                error(
                    f"{rel(marketplace_manifest)}: source '{source}' has no "
                    ".claude-plugin/plugin.json"
                )
        entry_version = entry.get("version")
        if entry_version and entry_version != plugin.get("version"):
            error(
                f"marketplace entry version {entry_version!r} disagrees with "
                f"plugin.json version {plugin.get('version')!r}"
            )
        elif not entry_version:
            warn(
                f"{rel(marketplace_manifest)}: entry has no 'version' — the release "
                "workflow cannot cross-check it"
            )


def check_commands() -> None:
    command_dir = PLUGIN / "commands"
    files = sorted(command_dir.glob("*.md"))
    if not files:
        error(f"{rel(command_dir)}: no commands found")
    for path in files:
        data = split_frontmatter(path)
        if data is None:
            continue
        if not data.get("description"):
            error(f"{rel(path)}: 'description' is required")


def check_skills() -> None:
    dirs = sorted(d for d in SKILLS.iterdir() if d.is_dir()) if SKILLS.is_dir() else []
    if not dirs:
        error(f"{rel(SKILLS)}: no skills found")
    for directory in dirs:
        skill = directory / "SKILL.md"
        if not skill.is_file():
            error(f"{rel(directory)}: no SKILL.md")
            continue
        data = split_frontmatter(skill)
        if data is None:
            continue
        for field in ("name", "description"):
            if not data.get(field):
                error(f"{rel(skill)}: '{field}' is required")
        name = data.get("name")
        if name and name != directory.name:
            error(f"{rel(skill)}: name {name!r} != directory {directory.name!r}")
        description = data.get("description") or ""
        if len(description) > 1024:
            warn(f"{rel(skill)}: description is {len(description)} chars — very long")


def check_script_references() -> None:
    """Every script a skill shells out to must exist.

    The skills invoke these by path. A rename would break them at runtime with
    no warning anywhere, which is exactly the class of failure this repo has
    already shipped once.
    """
    pattern = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]+)")
    sources = sorted(PLUGIN.rglob("*.md"))
    referenced: set[str] = set()

    for source in sources:
        text = source.read_text(encoding="utf-8")
        for match in set(pattern.findall(text)):
            referenced.add(match)
            target = PLUGIN / match
            if not target.exists():
                error(f"{rel(source)}: references missing file '{match}'")

    for script in sorted(SCRIPTS.glob("*.py")) if SCRIPTS.is_dir() else []:
        name = f"scripts/{script.name}"
        if name not in referenced:
            warn(f"{rel(script)}: not referenced by any skill or command")


def check_scripts() -> None:
    if not SCRIPTS.is_dir():
        return
    scripts = sorted(SCRIPTS.glob("*.py"))
    if not scripts:
        error(f"{rel(SCRIPTS)}: no scripts found")
    for script in scripts:
        text = script.read_text(encoding="utf-8")
        if text.startswith("#!") and not os.access(script, os.X_OK):
            error(f"{rel(script)}: has a shebang but is not executable (chmod +x)")
        with tempfile.TemporaryDirectory() as tmp:
            try:
                py_compile.compile(
                    str(script),
                    cfile=str(Path(tmp) / "out.pyc"),
                    doraise=True,
                )
            except py_compile.PyCompileError as exc:
                error(f"{rel(script)}: does not compile — {exc}")


def check_placeholders() -> None:
    needles = ("<OWNER>", "[owner]", "[repo]", "[ProjectName]")
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git/" in str(path):
            continue
        if path.suffix not in {".md", ".json", ".yml", ".yaml", ".sh", ".html", ".txt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for needle in needles:
            if needle in text:
                error(f"{rel(path)}: unsubstituted placeholder {needle!r}")


def main() -> int:
    check_manifests()
    check_commands()
    check_skills()
    check_script_references()
    check_scripts()
    check_placeholders()

    for message in warnings:
        print(f"warning: {message}")
    for message in errors:
        print(f"error: {message}", file=sys.stderr)

    if errors:
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)", file=sys.stderr)
        return 1
    print(f"\nvalidation passed ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
