#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd -P)"
cd "$repo_root"

required_files=(
  README.md
  AGENTS.md
  manifest.json
  popup/popup.html
  popup/popup.css
  tests/test_mv3_shell.py
  docs/PROJECT_BRIEF.md
  docs/ARCHITECTURE.md
  .gitignore
  .github/workflows/baseline.yml
)

for path in "${required_files[@]}"; do
  [[ -s "$path" ]] || { printf 'missing or empty required file: %s\n' "$path" >&2; exit 1; }
done

bash -n scripts/baseline.sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'
git diff --check HEAD --

if git grep -nE '[[:blank:]]+$' -- .; then
  printf 'tracked files contain trailing whitespace\n' >&2
  exit 1
fi

if git grep -nI -E '(AKIA[0-9A-Z]{16}|github_pat_|gh[pousr]_[A-Za-z0-9_]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|WB(_API)?_TOKEN[[:space:]]*=)' -- . ':!scripts/baseline.sh'; then
  printf 'possible credential material detected\n' >&2
  exit 1
fi

grep -Fq 'name: baseline' .github/workflows/baseline.yml
grep -Fq 'baseline:' .github/workflows/baseline.yml
grep -Fq 'run: ./scripts/baseline.sh' .github/workflows/baseline.yml

printf 'baseline: ok\n'
