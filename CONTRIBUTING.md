# Contributing to message-test

## Local Setup

```bash
git clone https://github.com/cocodedk/message-test.git
cd message-test
pip install pyyaml
./scripts/install-hooks.sh
```

`core.hooksPath` is per-checkout config and is not committed, so **every fresh clone must run
`./scripts/install-hooks.sh`** or no hooks are active.

Optional, for PDF input: `sudo apt install poppler-utils` (provides `pdftotext`).

## Local Git Setup

```bash
git config pull.rebase true
git config core.autocrlf input        # 'true' on Windows
git config push.autoSetupRemote true
```

## Testing your changes

```bash
python3 scripts/validate-plugin.py    # manifests, frontmatter, script wiring
python3 scripts/check-links.py        # relative markdown links
sh tests/smoke.sh                     # extract.py + cloze.py end to end
claude plugin validate ./plugins/message-test --strict
claude plugin validate . --strict
```

Then install from your working copy and exercise it:

```bash
claude plugin marketplace add ./message-test
claude plugin install message-test@message-test
claude plugin marketplace update message-test   # after every edit
```

## Frontmatter: quote your argument-hint

This repo shipped with a live bug worth knowing about, because it is easy to reintroduce and
the runtime will not tell you:

```yaml
argument-hint: [file] [who the reader is] [source document]   # BROKEN
```

Unquoted `[a] [b]` is two juxtaposed YAML flow sequences. That is invalid YAML, and Claude
Code responds by **silently discarding the entire frontmatter block** — so the command loads
with no description and no hint, and nothing anywhere reports an error. Quote it:

```yaml
argument-hint: "[file] [\"who the reader is\"] [\"source document\"]"
```

`claude plugin validate --strict` and `scripts/validate-plugin.py` both catch this now, and
both run in CI and in the pre-commit hook.

## Rules the content must keep

1. **A model must never take the cloze test.** It restores missing words from context far
   better than a person, so it scores well on text no human can follow. The skill may build
   the sheet and score returns; it may never answer one. Any change that weakens this is
   wrong however convenient it is.
2. **The answer key never comes from the document under test.** A key skimmed off the
   artifact measures whether the artifact repeats its own headlines, which it always does.
3. **The reader must be genuinely fresh.** A subagent inherits project instructions and
   memory; if those describe the subject, the reader passes a document that carries no
   message of its own.
4. **State what was not measured.** Every report says plainly which of the three ran and what
   a pass does and does not prove.

## Changing the scripts

`extract.py` and `cloze.py` are invoked by path from the skills. `scripts/validate-plugin.py`
checks that every `${CLAUDE_PLUGIN_ROOT}/...` path referenced in a skill still exists — a
rename would otherwise break the pipeline at runtime with no warning.

Both are pure standard library. Keep them that way; the plugin has no install step, and a pip
dependency would introduce one. The only external requirement is the `pdftotext` binary, and
it is already guarded with `shutil.which` and a clean error message.

Add a case to `tests/smoke.sh` for any behaviour you would be upset to lose.

## Commits and branches

Conventional Commits, enforced by the `commit-msg` hook:

```
feat: score near-misses separately in cloze output
fix: keep paragraph boundaries when extracting ODT
docs: explain why a model must not take the cloze test
```

Types: `feat|fix|chore|docs|style|refactor|test|ci|build|perf|revert`

Branch names are kebab-case with a prefix matching the commit type. Never commit directly to
`main` — open a PR.

## Releasing

The release workflow does **not** bump the version. Bump it by PR first, in both
`plugins/message-test/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` — the
workflow fails if they disagree — then run the `Release` workflow manually. It tags
`message-test--v<version>` and creates the GitHub Release.

## PR Checklist

- [ ] `python3 scripts/validate-plugin.py` passes
- [ ] `python3 scripts/check-links.py` passes
- [ ] `sh tests/smoke.sh` passes
- [ ] `claude plugin validate ./plugins/message-test --strict` passes
- [ ] Installed from the working copy and the changed skill exercised on a real document
- [ ] Any new `argument-hint` is quoted
