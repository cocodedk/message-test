#!/usr/bin/env python3
"""cloze.py: build a cloze test sheet and its answer key from a document.

A cloze test measures whether real readers can follow a specific text. Every
nth word is replaced by a blank of fixed width, readers restore what they can,
and the percentage restored is the score. Sixty percent or more means the text
is comprehensible for that audience.

Language models must not take the test. Restoring masked words is what they are
trained to do, so a model scores well on text no human can follow. Use this
script to prepare the sheet and to score returned sheets, never to answer it.

Usage
-----
  python3 cloze.py DOCUMENT [--start TEXT] [--words 280] [--every 6]
                   [--out sheet.md] [--key key.md]

  --start   begin the passage at the first sentence containing this text;
            without it the passage starts at the first prose paragraph
  --words   target passage length, default 280
  --every   delete every nth word, default 6; a higher number is an easier test
  --out     participant sheet, default stdout
  --key     answer key; without it the key is appended to the sheet, which is
            fine for scoring but not for handing to a reader

Markdown headings, code fences, tables, images, block quotes and list markers
are dropped before the passage is chosen, because a gap inside a fragment
measures guessing rather than comprehension. The first and last sentences of
the passage are never gapped, so readers have somewhere to stand.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

BLANK = "________"
WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*")


def prose_only(text: str) -> str:
    """Strip everything that is not continuous prose."""
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)       # frontmatter
    text = re.sub(r"```.*?```", " ", text, flags=re.S)             # code fences
    text = re.sub(r"`[^`]*`", " ", text)                           # inline code
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)              # images
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)           # links
    kept = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            kept.append("")
            continue
        if stripped.startswith(("#", ">", "|", "---", "===")):
            continue
        if re.match(r"^([-*+]|\d+\.)\s", stripped):                # list items
            continue
        kept.append(stripped)
    joined = "\n".join(kept)
    joined = re.sub(r"\*\*|__|\*|_", "", joined)                   # emphasis
    paragraphs = [re.sub(r"\s+", " ", p).strip() for p in joined.split("\n\n")]
    return "\n\n".join(p for p in paragraphs if len(p.split()) >= 20)


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
    return [p.strip() for p in parts if p.strip()]


def choose_passage(text: str, start: str | None, target: int) -> list[str]:
    all_sentences = sentences(text.replace("\n\n", " "))
    if not all_sentences:
        sys.exit("no continuous prose found in this document")
    begin = 0
    if start:
        lowered = start.lower()
        matches = [i for i, s in enumerate(all_sentences) if lowered in s.lower()]
        if not matches:
            sys.exit(f"--start text not found in the prose: {start!r}")
        begin = matches[0]
    picked, count = [], 0
    for sentence in all_sentences[begin:]:
        if sentence.endswith(":"):
            # It introduced a table or list that prose_only removed, so keeping
            # it would leave the reader staring at a colon with nothing after it.
            continue
        picked.append(sentence)
        count += len(sentence.split())
        if count >= target:
            break
    if len(picked) < 3:
        sys.exit("passage too short to test; lower --words or pick another start")
    return picked


def gap(picked: list[str], every: int) -> tuple[str, list[str]]:
    """Blank every nth word, leaving the first and last sentences whole."""
    answers: list[str] = []
    counter = 0
    out: list[str] = [picked[0]]
    for sentence in picked[1:-1]:
        pieces, last = [], 0
        for match in WORD.finditer(sentence):
            counter += 1
            if counter % every:
                continue
            answers.append(match.group(0))
            pieces.append(sentence[last:match.start()])
            pieces.append(f"[{len(answers)}]{BLANK}")
            last = match.end()
        pieces.append(sentence[last:])
        out.append("".join(pieces))
    out.append(picked[-1])
    return " ".join(out), answers


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("document", type=Path)
    parser.add_argument("--start")
    parser.add_argument("--words", type=int, default=280)
    parser.add_argument("--every", type=int, default=6)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--key", type=Path)
    args = parser.parse_args()

    if args.every < 3:
        sys.exit("--every below 3 leaves too little context to restore anything")

    if args.document.suffix.lower() not in (".md", ".markdown", ".txt"):
        sys.exit("this reads Markdown or plain text. For a PPTX, DOCX or PDF, "
                 "run scripts/extract.py first and pass the result here.")

    text = prose_only(args.document.read_text(encoding="utf-8"))
    picked = choose_passage(text, args.start, args.words)
    body, answers = gap(picked, args.every)
    if len(answers) < 15:
        sys.exit(f"only {len(answers)} blanks; too few to score meaningfully. "
                 f"Raise --words or lower --every.")

    sheet = (
        f"# Reading exercise\n\n"
        f"Some words have been removed from the passage below. Write your best "
        f"guess for each numbered blank. Guess at every one, even when you are "
        f"unsure. Nobody is expected to get them all, and a blank left empty "
        f"tells us less than a wrong guess does. Work alone and take the time "
        f"you need.\n\n"
        f"Passage from: {args.document.name}\n"
        f"Blanks to fill: {len(answers)}\n\n---\n\n{body}\n\n---\n\n"
        + "\n".join(f"{i}. ______________________" for i in range(1, len(answers) + 1))
        + "\n"
    )
    key = (
        f"# Answer key: {args.document.name}\n\n"
        f"Passage of {sum(len(s.split()) for s in picked)} words, every "
        f"{args.every}th word removed, {len(answers)} blanks.\n\n"
        f"Score a blank correct for the exact word, a synonym that keeps the "
        f"meaning, or a recognisable misspelling of either. Average across "
        f"readers. Sixty percent or above means the passage is comprehensible "
        f"for that audience. Report the range as well as the average, and look "
        f"for blanks that several readers failed together: those clusters mark "
        f"the sentences to rewrite.\n\n"
        + "\n".join(f"{i}. {word}" for i, word in enumerate(answers, start=1))
        + "\n"
    )

    if args.key:
        args.key.write_text(key, encoding="utf-8")
    else:
        sheet += "\n\n" + key

    if args.out:
        args.out.write_text(sheet, encoding="utf-8")
        where = f"{args.out}" + (f" and {args.key}" if args.key else "")
        print(f"{len(answers)} blanks over {sum(len(s.split()) for s in picked)} "
              f"words, wrote {where}")
    else:
        print(sheet)


if __name__ == "__main__":
    main()
