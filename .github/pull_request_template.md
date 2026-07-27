## Summary
<!-- What does this PR do and why? -->

## Changes
-

## Test plan
- [ ] `python3 scripts/validate-plugin.py` passes
- [ ] `python3 scripts/check-links.py` passes
- [ ] `sh tests/smoke.sh` passes
- [ ] `claude plugin validate ./plugins/message-test --strict` passes
- [ ] Installed from this working copy and the changed skill exercised on a real document

## Method checks (content changes only)
- [ ] Nothing lets a language model take the cloze test
- [ ] The answer key still cannot be sourced from the document under test
- [ ] The report still states what was and was not measured
- [ ] Any new or edited `argument-hint` is quoted

## Related issues
<!-- Closes #NNN -->
