#!/bin/sh
set -eu
cd "$(git rev-parse --show-toplevel)"
git config core.hooksPath .githooks
chmod +x .githooks/* scripts/*.py 2>/dev/null || true
echo "Hooks installed — pre-commit (validator), commit-msg (Conventional Commits),"
echo "and pre-push (owner-lock + protected-branch guard + full verification) are active."
echo
python3 -c "import yaml" 2>/dev/null || echo "NOTE: the hooks need PyYAML — run: pip install pyyaml"
