#!/usr/bin/env python3
"""extract.py: pull readable prose out of a document for the cloze test.

The cloze test needs continuous prose. Office files and PDFs keep their text
inside a container, so this pulls it out.

For the reader test, do NOT use this. Render the file to PDF instead and let the
reader read the PDF, because on a deck or a formatted report the layout carries
part of the message and extracted text throws it away:

    soffice --headless --convert-to pdf FILE --outdir DIR

Usage
-----
  python3 extract.py FILE [--out FILE.txt]

Handles .pptx, .docx, .pdf, .md, .txt, .html. PDF extraction needs the
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


def from_office(path: Path, tag: str) -> str:
    """Text runs out of an OOXML container: <a:t> for pptx, <w:t> for docx."""
    with zipfile.ZipFile(path) as archive:
        if tag == "a:t":
            parts = sorted(
                (n for n in archive.namelist()
                 if re.match(r"ppt/slides/slide\d+\.xml$", n)),
                key=lambda n: int(re.search(r"\d+", n.split("/")[-1]).group()),
            )
        else:
            parts = [n for n in archive.namelist() if n == "word/document.xml"]
        if not parts:
            sys.exit(f"no readable parts found inside {path.name}")
        blocks = []
        for name in parts:
            body = archive.read(name).decode("utf-8", "ignore")
            runs = [html.unescape(t) for t in
                    re.findall(rf"<{tag}(?: [^>]*)?>(.*?)</{tag}>", body, re.S)]
            if runs:
                blocks.append(" ".join(runs))
    return "\n\n".join(blocks)


def from_pdf(path: Path) -> str:
    if not shutil.which("pdftotext"):
        sys.exit("pdftotext is not installed; install poppler-utils or convert "
                 "the file to text another way")
    done = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                          capture_output=True, text=True)
    if done.returncode:
        sys.exit(f"pdftotext failed: {done.stderr.strip()}")
    return done.stdout


def from_html(text: str) -> str:
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", text, flags=re.S | re.I)
    return html.unescape(re.sub(r"<[^>]+>", " ", text))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("document", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    if not args.document.exists():
        sys.exit(f"no such file: {args.document}")

    suffix = args.document.suffix.lower()
    if suffix == ".pptx":
        text = from_office(args.document, "a:t")
    elif suffix == ".docx":
        text = from_office(args.document, "w:t")
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

    words = len(text.split())
    if words < 120:
        print(f"warning: only {words} words extracted, which is short for a "
              f"cloze passage. A deck usually is: test the talk track or the "
              f"source document instead.", file=sys.stderr)

    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
        print(f"{words} words -> {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
