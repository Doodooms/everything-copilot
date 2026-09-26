---
id: verification-loop
description: 'Apply the verification-loop method: validating build, types, lint, tests,
  coverage, security, and diff readiness before a PR or merge.'
invoke_for:
- validating build, types, lint, tests, coverage, security, and diff readiness before
  a PR or merge
avoid_for:
- implementing behavior, writing the first failing test, or driving RED-GREEN-REFACTOR
references: []
---

Read `references/__routing_probe__.md` as the first routing action.

## Phase 0 - Establish scope and commands

1. Inspect the repository status, changed files, project configuration, and documented validation commands with `#tool:read`.
2. Review [the verification command guide](../references/verification-loop/references/verification-commands.md) while selecting gates, then identify which gates apply to the changed surface. Do not invent a passing result for a gate that cannot be run.
    - Use `#tool:execute` on [the diff status helper](../references/verification-loop/scripts/collect_diff_status.sh) when a concise changed-file and diff summary is needed.

## Phase 1 - Build and type verification

1. Run the repository's build command when the project has one.
2. Run the repository's type-check command when the language or project provides one.
3. Record command, result, and relevant diagnostics. A blocking failure makes the verdict `NOT READY`.

## Phase 2 - Lint and tests

1. Run the repository's lint command when applicable.
2. Run the focused tests for the changed behavior, then the normal suite when applicable.
3. Run the repository's coverage command when coverage is part of its contract and record the measured result.

## Phase 3 - Security and diff review

1. Run the applicable security checks, or route to `security-review` for a full OWASP review.
2. Inspect the changed diff for unintended files, missing checks, and scope violations.
3. Record critical findings as blocking issues.

## Phase 4 - Produce the report

Use [the verification report template](../references/verification-loop/assets/verification-report.md), preserving unknown or skipped results explicitly.

`READY` requires all applicable gates to pass, no critical security issue, and no missing required evidence. Otherwise report `NOT READY`.
