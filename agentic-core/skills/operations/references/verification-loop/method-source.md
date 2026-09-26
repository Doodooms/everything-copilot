---
name: verification-loop
description: "WHAT: Run the final verification loop after an executable change is complete. USE FOR: validating build, types, lint, tests, coverage, security, and diff readiness before a PR or merge. DO NOT USE FOR: implementing behavior, writing the first failing test, or driving RED-GREEN-REFACTOR."
user-invocable: false
compatibility: vscode 1.119.0+, github-copilot 1.119.0+
metadata:
    creation-date: 2026-09-22
    creator: Doodooms
license: MIT
---

<definitions>

- **completed change**: An executable feature, bug fix, refactor, configuration change, or test change whose implementation is already present and whose focused behavior has been checked.
- **quality gate**: A repository-appropriate build, type-check, lint, test, coverage, security, or diff check that supplies evidence about release readiness.
- **verification evidence**: The command, exit status, report, or inspected diff supporting a gate result; an assumed or skipped command is not evidence.
- **blocking failure**: A failed build, type-check, focused test, required gate, critical security finding, or missing evidence that prevents a READY verdict.
- **verification report**: The final structured summary of each applicable gate, its evidence, issues, and the overall `READY` or `NOT READY` verdict.
- **scope boundary**: The changed files and repository commands relevant to this verification; it does not authorize feature implementation or unrelated cleanup.

</definitions>

<admission>

Classify the request into exactly one outcome: `ACCEPT` or `REJECT`.

## ACCEPT

- An executable change is already implemented or the request explicitly asks to assess an existing completed change.
- The requested deliverable is evidence of repository readiness, a final quality report, or a PR/merge gate decision.
- The repository and changed surface provide enough information to identify applicable verification commands.

## REJECT

- The request asks to add a feature, fix a bug, refactor behavior, or write the first test -> `tdd` or the relevant implementation route.
- The request asks only for architecture, planning, documentation, prompt, agent, or skill authoring -> the relevant specialist route.
- The request requires changing code to make a gate pass -> route to the implementation or debugging specialist, then return here for verification.
- No completed change or verification target can be identified -> request clarification or route to the relevant specialist.

Testing, coverage, or failure vocabulary alone is not sufficient for admission. The deciding signal is whether the implementation phase is complete and the requested work is evidence-only verification.

</admission>

<routing>

Apply these checks in order:

1. Confirm that the requested implementation is already complete and that the focused behavior is not being designed or changed now.
2. Identify the changed repository surface and the quality gates that apply to it.
3. Confirm that the requested output is a verification report or readiness decision rather than a code change.
4. Choose `ACCEPT` when this workflow owns final evidence collection; otherwise choose `REJECT` and route to the closest specialist.

For `REJECT`, do **not** load the workflow. Return exactly:

```json
{"status":"rejected","skill":"verification-loop","reason":"<concise mismatch reason>","routing":"<suggested route or null>"}
```

For `ACCEPT`, read `references/__routing_probe__.md` as the first routing action, then continue to Phase 0. The probe is a routing boundary marker only; it is not a project verification result.

</routing>

<rules>

- Inspect the repository's own commands and changed surface before selecting gates.
- Run applicable gates in dependency order and preserve their actual results.
- Stop or report `NOT READY` when a blocking failure or missing required evidence occurs; do not repair product code in this workflow.
- Treat warnings according to repository policy and distinguish them from blocking failures.
- Never claim coverage, security, or readiness from an unrun command or an assumed result.
- Keep verification scoped to the completed change and its relevant dependencies.

</rules>

<workflow>

Read `references/__routing_probe__.md` as the first routing action.

## Phase 0 - Establish scope and commands

1. Inspect the repository status, changed files, project configuration, and documented validation commands with `#tool:read`.
2. Review [the verification command guide](./references/verification-commands.md) while selecting gates, then identify which gates apply to the changed surface. Do not invent a passing result for a gate that cannot be run.
    - Use `#tool:execute` on [the diff status helper](./scripts/collect_diff_status.sh) when a concise changed-file and diff summary is needed.

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

Use [the verification report template](./assets/verification-report.md), preserving unknown or skipped results explicitly.

`READY` requires all applicable gates to pass, no critical security issue, and no missing required evidence. Otherwise report `NOT READY`.

</workflow>

Source provenance: [original specification](./references/original-spec.md) when present.