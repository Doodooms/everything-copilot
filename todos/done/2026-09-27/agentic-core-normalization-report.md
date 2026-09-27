# Agentic Core normalization and Codex installation

**Outcome:** implementation released locally; overall task remains partial pending independent QA and Reviewer.
**Source task:** `task_5`, `SPEC-AGENTIC-CORE-NORMALIZATION@2`, plan r10.

## Completed in this task slice

- Preserved the 11 top-level domain skills and 59 complete nested workflow subskills; validated domain routes and source dispositions.
- Integrated the generic and Rust MCP authoring workflows, typed exchange/state validation, multi-harness guidance, same-harness session workflow, and Codex agent projection changes.
- Reinstalled the local plugin at 0.3.3 and verified the nine projected Codex agent files and a fresh orchestration skill load.
- Added repository tracking rules for Python/tool caches, the local Copilot snapshot, the installed Waza binary/manifest, and raw SkillOpt runs, while leaving curated evaluation evidence and `outputs/evals/baseline-inventory-r7.json` trackable.
- Recorded Git/GitHub handoff conventions in the repository documentation and PR template.

## Validation

Automated validation reported for task 5: 25 targeted source tests, Ruff, manifest validation, all 54 pre-checkpoint task transitions, and `git diff --check` passed. This checkpoint reran the source tests (25 passed), Ruff check and format, the manifest-record validator, and the exchange event/transition validators. Three new `TASK-5-08` transitions were appended through the validator, which re-read and validated the existing task history. `git diff --check` passed.

The separate legacy `validate_sdd_state.py` also reported stale revision-1 evidence and fields that do not match its stricter embedded-state contract. Historical evidence was left at its original revision; no pass was claimed from that validator.

QA and Reviewer did not run. This host has no custom-role dispatch mechanism. The task remains partial; see [the review-gate backlog](../../backlog/2026-09-27/agentic-core-normalization-review-gates.md).

## Excluded from this release

`task_3` remains owned by another active session. Its harness factory, harness evaluation/routing experiments, task history, baseline inventory, related tests, and overlapping README changes were preserved outside these commits. User-local mixed VS Code settings and unclassified ideas/artifacts were also preserved.
