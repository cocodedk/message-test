---
description: Measure how well a document conveys its message
argument-hint: [file] [optional: who the reader is]
---

Measure whether `$1` delivers its message. The reader, if given, is: $2

Work in this order and stop at the first step that fails badly enough to make
the later ones pointless.

## 1. Establish the reader and the intended message

If the reader was not given, ask for it in one question, or state the reader you
are assuming and carry on. Then write down, before reading the document
closely, the three to five things a reader must take away. For anything that
asks for a decision, that list always includes what is being asked for, what it
costs, what limits the result, and what happens if it fails.

Show this list. It is the answer key, and everything after depends on it.

## 2. Score the clarity index

Invoke the `clarity-index` skill on the file. Report the score out of 100, the
failing items worst first, and the smallest fix for each.

If the score is below about 70, stop and report. The document has structural
problems that will dominate any reader result, and fixing those first is
cheaper than measuring twice.

## 3. Run the reader test

Invoke the `reader-test` skill. Spawn a genuinely fresh subagent with no context
beyond the file itself, ask it the reader questions, and score what comes back
against the key from step 1.

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
