---
name: cloze-test
description: Prepare and score a cloze test, the classic measurement of whether real readers can actually follow a text. Deletes every sixth word, human readers restore them, and a score of 60 percent or higher means the text is comprehensible for that audience. Use when a document matters enough to spend real readers on, or when asked for hard evidence that a text is readable by a specific group. Language models must never take this test; the skill explains why.
---

# Cloze Test

The strongest evidence you can get that a text is readable by a particular
audience, because the text itself is the measuring instrument. Not a grade
level, not a formula: a score for this document and these readers.

**Use for:** the one or two documents per programme that justify spending real
people's time.
**Not for:** routine checks. Use `clarity-index` and `reader-test` for those.
**Output:** a participant sheet, an answer key, and a scored result with the
passages that failed.

## The rule that makes or breaks this

**A language model must never take this test.** Predicting a masked word is the
training objective of every large language model, so a model will restore the
gaps in a text that no human can follow. A model score here is not weak
evidence, it is no evidence. If someone asks for an automated cloze run, refuse
and explain, then offer `reader-test`, which does work with a fresh model.

Models are still useful for preparing the sheet, scoring returned sheets against
the key, and interpreting the result.

## Procedure

### 1. Choose the passage

Take continuous prose of roughly 250 to 300 words from the part of the document
that carries the message. Skip tables, headings, bullet lists and captions:
gaps in fragments measure guessing, not comprehension. Leave the first and last
sentences whole so readers have somewhere to stand.

### 2. Make the gaps

Delete every sixth word and replace it with a blank of fixed length, so the
length of the blank gives nothing away. A higher interval makes an easier test;
six is the standard. Generate the sheet with the bundled script:

```
python3 scripts/cloze.py DOCUMENT.md --start "the sentence to start from" \
    --words 280 --every 6 --out sheet.md --key key.md
```

### 3. Run it

Four to six readers from the real audience, not colleagues who helped write it.
Each works alone, without the original, with no time limit. Tell them to guess
at every blank and that nobody expects a perfect score, because blanks left
empty out of politeness distort the result more than wrong guesses do.

### 4. Score

Count a blank correct when the reader supplies the exact word, a synonym that
preserves the meaning, or a recognisable misspelling of either. Score each
reader as a percentage, then average.

- **60 percent or above:** comprehensible for that audience.
- **40 to 60:** the reader needs help, a briefing or a walkthrough. It will not
  stand alone.
- **Below 40:** the audience cannot follow this text unaided. Rewrite rather
  than tidy.

### 5. Read the pattern, not just the number

The average tells you whether to rewrite. The pattern tells you what to rewrite.
Look at which blanks failed across several readers at once. Clusters mark the
sentences where meaning breaks, and those are the sentences to fix first. A
scattered failure pattern with an acceptable average usually means unfamiliar
vocabulary; a clustered one means the argument itself does not follow.

## Reporting

```
Cloze test: <document>, <passage described>
Readers: 5 from <audience>
Average restoration: 64 percent  (range 51 to 78)
Verdict: comprehensible for this audience, with one weak passage.

Failure clusters
  Blanks 22 to 29 ("...the broker validates the approval binding...")
  4 of 5 readers failed. The sentence carries three ideas. Split it.
```

Always report the range as well as the average. One strong reader can carry an
average past 60 while most of the room is lost.

## Honesty rules

- Report the number of readers. Fewer than four is an indication, not a result.
- Never mix a model's answers into a human sample.
- The score belongs to that passage and that audience. Do not carry it over to
  the rest of the document or to a different group of readers.

## Source

The procedure follows the standard cloze method as described by Nielsen Norman
Group at `https://www.nngroup.com/articles/cloze-test-reading-comprehension/`,
including the 60 percent threshold and the every sixth word default. The method
dates to Taylor in 1953 and remains the basis on which several readability
formulas were calibrated.
