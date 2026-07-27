# message-test

Three ways to find out whether a document actually delivers its message, and one clear
statement of what each of them can and cannot prove.

A readability score tells you how hard a text is to process. It does not tell you whether
the reader took away what you meant. Those are different questions, and only the second one
matters when a document has to carry a decision.

## Website

- [English](https://cocodedk.github.io/message-test/)
- [فارسی (Persian)](https://cocodedk.github.io/message-test/fa/)

---

## Installation

In a Claude Code session:

```
/plugin marketplace add cocodedk/message-test
/plugin install message-test@message-test
```

Restart or `/reload-plugins` and the command is available.

**If either step errors, you almost certainly already have it.** A marketplace name can only
be registered once, so adding it a second time — or adding it when you already have this repo
registered from a local directory — is rejected rather than merged. Update instead of adding:

```
/plugin marketplace update message-test
/plugin update message-test@message-test
```

Note the `plugin@marketplace` form on the update — the bare name is rejected with
"Plugin not found".

The command-line equivalents are more forgiving: they report "already installed" and exit
cleanly rather than failing, so prefer them if you are scripting or unsure of current state.

```bash
claude plugin marketplace add cocodedk/message-test
claude plugin install message-test@message-test

# already have it?
claude plugin marketplace update message-test
claude plugin update message-test@message-test
```

The CLI clones over **SSH** (`git@github.com:…`), so it needs a working GitHub SSH key. If
the clone fails with a permission error, that is why.

> **Updating an existing install needs a version bump.** The cached copy is keyed by version,
> so editing plugin files without raising `version` in `plugin.json` leaves every existing
> install on the old code. That is not a hypothetical: the frontmatter fix in 1.0.1 did not
> reach this machine's cache until the version moved.

<details>
<summary>From a local clone (for development)</summary>

```bash
git clone https://github.com/cocodedk/message-test.git
claude plugin marketplace add ./message-test
claude plugin install message-test@message-test
```

The marketplace path must be given as a path — `./message-test`, not `message-test`, or it
is read as a GitHub `owner/repo`. Run `claude plugin marketplace update message-test` after
editing plugin files.
</details>

**Requires** Claude Code v2.1.x or newer. PDF extraction needs `pdftotext` (poppler-utils);
everything else is Python standard library.

---

## Usage

```
/message-test:run <file> "<who the reader is>" "<source document it came from>"
```

Quote the multi-word arguments — positional arguments split on whitespace.

```
/message-test:run deliverables/some-deck.pptx "a board member with 11 minutes" \
    "governance/the-source-document.md"
```

A PPTX, DOCX, ODP or ODT is rendered to PDF first, so the reader sees the layout rather than
a pile of extracted words.

## What it gives you

| Skill | What it measures | Who runs it | Cost |
|---|---|---|---|
| `clarity-index` | Whether the known blockers are absent: no main message, no stated action, unusable numbers, risk without likelihood. Scored out of 100, 90 passes. | A model, in minutes | Free |
| `reader-test` | Whether a fresh reader extracts the intended message, and what they believe that the document never said. | A model, isolated from your context | Nearly free |
| `cloze-test` | Whether real readers can follow the text. Every sixth word removed and restored; 60 percent or more passes. | Humans only | Real people's time |

`/message-test:run` runs the first two in order and tells you whether the third is worth it.

## The three rules that matter most

**The reader must really be fresh, and a subagent often is not.** A subagent inherits the
project's `CLAUDE.md` and memory files. If those explain the subject, the reader answers from
them and passes a document that carries no message of its own.

**The answer key must not come from the document under test.** A key skimmed off the artifact
measures whether the artifact repeats its own headlines. It always does.

**A model must never take the cloze test.** A model restores a missing word from context far
better than any person, so it scores well on text no human can follow. Use it to build the
sheet and score the returns, never to answer one.

That last rule is the most trustworthy thing here: the instrument states the case in which
its own output is worthless.

## Where the methods come from

- **ISO 24495-1:2023**, the plain language standard, defines the target as a reader outcome
  and explicitly rejects readability formulas as the test of success.
  <https://www.iso.org/standard/78907.html>
- **CDC Clear Communication Index**: twenty scored items, out of 100, 90 to pass, about
  fifteen minutes. `clarity-index` adapts its seven published areas for general documents.
  For a score that has to stand up formally, use the CDC score sheet itself.
  <https://www.cdc.gov/ccindex/pdf/full-index-score-sheet.pdf>
- **Cloze procedure**, Taylor 1953, still the basis on which several readability formulas
  were calibrated. Threshold and method as described by Nielsen Norman Group.
  <https://www.nngroup.com/articles/cloze-test-reading-comprehension/>

## What none of this proves

That the message is right, that the audience will agree, or that a specific person will act.
It catches the document that says something different from what you meant, which is the
failure that goes unnoticed for longest.

## Repository layout

```
message-test/
├── .claude-plugin/marketplace.json
├── plugins/message-test/
│   ├── .claude-plugin/plugin.json
│   ├── commands/run.md
│   ├── skills/{clarity-index,reader-test,cloze-test}/SKILL.md
│   └── scripts/{extract.py,cloze.py}
├── tests/{smoke.sh,fixture.md}
├── scripts/{validate-plugin.py,check-links.py,install-hooks.sh,setup-repo.sh}
└── website/            # bilingual EN + FA
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Run `./scripts/install-hooks.sh` after cloning — the
hooks are what stop a malformed frontmatter block reaching main.

## Author

**Babak Bandpey** — [cocode.dk](https://cocode.dk) | [LinkedIn](https://linkedin.com/in/babakbandpey) | [GitHub](https://github.com/cocodedk)

## License

Apache-2.0 | © 2026 [Cocode](https://cocode.dk) | Created by [Babak Bandpey](https://linkedin.com/in/babakbandpey)
