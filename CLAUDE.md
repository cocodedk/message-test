# CLAUDE.md — message-test

Claude Code plugin that measures whether a document delivers its message: a scored clarity
index, a fresh-reader extraction test, and a human cloze test.

- **Language / Runtime**: Python 3.12, standard library only
- **External binary**: `pdftotext` (poppler-utils), for PDF input only, guarded by
  `shutil.which`

## Repository shape

Marketplace at repo root; plugin nested under `plugins/message-test/`. Inside the plugin,
`.claude-plugin/` contains **only** `plugin.json` — commands, skills, and scripts sit at the
plugin root.

```
.claude-plugin/marketplace.json      # marketplace: message-test
plugins/message-test/
  .claude-plugin/plugin.json         # plugin: message-test
  commands/run.md
  skills/{clarity-index,reader-test,cloze-test}/SKILL.md
  scripts/{extract.py,cloze.py}
tests/{smoke.sh,fixture.md}
scripts/{validate-plugin.py,check-links.py,install-hooks.sh,setup-repo.sh}
```

## Working on this repo

**Validate after every manifest or frontmatter change:**

```bash
python3 scripts/validate-plugin.py
sh tests/smoke.sh
claude plugin validate ./plugins/message-test --strict
claude plugin validate . --strict
```

**Reload after editing plugin files** — the installed copy is cached:

```bash
claude plugin marketplace update message-test
```

**Quote every `argument-hint`.** Unquoted `[a] [b]` is invalid YAML (two juxtaposed flow
sequences), and the runtime **silently drops the entire frontmatter block** rather than
erroring — the command then loads with no description at all. This repo shipped in that state
for four commits. `--strict` and the validator both catch it now, and both run in the
pre-commit hook.

**Positional arguments split on whitespace.** `$1`/`$2`/`$3` bind correctly only when the
caller quotes multi-word values. `run.md` carries a guard telling the model to treat a
fragment-looking `$2`/`$3` as absent rather than proceeding on it.

## Rules the content must keep

These are correctness constraints on the method, not preferences.

1. **A model must never take the cloze test.** A model restores missing words from context far
   better than a person, so it scores well on text no human can follow. Build the sheet and
   score the returns; never answer one.
2. **The answer key never comes from the document under test.** It must come from the source
   document or the author, or the report must say the run tested internal consistency only.
3. **The reader must be genuinely fresh.** A subagent inherits `CLAUDE.md` and memory files;
   if those describe the subject, the reader passes a document that carries no message.
4. **Always state what was not measured.** A passing index means known blockers are absent. A
   passing reader test means one competent uninformed reader extracted the message. Neither
   proves the real audience will understand or agree.

## Scripts

`extract.py` pulls prose from `.pptx/.docx/.odp/.odt/.pdf/.md/.txt/.html`, preserving
paragraph boundaries — `cloze.py` depends on those boundaries to tell prose from slide
furniture. `cloze.py build` strips frontmatter, code fences, headings and list items, selects
a passage, and blanks every 6th word; `cloze.py score` grades returned answers.

Both are invoked **by path** from the skills. `validate-plugin.py` checks that every
`${CLAUDE_PLUGIN_ROOT}/...` path referenced in a skill still exists, because a rename would
otherwise break the pipeline at runtime with nothing reporting it.

Keep them standard-library only. The plugin has no install step and a pip dependency would
introduce one.

## Known deviations

- `cloze.py` is 312 lines, over the 200-line file limit this house convention normally
  applies. It is working, tested code with a single coherent responsibility; it is recorded
  here rather than split, and should be split if it grows further.

## Author

Babak Bandpey · bb@cocode.dk · https://cocode.dk
