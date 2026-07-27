# message-test

Three ways to find out whether a document actually delivers its message, and one
clear statement of what each of them can and cannot prove.

A readability score tells you how hard a text is to process. It does not tell
you whether the reader took away what you meant. Those are different questions,
and only the second one matters when a document has to carry a decision.

## What it gives you

| Skill | What it measures | Who runs it | Cost |
|---|---|---|---|
| `clarity-index` | Whether the known blockers are absent: no main message, no stated action, unusable numbers, risk without likelihood. Scored out of 100, 90 passes. | A model, in minutes | Free |
| `reader-test` | Whether a fresh reader extracts the intended message, and what they believe that the document never said. | A model, isolated from your context | Nearly free |
| `cloze-test` | Whether real readers can follow the text. Every sixth word removed and restored; 60 percent or more passes. | Humans only | Real people's time |

The command `/message-test:run <file> [reader] [source document]` runs the first
two in order and tells you whether the third is worth it.

## The three rules that matter most

**The reader must really be fresh, and a subagent often is not.** A subagent
inherits the project's `CLAUDE.md` and memory files. If those explain the
subject, the reader answers from them and passes a document that carries no
message of its own. Run the reader in a separate session outside the project
unless you have checked that the project's instructions say nothing about the
subject.

**The answer key must not come from the document under test.** A key skimmed
off the artifact measures whether the artifact repeats its own headlines. It
always does. Take the key from the source document or from the author, or say
in the report that this run did not test drift.

**A model must never take the cloze test.** A model restores a missing word from
context far better than any person, so it scores well on text no human can
follow. Use it to build the sheet and score the returns, never to answer one.

## Install

```
/plugin marketplace add cocodedk/message-test
/plugin install message-test@message-test
```

Then:

```
/message-test:run deliverables/some-deck.pptx "a board member with 11 minutes" \
    governance/the-source-document.md
```

A PPTX, DOCX, ODP or ODT is rendered to PDF first, so the reader sees the layout
rather than a pile of extracted words. The cloze script needs plain prose, so
`${CLAUDE_PLUGIN_ROOT}/scripts/extract.py` pulls text out of Office files,
OpenDocument files and PDFs for that one.

## Where the methods come from

- **ISO 24495-1:2023**, the plain language standard, defines the target as a
  reader outcome: readers get what they need, can find it, understand it and use
  it. It explicitly rejects readability formulas as the test of success.
  `https://www.iso.org/standard/78907.html`
- **CDC Clear Communication Index**: twenty scored items, out of 100, 90 to
  pass, about fifteen minutes. `clarity-index` adapts its seven published areas
  for general documents. For a score that has to stand up formally, use the CDC
  score sheet itself. `https://www.cdc.gov/ccindex/pdf/full-index-score-sheet.pdf`
- **Cloze procedure**, Taylor 1953, still the basis on which several readability
  formulas were calibrated. Threshold and method as described by Nielsen Norman
  Group. `https://www.nngroup.com/articles/cloze-test-reading-comprehension/`

## What none of this proves

That the message is right, that the audience will agree, or that a specific
person will act. It catches the document that says something different from what
you meant, which is the failure that goes unnoticed for longest.
