#!/usr/bin/env python3
"""extract.py: pull readable prose out of a document for the cloze test.

Keeps paragraph structure, because the cloze script relies on it to tell prose
from headings, bullets and table rows. Joining every text run into one blob
would hide all of that and produce a test built from slide furniture.

For the reader test, do NOT use this. Render the file to PDF and let the reader
read the PDF, because on a deck or a formatted report the layout carries part of
the message:

    soffice --headless --convert-to pdf FILE --outdir DIR

Usage
-----
  python3 "${CLAUDE_PLUGIN_ROOT}/scripts/extract.py" FILE [--out FILE.txt]
                                                          [--notes]

  --notes   for a .pptx, take the speaker notes instead of the slide text.
            Slides rarely hold enough continuous prose to cloze test; notes
            usually do.

Handles .pptx, .docx, .odp, .odt, .pdf, .md, .txt, .html. PDF needs the
`pdftotext` command; everything else uses the standard library only.
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

# One entry per format: the archive members to read, and the element that marks
# a paragraph inside them. Runs inside a paragraph join with nothing; paragraphs
# are separated by a blank line.
OOXML = {
    ".pptx": (r"ppt/slides/slide(\d+)\.xml$", "a:p", "a:t"),
    ".pptx-notes": (r"ppt/notesSlides/notesSlide(\d+)\.xml$", "a:p", "a:t"),
    ".docx": (r"word/document\.xml$", "w:p", "w:t"),
    ".odp": (r"content\.xml$", "text:p", None),
    ".odt": (r"content\.xml$", "text:p", None),
}


def ordered_members(archive: zipfile.ZipFile, pattern: str) -> list[str]:
    matches = [(m, re.search(pattern, m)) for m in archive.namelist()]
    found = [(m, hit) for m, hit in matches if hit]
    if found and found[0][1].groups():
        found.sort(key=lambda pair: int(pair[1].group(1)))
    return [m for m, _ in found]


def from_zip_xml(path: Path, kind: str) -> str:
    pattern, para_tag, run_tag = OOXML[kind]
    with zipfile.ZipFile(path) as archive:
        members = ordered_members(archive, pattern)
        if not members:
            sys.exit(f"no readable parts found inside {path.name}")
        paragraphs: list[str] = []
        for name in members:
            body = archive.read(name).decode("utf-8", "ignore")
            for block in re.findall(rf"<{para_tag}(?:\s[^>]*)?>(.*?)</{para_tag}>",
                                    body, re.S):
                if run_tag:
                    runs = re.findall(rf"<{run_tag}(?:\s[^>]*)?>(.*?)</{run_tag}>",
                                      block, re.S)
                    line = "".join(runs)
                else:
                    line = re.sub(r"<[^>]+>", "", block)
                line = html.unescape(line).strip()
                if line:
                    paragraphs.append(line)
    return "\n\n".join(paragraphs)


def from_pdf(path: Path) -> str:
    if not shutil.which("pdftotext"):
        sys.exit("pdftotext is not installed; install poppler-utils or convert "
                 "the file to text another way")
    done = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                          capture_output=True, text=True, encoding="utf-8")
    if done.returncode:
        sys.exit(f"pdftotext failed: {(done.stderr or '').strip()}")
    return done.stdout


def from_html(text: str) -> str:
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", text, flags=re.S | re.I)
    text = re.sub(r"</(p|div|h\d|li|tr)>", "\n\n", text, flags=re.I)
    return html.unescape(re.sub(r"<[^>]+>", " ", text))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("document", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--notes", action="store_true",
                        help="take pptx speaker notes rather than slide text")
    args = parser.parse_args()

    if not args.document.exists():
        sys.exit(f"no such file: {args.document}")

    suffix = args.document.suffix.lower()
    if args.notes and suffix != ".pptx":
        sys.exit("--notes applies to .pptx only")

    if suffix == ".pptx":
        text = from_zip_xml(args.document, ".pptx-notes" if args.notes else ".pptx")
    elif suffix in (".docx", ".odp", ".odt"):
        text = from_zip_xml(args.document, suffix)
    elif suffix == ".pdf":
        text = from_pdf(args.document)
    elif suffix in (".html", ".htm"):
        text = from_html(args.document.read_text(encoding="utf-8", errors="ignore"))
    elif suffix in (".md", ".txt", ".markdown"):
        text = args.document.read_text(encoding="utf-8")
    else:
        sys.exit(f"unsupported file type: {suffix}")

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    paragraphs = [p for p in text.split("\n\n") if len(p.split()) >= 20]
    words = len(text.split())
    prose_words = sum(len(p.split()) for p in paragraphs)

    if prose_words < 150:
        print(f"warning: {words} words extracted but only {prose_words} of them "
              f"sit in paragraphs long enough to cloze test. Slide text is "
              f"usually like this. Try --notes, or test the talk track or the "
              f"source document instead.", file=sys.stderr)

    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
        print(f"{words} words, {prose_words} in usable paragraphs -> {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
