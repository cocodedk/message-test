---
name: reader-test
description: Test whether a document delivers its intended message by giving it to a fresh reader who has no other context, asking what they took away, and scoring that against an answer key written in advance. Use when checking whether a deck, summary, report or handout still says what its source says, when an artifact has been rebuilt or edited, or when asked whether a document conveys its message. Catches drift and unintended readings that no readability score can see.
---

# Reader Test

The only cheap test that measures the message rather than the prose. You write
down what a reader must take away, hand the document and nothing else to a
reader who has never seen it, and compare.

**Use for:** decks, executive summaries, handouts, policies, release notes, any
artifact derived from a longer source.
**Not for:** proof that a specific named audience will agree or act. This
measures extraction, not persuasion.
**Output:** a scored table of intended points against what came back, plus the
list of things the reader believed that the document never said.

## Why it works, and the one rule that makes it valid

ISO 24495-1:2023 defines plain language by reader outcome: readers get what they
need, can find it, can understand it, and can use it. This test measures three
of those four directly.

**The rule: the reader must be genuinely fresh.** Anything that helped write the
document, or that has the source in its context, will pass its own test and tell
you nothing. In practice that means a subagent with no inherited context, given
only the file. If you cannot isolate the reader, say so and treat the result as
worthless rather than reassuring.

## Procedure

### 0. Give the reader what a reader would see

A deck is not its text. Slide order, what shares a slide, what is large and
what is a footnote: all of it carries message, and extracting the words throws
it away. So:

- **PPTX, DOCX:** render to PDF first and give the reader the PDF.
  `soffice --headless --convert-to pdf FILE --outdir DIR`
- **PDF:** give it directly. The reader can read the pages, including layout.
- **Markdown, plain text:** give the file.

Never hand a subagent a summary, a quote, or your description of the document.
The moment your words reach the reader, you are testing your summary rather
than the artifact, and the test silently passes.

### 1. Write the answer key first

Before opening the document, write what a reader must leave with. Three to five
entries. Each is a plain sentence, and each must be falsifiable, so "understands
the strategy" is not an entry but "knows the pilot runs in Denmark first" is.

For a document that asks for a decision, the key must always include: what
decision is being asked for, what it costs, what limits the result, and what
happens if it fails.

Writing the key is half the value of the test. If you cannot write it, the
document has no message yet and no test will fix that.

### 2. Send the reader in

Spawn a subagent with no context beyond the file. Give it the reader's role, not
your own. The prompt shape:

```
You are <the reader: their role, what they already know, how long they have>.
Read the attached file. You have no other information and cannot ask questions.

Answer in your own words:
1. What is this asking me to do or decide?
2. What would it cost, and what do I get?
3. What is the single biggest thing that could go wrong?
4. What did this document leave me unsure about?
5. If I had to act on this today, what would I do first?

Then: what is the one sentence you would repeat to a colleague?
```

Ask for judgement, not summary. A reader who summarises well can still have
drawn the wrong conclusion, and question 5 is where that shows.

### 3. Score

For each entry in the key, mark one of:

- **Landed.** The reader stated it, in their own words.
- **Missing.** The reader did not mention it.
- **Wrong.** The reader stated something that contradicts it. Worst outcome,
  because the document actively misled rather than merely failed.

Then list **inventions**: things the reader believed that the document never
said. Every invention is a defect with a location, and this list is the reason
to run the test at all. No readability metric produces it.

### 4. Report

```
Reader test: <artifact>
Reader: <who they were>
Key written before the test: yes

Landed   3/5
Missing  1  (what it costs)
Wrong    1  (believed the pilot covers all five countries)

Inventions
  "Every finding gets fixed automatically."  Not stated. Slide 2's flow
  implies it by showing no constraint. Fix: name the constraint on that slide.

One sentence they would repeat:
  "..."
```

Fix the wrong answers first, then the inventions, then the missing ones. A
missing point is a gap. A wrong point is damage.

## Running it more than once

- **Two readers, different roles**, catches more than one reader twice. A
  sceptic and a supporter read the same page differently.
- **Re-run after every rebuild** of a derived artifact. Drift between a source
  document and the deck made from it is exactly what this test is for, and it
  appears silently whenever the source is edited and the artifact is not.
- **Keep the key in version control** beside the artifact. A key that changes
  after a bad result is not a test.

## Honesty rules

- Report the reader's actual words, not your paraphrase of them.
- Never run this on a document you produced earlier in the same session and
  report the result as independent.
- A perfect score means a competent uninformed reader extracted the intended
  message. It does not mean the message is right.
