# Plan r2 addendum — explicit catalog propagation

Status: approved by Orchestrator from Planner follow-up
Parent plan: [plan r1](plan-r1.md)
Risk level: L2 (unchanged)
Specification: SPEC-6 revision 1 (unchanged)

## TASK-6-07 — Propagate explicit agent catalogs through Harness Factory entry points

**Owner:** Implementer

**Trace:** REQ-6-2, REQ-6-7; AC-6-2, AC-6-7.

**Dependency:** TASK-6-02 is complete. Reuse its `known_agents` input contract; do not reopen or rewrite TASK-6-02 history.

**Scope:** Thread caller-supplied agent IDs through CLI validation and execution preparation, and through `HarnessAdapter.prepare`/`materialize`. Keep omitted catalogs empty and fail closed. Do not restore implicit Agentic Core discovery or add a new abstraction.

**Exit criteria:**

- CLI `validate` and `suite-run` accept and forward a repeated explicit catalog input.
- `HarnessAdapter.prepare` can receive and forward the explicit catalog to materialization.
- Other CLI paths that call adapter preparation expose and forward the same explicit input.
- Behavior tests show the explicit catalog works through CLI validation, suite-run preflight, and adapter preparation; omission remains fail-closed.
- Pack v1 remains unchanged.

**Validation:** Focused Harness Factory and Pack v1 tests, scoped Ruff check/format, and `git diff --check`. Independent QA retest and final review are required for AC-6-2/AC-6-7.

The reviewer finding is recorded in `return-task-6-06-review-a1.json`. Plan r1 and all terminal TASK-6-02 evidence remain immutable.

## TASK-6-08 — Independent QA retest

**Owner:** Quality Assurance

**Trace:** REQ-6-2, REQ-6-7; AC-6-2, AC-6-7.

**Dependency:** TASK-6-07 implementation is complete.

**Exit criteria:** Independently exercise the CLI validation, suite-run preflight, and adapter preparation paths with an explicit catalog and omitted-catalog fail-closed behavior; confirm Pack v1 regression tests still pass. Record exact commands, subject patch digest, PASS/FAIL/BLOCKED per criterion, and external limitations without changing code.

## TASK-6-09 — Final Reviewer retest

**Owner:** Reviewer

**Trace:** REQ-6-2, REQ-6-7; AC-6-2, AC-6-7.

**Dependency:** TASK-6-08 has current QA evidence.

**Exit criteria:** Review the final implementation and current QA evidence, resolve REVIEW-6-01, and return approve/reject with concrete findings. Do not repeat the QA campaign.
