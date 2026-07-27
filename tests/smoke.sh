#!/bin/sh
# Smoke test for the two scripts the skills shell out to.
#
# These are ~460 lines of real code with no unit tests. This does not test their
# correctness in detail — it proves they run end to end on a realistic document
# and produce the artifacts the skills expect, so a refactor cannot break the
# pipeline silently.
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$ROOT/plugins/message-test/scripts"
FIXTURE="$ROOT/tests/fixture.md"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

fail() { echo "smoke: FAIL — $1" >&2; exit 1; }

# ── extract.py: markdown in, prose out ────────────────────────────────────────
python3 "$SCRIPTS/extract.py" "$FIXTURE" > "$WORK/extracted.txt" 2>"$WORK/extract.err" \
  || fail "extract.py exited non-zero: $(cat "$WORK/extract.err")"

[ -s "$WORK/extracted.txt" ] || fail "extract.py produced no output"

grep -q "reducing the time it takes" "$WORK/extracted.txt" \
  || fail "extract.py dropped body prose"

# Paragraph boundaries are the contract cloze.py depends on to tell prose from
# slide furniture, so blank lines must survive extraction.
grep -q "^$" "$WORK/extracted.txt" \
  || fail "extract.py collapsed paragraph boundaries"

echo "smoke: extract.py OK ($(wc -w < "$WORK/extracted.txt") words)"

# ── cloze.py build: prose in, sheet + key out ─────────────────────────────────
python3 "$SCRIPTS/cloze.py" build "$WORK/extracted.txt" \
  --out "$WORK/sheet.txt" --key "$WORK/key.txt" >"$WORK/build.log" 2>&1 \
  || fail "cloze.py build exited non-zero: $(cat "$WORK/build.log")"

[ -s "$WORK/sheet.txt" ] || fail "cloze.py produced no sheet"
[ -s "$WORK/key.txt" ]   || fail "cloze.py produced no answer key"

grep -q "_____" "$WORK/sheet.txt" || fail "sheet contains no blanks"

# cloze.py is responsible for stripping non-prose. None of this may reach a
# human reader's test sheet — a blank inside a code fence is unanswerable.
if grep -q "this text must not appear" "$WORK/sheet.txt"; then
  fail "cloze.py leaked fenced code into the test sheet"
fi
if grep -q "title: Fixture document" "$WORK/sheet.txt"; then
  fail "cloze.py leaked YAML frontmatter into the test sheet"
fi
if grep -q "Quarterly platform review" "$WORK/sheet.txt"; then
  fail "cloze.py leaked a markdown heading into the test sheet"
fi

# Count numbered blanks in the passage — `[7]________`. The sheet also carries a
# ruled answer line per blank at the foot, so a bare underscore-run count doubles.
blanks=$(grep -oE '\[[0-9]+\]_+' "$WORK/sheet.txt" | wc -l)
answers=$(grep -cE '^[[:space:]]*[0-9]+[.)]' "$WORK/key.txt" || true)

[ "$blanks" -gt 10 ] || fail "sheet has only $blanks blanks — expected a real passage"
[ "$answers" -gt 10 ] || fail "key has only $answers answers — expected one per blank"
[ "$blanks" -eq "$answers" ] \
  || fail "sheet has $blanks blanks but key has $answers answers — they must agree"

echo "smoke: cloze.py build OK ($blanks blanks, $answers keyed answers, matched)"

# ── cloze.py must reject a missing file rather than pass silently ─────────────
if python3 "$SCRIPTS/cloze.py" build "$WORK/does-not-exist.txt" \
     --out "$WORK/x.txt" --key "$WORK/y.txt" >/dev/null 2>&1; then
  fail "cloze.py accepted a nonexistent input file"
fi
echo "smoke: cloze.py rejects missing input OK"

echo "smoke: all checks passed"
