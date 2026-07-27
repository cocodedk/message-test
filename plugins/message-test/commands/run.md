---
description: Measure how well a document conveys its message
argument-hint: "[file] [\"who the reader is\"] [\"source document the file came from\"]"
---

Measure whether `$1` delivers its message.

The reader, if given, is: $2
The source document it was derived from, if given, is: $3

Positional arguments split on whitespace, so these bind correctly only when each was
quoted. If `$2` or `$3` looks like a stray fragment of a longer unquoted phrase rather than
a coherent answer, treat it as absent and ask for the reader instead of proceeding on it.
The full invocation was: $ARGUMENTS

Work in this order and stop at the first step that fails badly enough to make
the later ones pointless.

## 0. Prepare the artifact

If `$1` is a PPTX, DOCX, ODP or ODT, render it to PDF first and use that,
because layout carries part of the message and extracted text loses it:

```
soffice --headless --convert-to pdf "$1" --outdir <a scratch directory>
```

A PDF or Markdown file can be used as it is. Say in the report which form was
read.

## 1. Establish the reader and the intended message

If the reader was not given, ask for it in one question, or state the reader you
are assuming and carry on.

Then write the answer key: the three to five things a reader must take away.
For anything that asks for a decision, that list always includes what is being
asked for, what it costs, what limits the result, and what happens if it fails.

**Take the key from `$3` if a source document was given, otherwise from the
author.** A key skimmed off `$1` itself cannot fail and cannot detect drift,
which is the main thing this command is for. If neither is available, write it
from the artifact and say plainly in the report that this run tested internal
consistency only.

Show the list and where it came from. Everything after depends on it.

## 2. Score the clarity index

Invoke the `clarity-index` skill on the file. Report the score out of 100, the
failing items worst first, and the smallest fix for each.

If the score is below 70, stop and report. The document has structural
problems that will dominate any reader result, and fixing those first is
cheaper than measuring twice.

## 3. Run the reader test

Invoke the `reader-test` skill and follow its isolation rule. A subagent
inherits this project's instruction files, so if those describe the document's
subject at all, run the reader in a separate session outside the project
instead. Ask the reader questions, ask what it already knew, and score what
comes back against the key from step 1.

Pay most attention to two things: anything the reader got wrong, which means the
document actively misled, and anything the reader believed that the document
never said.

## 4. Decide whether a cloze test is worth it

Recommend one only when the document is going to an audience that cannot ask
questions and the cost of being misunderstood is high. If it is worth it, use
the `cloze-test` skill to prepare the sheet and key. Never generate model
answers for it, and say why when you decline.

## Report

One page. The score, the reader result as landed, missing and wrong, the
inventions, and a ranked list of fixes. Lead with whether the message landed,
not with the number.

State plainly what was and was not measured: a passing index score means the
known blockers are absent, and a passing reader test means one competent
uninformed reader extracted the intended message. Neither is proof that the
real audience will understand or agree.
