---
name: verification-loop
description: "Comprehensive verification system before creating a PR or merging. Runs build, type check, lint, tests, security scan, and diff review in sequence. Returns a VERIFICATION REPORT with READY/NOT READY verdict. Use after completing a feature or significant code change. Derived from Everything Claude Code (https://github.com/affaan-m/everything-claude-code)."
user-invocable: false
---

# Verification Loop Skill

A comprehensive verification system to run before creating a PR or merging code.
Runs all quality gates in sequence and produces a verification report.

## When to Use

- After completing a feature or significant code change
- Before creating a PR
- When you want to ensure all quality gates pass
- After refactoring

## Verification Phases

### Phase 1 -- Build Verification

Check if the project builds without errors:

```bash
# Node.js / TypeScript
npm run build
pnpm build

# Python
python -m py_compile src/**/*.py
# or: mypy src/

# Go
go build ./...

# Rust
cargo build
```

If build fails, STOP and fix before continuing.

### Phase 2 -- Type Check

```bash
# TypeScript
npx tsc --noEmit

# Python
pyright .
mypy src/

# Rust (included in cargo build)
cargo check
```

Report all type errors. Fix critical ones before continuing.

### Phase 3 -- Lint Check

```bash
# TypeScript / JavaScript
npm run lint
npx eslint src/

# Python
ruff check .
flake8 src/

# Go
go vet ./...

# Rust
cargo clippy
```

### Phase 4 -- Test Suite

Run tests with coverage:

```bash
# Node.js
npm test -- --coverage

# Python
pytest --cov=src/ --cov-report=term-missing

# Go
go test ./... -cover

# Rust
cargo test
```

Report:
- Total tests: X
- Passed: X
- Failed: X
- Coverage: X% (target: 80%+)

### Phase 5 -- Security Scan

Quick scan for obvious secrets and debug artifacts:

```bash
# Search for hardcoded secrets
grep -rn "sk-" --include="*.py" --include="*.ts" --include="*.js" . | head -10
grep -rn "password\s*=" --include="*.py" --include="*.ts" . | head -10
grep -rn "api_key\s*=" --include="*.py" --include="*.ts" . | head -10

# Search for debug logging left in code
grep -rn "console.log\|print(\|pdb.set_trace\|debugger" src/ | head -10
```

For a full security review, invoke the security-review skill.

### Phase 6 -- Diff Review

Review what changed:

```bash
git diff --stat
git diff HEAD~1 --name-only
```

Review each changed file for:
- Unintended changes
- Missing error handling
- Potential edge cases
- Files that should not have changed

## Output Format

After running all phases, produce this report:

```
VERIFICATION REPORT
===================

Build:    [PASS/FAIL]
Types:    [PASS/FAIL] (X errors)
Lint:     [PASS/FAIL] (X warnings)
Tests:    [PASS/FAIL] (X/Y passed, Z% coverage)
Security: [PASS/FAIL] (X issues)
Diff:     [X files changed]

Overall:  [READY/NOT READY] for PR

Issues to Fix:
1. [Phase]: [description]
2. ...
```

<gates>

## Decision Rules

- **READY**: All phases PASS, coverage >= 80%, no security issues
- **NOT READY**: Any of: build fails, type errors, test failures, coverage < 80%,
  CRITICAL security issue
- **WARN**: Lint warnings or MEDIUM security issues (document but can proceed)

</gates>

## Continuous Mode

For long sessions, run verification periodically:

- After completing each function or component
- Before moving to the next task
- After any refactoring

## Integration with Other Skills

- **tdd-workflow**: verification-loop is the final step after RED-GREEN-REFACTOR
- **security-review**: invoke for a full OWASP check in Phase 5
- **gitnexus detect_changes**: run before Phase 6 for impact analysis

## Common Issues by Language

### Python
- Missing `__init__.py` causing import failures
- `pytest` not finding tests (check `testpaths` in `pyproject.toml`)
- Type errors in third-party stubs (`pip install types-requests`)

### TypeScript
- `tsconfig.json` `paths` aliases not resolving in Jest
- `moduleResolution` mismatch between tsconfig and bundler
- Missing `@types/*` packages

### Go
- Circular imports between packages
- Missing error checks (`if err != nil`)
- Race conditions in tests (run `go test -race ./...`)