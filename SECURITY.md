# Security Policy

## Reporting a Vulnerability

Do **not** open a public GitHub issue for security vulnerabilities.

To report a vulnerability:

- Use the **"Report a vulnerability"** button on the Security tab of this repository
  (GitHub private advisory)
- Or email: bb@cocode.dk

We will acknowledge within 5 business days and aim to release a fix within 30 days of
confirmation.

## Scope notes for this plugin

This plugin processes documents you point it at, and those documents are frequently written
by someone else. Three things are worth knowing.

**Documents under test are untrusted input.** A deck, report, or source document may contain
text crafted to look like instructions. The skills treat supplied documents as evidence to
measure, never as commands to follow. If you find a phrasing that defeats that, it is a valid
report under this policy.

**`extract.py` shells out to an external binary.** PDF extraction invokes `pdftotext` from
poppler-utils via `subprocess`. The call is guarded with `shutil.which` and the input path is
passed as an argument rather than through a shell, but you are running a third-party parser
over an untrusted file. Keep poppler-utils patched. Office and OpenDocument formats are
handled in-process with `zipfile` and the standard library, with no external binary.

**The reader test may run a subagent.** That subagent inherits the environment it is launched
in. This is documented as a *measurement* hazard — a reader that inherits your project's
instructions is not a fresh reader — but it is also the reason not to run it against
documents you would not want a model session to see.

Neither script writes outside paths you supply, and neither makes network requests.

## Supported Versions

| Version | Supported |
|---------|-----------|
| latest  | ✅ |
| older   | ❌ |
