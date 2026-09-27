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
<critical_rules>
- MUST keep work within this subskill’s declared scope and its specific safety or authority constraints.
- MUST NOT replace the parent domain skill’s admission, global routing, or authority boundaries.
</critical_rules>

<general_rules>
- SHOULD load listed references only at the procedure step that needs them.
- MAY report unavailable evidence or unresolved decisions as unknown.
</general_rules>

<risk_assessment>
Consume the Orchestrator-assigned `risk_level` through the parent domain skill; MUST NOT reclassify or downgrade it. SHOULD escalate only when new evidence materially increases risk. Scale evidence depth, not authority or approvals.
</risk_assessment>

<rules>
- MUST follow this selected subskill only within its declared procedure and scope.
- MUST NOT replace the parent domain skill’s admission, global routing, or authority boundaries.
- MUST return the result, evidence, remaining unknowns, risks, and status required by this procedure.
</rules>

<workflow>
## Step 1 - Establish scope and commands

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Inspect the repository status, changed files, project configuration, and documented validation commands with `#tool:read`.
2. Review [the verification command guide](../references/verification-loop/references/verification-commands.md) while selecting gates, then identify which gates apply to the changed surface. Do not invent a passing result for a gate that cannot be run.
    - Use `#tool:execute` on [the diff status helper](../references/verification-loop/scripts/collect_diff_status.sh) when a concise changed-file and diff summary is needed.

## Step 2 - Build and type verification

1. Run the repository's build command when the project has one.
2. Run the repository's type-check command when the language or project provides one.
3. Record command, result, and relevant diagnostics. A blocking failure makes the verdict `NOT READY`.

## Step 3 - Lint and tests

1. Run the repository's lint command when applicable.
2. Run the focused tests for the changed behavior, then the normal suite when applicable.
3. Run the repository's coverage command when coverage is part of its contract and record the measured result.

## Step 4 - Security and diff review

1. Run the applicable security checks, or route to `security-review` for a full OWASP review.
2. Inspect the changed diff for unintended files, missing checks, and scope violations.
3. Record critical findings as blocking issues.

## Step 5 - Produce the report

1. Use [the verification report template](../references/verification-loop/assets/verification-report.md), preserving unknown or skipped results explicitly.
2. Report `READY` only when all applicable gates pass, no critical security issue remains, and no required evidence is missing; otherwise report `NOT READY`.
</workflow>
