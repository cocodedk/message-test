---
name: clarity-index
description: Score a document out of 100 for clarity against a 20 item checklist, with 90 as the passing mark. Use when asked to measure, score or check how clear a document is, whether a deck, memo, report, policy, patient leaflet or board paper delivers its message, or before sending anything to an audience that cannot ask questions. Produces a scored report with the failing items and the smallest fix for each. Adapted from the CDC Clear Communication Index.
---

# Clarity Index

A scored checklist you can run on a document in about fifteen minutes, without
recruiting readers. It catches the failures that stop a message landing:
no single main message, no stated action, numbers nobody can use, risk
described without a chance of it happening.

**Use for:** any document meant to make a reader understand or do something.
**Not for:** proof that readers understood. Only readers can supply that, so
follow a pass here with the `reader-test` skill, and with `cloze-test` when the
document matters enough to spend real readers on it.
**Output:** a score out of 100, the failing items, and one concrete fix each.

## Where this comes from, and what is mine

The instrument is the CDC Clear Communication Index: twenty scored items, each
worth zero or one, converted to a score out of 100, with 90 as passing. The
seven areas it assesses are published: main message and call to action;
language; information design; state of the science; behavioural
recommendations; numbers; and risk.

The item wording below is my adaptation of those areas for general documents.
It is not a verbatim copy of the CDC instrument. When a score has to stand up
formally, use the authoritative score sheet at
`https://www.cdc.gov/ccindex/pdf/full-index-score-sheet.pdf` instead, and say
which one you used.

The 90 threshold comes from the CDC instrument, which was built and validated
for public health materials aimed at a general audience. It is a sensible
default and it is not calibrated for board papers, technical specifications or
legal text. Treat a score as a comparison against the same document last week,
or against a sibling artifact, rather than as an absolute grade. Say so when
reporting one.

## Before scoring, write these down

The score is meaningless without them, and disagreements about a score are
almost always disagreements about these three:

1. **Who the reader is.** Not "executives" but "a board member who has not read
   the underlying document and has eleven minutes."
2. **What they must take away.** Three to five things, in plain sentences.
3. **What they must be able to do afterwards.** The action, or "none" if the
   document only informs.

## The twenty items

Score one point when the material meets the item **everywhere it applies**, and
zero when any instance fails. Skip an area that genuinely does not apply, and
scale the total: score achieved divided by items scored, times 100.

**Score zero when you are unsure.** This matters more than any single item. A
model scoring a document it is asked to help with drifts generous, and a
generous scorer produces a number that moves between runs and reassures nobody.
The tie-break rule is: if you are arguing yourself into the point, it is a zero.
For every point you do award, you must be able to quote the text that earns it.

Worked example, item 1, "there is a main message and it is identifiable
without hunting":

- **One point:** the first slide reads "Approve the Denmark pilot and fund a
  team of four to six." You can quote it.
- **Zero:** the first slide reads "Spectrum Command: governed AI automation."
  That is a subject, not a message. A reader cannot tell what it claims.
- **Zero:** the message exists but sits on slide 7. It is present, not
  identifiable without hunting, and the item asks for both.

### Main message and call to action (4 items)

1. There is a main message, and it is identifiable without hunting.
2. The main message appears in the first visible position: the title, the
   subject line, the opening sentence or the first slide.
3. The main message is repeated or reinforced somewhere later.
4. There is one clear statement of what the reader should do, or an explicit
   statement that no action is required.

### Language (4 items)

5. The document uses everyday words. Rare words appear only where no common
   word carries the meaning.
6. Every unavoidable technical term is defined at first use.
7. Sentences carry one idea each, and the active voice is the default.
8. The document addresses the reader directly and consistently.

### Information design (4 items)

9. Headings and structure let a reader find a specific fact without reading the
   whole document.
10. Related information is grouped, and the order matches the order the reader
    needs it in.
11. Visuals, if present, carry meaning rather than decoration, and each one has
    a caption saying what it shows.
12. The layout leaves the eye somewhere to rest: white space, short blocks, no
    unbroken walls of text.

### State of the knowledge (2 items)

13. The document says what is known, and separately what is not known or not
    yet measured.
14. Where evidence is contested, incomplete or forecast rather than fact, the
    document says so in its own text rather than in a footnote elsewhere.

### Recommendations for the reader (2 items)

15. Each recommended action is specific enough to carry out without asking a
    follow-up question.
16. The document says what the reader gets by acting, or risks by not acting.

### Numbers (2 items)

17. Numbers a reader has to use are presented so they can be used: same base,
    stated denominator, no bare percentages standing in for counts.
18. The document explains what each important number means rather than leaving
    the reader to infer it.

### Risk (2 items)

19. Where the document describes a risk, it states both what could happen and
    how likely it is.
20. Where the document describes only benefits or only harms, it says that the
    other side exists and where to find it.

## Reporting

Report the score, then the failures, worst first. For every failed item give
the smallest change that would pass it, quoting the text you would change.
Never report a score without the reader definition it was scored against.

```
Clarity index: 78 / 100  (18 items scored, 14 passed)
Reader: a board member who has not read the source document, 11 minutes.

Failed items
  4  No stated action. The deck describes a decision but never says
     "approve X by date Y". Fix: one line on the decision slide.
  13 The estate numbers are presented as known. They are not measured.
     Fix: say "not yet measured" beside them.
  ...
```

## Honesty rules

- A high score is not evidence that the message landed. It is evidence that the
  known blockers are absent. Say this whenever you report a score.
- Do not score a document you wrote in this session without saying so. You will
  score your own intent rather than the text.
- If the reader definition is missing and cannot be obtained, say the score is
  provisional and state the reader you assumed.
