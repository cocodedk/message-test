#!/usr/bin/env python3
"""cloze.py: build a cloze test sheet and answer key, then score what comes back.

A cloze test measures whether real readers can follow a specific text. Every nth
word is replaced by a blank, readers restore what they can, and the percentage
restored is the score. Sixty percent or more means the text is comprehensible
for that audience.

Language models must not take the test. A model predicts a missing word from
context far better than any human reader, so its score says nothing about
whether a person can follow the text. Use this script to prepare the sheet and
to score returned sheets, never to answer one.

Usage
-----
  Build a sheet:
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/cloze.py" build DOCUMENT.md \\
        [--start TEXT] [--words 280] [--every 6] [--out sheet.md] [--key key.md]

  Score returned sheets:
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/cloze.py" score key.md \\
        reader1.txt reader2.txt ...

Build reads Markdown or plain text. For a PPTX, DOCX, ODP or PDF, run
extract.py first and pass its output here.

  --start   begin the passage at the first sentence containing this text;
            without it the passage starts at the first prose paragraph
  --words   target passage length, default 280
  --every   delete every nth word, default 6; a higher number is easier

Answer files are one line per blank, "12. word". Blank or missing lines count
as unanswered. Matching is exact after case and accent folding, so the script
reports near misses separately: a human decides whether a synonym counts, which
is why the report separates certain marks from ones needing a decision.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

BLANK = "________"
# Unicode letters, so Nordic and other accented words stay whole. A word may
# hold an internal apostrophe or hyphen.
LETTER = r"[^\W\d_]"
WORD = re.compile(rf"{LETTER}(?:[{''}'’-]?{LETTER})*", re.UNICODE)


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
    # Paired emphasis only, so file_names and snake_case survive intact.
    joined = re.sub(r"\*\*(.+?)\*\*", r"\1", joined, flags=re.S)
    joined = re.sub(r"__(.+?)__", r"\1", joined, flags=re.S)
    joined = re.sub(r"(?<!\w)\*(\S.*?\S)\*(?!\w)", r"\1", joined, flags=re.S)

    paragraphs = []
    for block in joined.split("\n\n"):
        block = re.sub(r"\s+", " ", block).strip()
        # A paragraph ending in a colon introduced a list or table that was
        # stripped above. Drop that clause now, before sentences are split,
        # or it fuses with the next paragraph into a sentence nobody wrote.
        if block.endswith(":"):
            block = re.sub(r"[^.!?]*:$", "", block).strip()
        if len(block.split()) >= 20:
            paragraphs.append(block)
    return "\n\n".join(paragraphs)


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
    return [p.strip() for p in parts if p.strip()]


FURNITURE = re.compile(r"[→•·|]|\.{3,}|\b\d+\s*[.)]\s")


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
            continue
        picked.append(sentence)
        count += len(sentence.split())
        if count >= target:
            break
    if len(picked) < 3:
        sys.exit("passage too short to test; lower --words or pick another start")
    return picked


def fold(word: str) -> str:
    stripped = unicodedata.normalize("NFKD", word.lower())
    return "".join(c for c in stripped if not unicodedata.combining(c))


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


def read_numbered(path: Path) -> dict[int, str]:
    values: dict[int, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        hit = re.match(r"\s*(\d+)[.)]\s*(.*)$", line)
        if hit:
            answer = hit.group(2).strip().strip("_").strip()
            values[int(hit.group(1))] = answer
    return values


def build(args: argparse.Namespace) -> None:
    if args.document.suffix.lower() not in (".md", ".markdown", ".txt"):
        sys.exit("build reads Markdown or plain text. For a PPTX, DOCX, ODP or "
                 "PDF, run extract.py first and pass its output here.")
    if args.every < 3:
        sys.exit("--every below 3 leaves too little context to restore anything")

    text = prose_only(args.document.read_text(encoding="utf-8"))
    picked = choose_passage(text, args.start, args.words)
    body, answers = gap(picked, args.every)
    if len(answers) < 15:
        sys.exit(f"only {len(answers)} blanks; too few to score meaningfully. "
                 f"Raise --words or lower --every.")

    furniture = FURNITURE.findall(body)
    if furniture:
        print(f"warning: the passage contains {len(furniture)} pieces of layout "
              f"furniture such as arrows, bullets or numbered fragments. Readers "
              f"cannot restore those from comprehension. Pick another --start.",
              file=sys.stderr)

    total = sum(len(s.split()) for s in picked)
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
        f"Passage of {total} words, every {args.every}th word removed, "
        f"{len(answers)} blanks.\n\n"
        f"Score with: cloze.py score KEY reader1.txt reader2.txt ...\n"
        f"A blank counts when the reader gives the exact word, a synonym that "
        f"keeps the meaning, or a recognisable misspelling. The script marks "
        f"exact and near matches; a person decides the synonyms.\n\n"
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
        print(f"{len(answers)} blanks over {total} words, wrote {where}")
    else:
        print(sheet)


def score(args: argparse.Namespace) -> None:
    key = read_numbered(args.key)
    if not key:
        sys.exit(f"no numbered answers found in {args.key}")

    per_reader: list[tuple[str, float]] = []
    missed: dict[int, int] = {number: 0 for number in key}
    undecided: list[str] = []

    for path in args.answers:
        given = read_numbered(path)
        correct = 0
        for number, expected in key.items():
            answer = given.get(number, "")
            if not answer:
                missed[number] += 1
                continue
            if fold(answer) == fold(expected):
                correct += 1
            elif fold(answer).startswith(fold(expected)[:4]):
                correct += 1        # recognisable misspelling
            else:
                missed[number] += 1
                undecided.append(f"  blank {number}: key {expected!r}, "
                                 f"{path.name} said {answer!r}")
        per_reader.append((path.name, 100 * correct / len(key)))

    scores = [value for _, value in per_reader]
    average = sum(scores) / len(scores)
    verdict = ("comprehensible for this audience" if average >= 60 else
               "needs a briefing or walkthrough; will not stand alone"
               if average >= 40 else
               "this audience cannot follow the text unaided; rewrite")

    print(f"Cloze result: {args.key.name}")
    print(f"Readers: {len(per_reader)}"
          + ("   (fewer than four is an indication, not a result)"
             if len(per_reader) < 4 else ""))
    for name, value in per_reader:
        print(f"  {name:<28} {value:5.1f} percent")
    print(f"Average {average:.1f} percent, range {min(scores):.1f} to "
          f"{max(scores):.1f}")
    print(f"Verdict: {verdict}")

    threshold = max(2, len(per_reader) // 2)
    clusters = sorted((n for n, count in missed.items() if count >= threshold))
    if clusters:
        runs, current = [], [clusters[0]]
        for number in clusters[1:]:
            if number == current[-1] + 1:
                current.append(number)
            else:
                runs.append(current)
                current = [number]
        runs.append(current)
        print(f"\nBlanks failed by {threshold} or more readers:")
        for run in runs:
            span = f"{run[0]} to {run[-1]}" if len(run) > 1 else f"{run[0]}"
            words = ", ".join(key[n] for n in run)
            mark = "  <- cluster, rewrite this sentence" if len(run) > 2 else ""
            print(f"  {span}: {words}{mark}")

    if undecided:
        print(f"\nNot counted, decide by hand whether these are synonyms "
              f"({len(undecided)}):")
        for line in undecided[:25]:
            print(line)
        if len(undecided) > 25:
            print(f"  ... and {len(undecided) - 25} more")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="mode", required=True)

    maker = sub.add_parser("build", help="make a sheet and answer key")
    maker.add_argument("document", type=Path)
    maker.add_argument("--start")
    maker.add_argument("--words", type=int, default=280)
    maker.add_argument("--every", type=int, default=6)
    maker.add_argument("--out", type=Path)
    maker.add_argument("--key", type=Path)
    maker.set_defaults(run=build)

    scorer = sub.add_parser("score", help="score returned sheets against a key")
    scorer.add_argument("key", type=Path)
    scorer.add_argument("answers", nargs="+", type=Path)
    scorer.set_defaults(run=score)

    args = parser.parse_args()
    args.run(args)


if __name__ == "__main__":
    main()
