#!/usr/bin/env python3
"""Verify every relative link in the repository's markdown resolves to a file.

External links (http, https, mailto) and pure anchors are skipped — this only
catches the kind of rot that follows a file rename.

Run from the repository root:  python3 scripts/check-links.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "#", "tel:")


def main() -> int:
    broken: list[str] = []
    checked = 0

    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for raw in LINK.findall(text):
            if raw.startswith(SKIP_PREFIXES):
                continue
            target = unquote(raw.split("#", 1)[0])
            if not target:
                continue
            checked += 1
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                broken.append(f"{path.relative_to(ROOT)} -> {raw}")

    for entry in broken:
        print(f"error: broken link: {entry}", file=sys.stderr)

    if broken:
        print(f"\n{len(broken)} broken link(s) of {checked} checked", file=sys.stderr)
        return 1
    print(f"all {checked} relative markdown links resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
