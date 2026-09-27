# Plan — Codex-first behavioral evaluation

## Identity and approval

- `task_id`: `task_3`
- `plan_revision`: 1
- `status`: approved
- `specification`: `SPEC-COST-EVAL-OPT@1`
- `architecture`: not required for this plan; use the existing `harness_factory` boundary and revisit only if implementation evidence shows it cannot satisfy the specification.
- Approval note: the Planner attempt `planner-cost-1` was interrupted by the Orchestrator after no structured result was returned. This bounded fallback plan is authored and approved by the Orchestrator under the parent instruction; no Planner output is claimed.
- Source: `todos/harness/cost-eval-opt.md` (the five referenced task documents remain unchanged).

## Scope and gates

Deliver only the `cost-eval-opt` phase. The two attached `in_progress` notes are unfinished context; the remaining agentic-core backlog is outside this plan. The GitHub authorization-boundary check is a separate external gap and is not a dependency for local evaluation implementation. Do not guess a denied repository name.

Use local deterministic validation before model calls. Codex is the default for costly evaluation. Any Copilot call must carry one explicit reason from `copilot_specific_behavior`, `portability_sample`, `regression_confirmation`, or `host_specific_agent_behavior`. Do not run a massive benchmark or optimization corpus in this phase.

All implementation tasks must first inspect and preserve the shared dirty worktree, including untracked `harness_factory/` sources and tests. Do not overwrite or attribute pre-existing changes without evidence. This plan does not authorize staging, committing, branch/worktree creation, or other lifecycle changes.

## Requirement and acceptance traceability

| Requirement | Acceptance criterion | Owning task(s) |
|---|---|---|
| `REQ-COST-1` | `AC-COST-1` | `TASK-COST-01`, `TASK-COST-04` |
| `REQ-COST-2` | `AC-COST-2` | `TASK-COST-02`, `TASK-COST-04` |
| `REQ-COST-3` | `AC-COST-3` | `TASK-COST-03`, `TASK-COST-04` |
| `REQ-COST-4` | `AC-COST-4` | `TASK-COST-02`, `TASK-COST-05`, `TASK-COST-06` |
| `REQ-COST-5` | `AC-COST-5` | `TASK-COST-03`, `TASK-COST-05`, `TASK-COST-06` |
| `REQ-COST-6` | `AC-COST-6` | `TASK-COST-03`, `TASK-COST-04` |
| `REQ-COST-7` | `AC-COST-7` | `TASK-COST-04`, `TASK-COST-06` |
| `REQ-COST-8` | `AC-COST-8` | `TASK-COST-02`, `TASK-COST-06` |

## Phase 1 — Suite schema and deterministic validator

### `TASK-COST-01` — Scenario and suite contract

- **Owner:** Implementer.
- **Objective:** Add a harness-neutral scenario/suite contract and local loader/validator for stable IDs, category, fixture/base revision, prompt, expected behavior, required/forbidden/optional observations, and metrics.
- **Bounded components:** existing `harness_factory` models and new suite/validation module(s); focused additions to `tests/test_harness_factory.py` and deterministic suite fixtures. Preserve current adapter and run APIs unless a required compatibility change is evidenced.
- **Dependencies:** none.
- **Acceptance mapping:** `AC-COST-1`.
- **Expected output:** versioned suite data and validation errors that can be checked without invoking either harness.
- **Validation:** focused deterministic tests for a valid scenario, missing/malformed fields, duplicate IDs, bad categories, and incompatible fixture revisions. Prove validation does not launch a harness.
- **Phase exit:** suite metadata is parseable, field constraints are explicit, and all local validator cases pass.

## Phase 2 — Runner, budgets, artifacts, and CLI

### `TASK-COST-02` — Cost policy, budget gates, and cross-harness rules

- **Owner:** Implementer.
- **Objective:** Enforce Codex-first target selection, the Copilot reason enum, explicit run/model-call/known-token/failure budgets, fail-fast conditions, and isolated read-only cross-harness validation with no recursive delegation or validation ownership transfer.
- **Bounded components:** `harness_factory` scenario/run models, adapters, run orchestration, CLI, and focused tests. Reconcile the pre-existing adapter implementation before editing.
- **Dependencies:** `TASK-COST-01`.
- **Acceptance mapping:** `AC-COST-2`, `AC-COST-4`, `AC-COST-8`.
- **Expected output:** a suite-only Codex invocation path; Copilot requests rejected before launch unless a valid reason is supplied; cost limits checked before launch and during result collection; read-only cross-harness request validation.
- **Validation:** deterministic adapter mocks for missing/invalid Copilot reasons, each budget edge, fail-fast errors, mismatched origin/target, attempted mutation, and recursive validation. Keep unknown token counts as unknown; enforce token caps only when usage is known.
- **Phase exit:** invalid or over-budget requests make no harness invocation; system failures stop subsequent calls; validator remains read-only and single-depth.

### `TASK-COST-03` — Durable run records and matched comparison

- **Owner:** Implementer.
- **Objective:** Persist one machine-readable artifact for every completed/failed run and compare candidate profiles over matched fixture, prompt, and expected behavior.
- **Bounded components:** `harness_factory` result/serialization/storage/comparison modules and CLI, plus focused artifact and comparison tests. Markdown is a projection only.
- **Dependencies:** `TASK-COST-02`.
- **Acceptance mapping:** `AC-COST-3`, `AC-COST-5`, `AC-COST-6`.
- **Expected output:** run artifact includes suite, harness, model, base revision, profile, results, metrics, failures, token usage, latency, and raw-artifact references; evaluator accepts a profile/plugin input without knowing how it was generated.
- **Validation:** JSON or other selected machine format round-trip; required-field checks for pass/fail/blocked runs; paired comparison rejects fixture/prompt/expected mismatches; unavailable metrics serialize as unknown, not zero.
- **Phase exit:** durable records can be reloaded and paired comparisons are deterministic over identical evidence.

## Phase 3 — Initial suites, bounded smoke, QA, review, and convergence

### `TASK-COST-04` — Conformance suite and baselines

- **Owner:** Implementer.
- **Objective:** Add initial cases for skill discovery, skill routing, workflow routing, agent routing, plugin loading, MCP exposure, risk-proportional routing, evidence reuse, and cross-harness materialization. Create a matched flat-versus-hierarchical baseline pair; add old-versus-risk-proportional routing only when historical artifacts exist.
- **Bounded components:** new evaluation suite/fixture and profile inputs; baseline result references under the task's evaluation-artifact directory. Do not alter canonical plugin/skill sources to create an evaluation candidate.
- **Dependencies:** `TASK-COST-03`.
- **Acceptance mapping:** `AC-COST-1`, `AC-COST-2`, `AC-COST-3`, `AC-COST-6`, `AC-COST-7`.
- **Expected output:** reusable suite cases and comparable profile inputs; a durable matched baseline pair or a documented, evidence-backed blocker if a valid pair cannot be materialized from available history.
- **Validation:** assert paired inputs are identical except for the candidate profile. Record unsupported metrics as unknown. Do not infer that unverified historical reports are current baselines.
- **Phase exit:** the suite is runnable Codex-only; available baselines are identified; missing historical old/new routing artifacts are explicitly reported.

### `TASK-COST-05` — Bounded smoke

- **Owner:** Implementer.
- **Objective:** Run only the minimum smoke/evaluation needed to prove suite loading, budget enforcement, artifact persistence, matched comparison, and Codex-first operation.
- **Bounded components:** only the frozen phase-3 fixtures and the new evaluation records; no unrelated benchmark corpus.
- **Dependencies:** `TASK-COST-04`.
- **Acceptance mapping:** `AC-COST-2`, `AC-COST-4`, `AC-COST-5`.
- **Expected output:** exact commands, budgets recorded before invocation, durable result IDs, and any observed failures. A Copilot run is allowed only when one of its four reasons is recorded and the sample is necessary for a Copilot-specific/portability criterion.
- **Validation:** static suite tests, focused runner tests, then a small Codex smoke with limits recorded before invocation. Stop on the first systemic materialization/plugin/schema/routing error. Do not repeat the large corpus on Copilot.
- **Phase exit:** the bounded smoke is complete or blocked with exact evidence; no unbounded run occurs.

### `TASK-COST-06` — Independent QA

- **Owner:** quality-assurance.
- **Objective:** Independently falsify scenario validation, policy gates, budget/fail-fast behavior, durable artifacts, matched comparisons, profile-agnostic evaluation, and cross-harness restrictions.
- **Dependencies:** `TASK-COST-05` and current implementation evidence from `TASK-COST-01` through `TASK-COST-04`.
- **Acceptance mapping:** all `AC-COST-1` through `AC-COST-8`.
- **Expected output:** QA run ID, reproduced or closed findings, commands/results, remaining gaps, and next owner; QA makes no production edits.
- **Validation:** test invalid and boundary inputs, attempted over-budget runs, systemic fail-fast, artifact round-trip, fixture mismatch, validator mutation attempts, and recursion denial. Keep all harness calls within the recorded smoke budget.
- **Phase exit:** QA passes or returns a grounded defect packet to Implementer; do not advance to Reviewer on partial evidence.

### `TASK-COST-07` — Reviewer gate

- **Owner:** Reviewer.
- **Objective:** Review the implementation against current specification and QA evidence.
- **Dependencies:** `TASK-COST-06` QA pass.
- **Acceptance mapping:** all `AC-COST-1` through `AC-COST-8`.
- **Expected output:** review verdict tied to current implementation and QA evidence, with findings routed to the evidenced owner.
- **Validation:** Reviewer loads static `security-review` analysis if the read-only harness invocation or authorization boundary changed.
- **Phase exit:** Reviewer approves current implementation and QA evidence, or returns a scoped finding; no convergence claim yet.

### `TASK-COST-08` — SDD convergence and final report

- **Owner:** Orchestrator using SDD convergence.
- **Objective:** Reconcile current specification, plan, implementation, QA, and review evidence; report remaining gaps and readiness claims.
- **Dependencies:** `TASK-COST-07` approval.
- **Acceptance mapping:** all `AC-COST-1` through `AC-COST-8`.
- **Expected output:** convergence verdict with criterion coverage, fresh evidence references, external gaps, and exact next owner/action if incomplete.
- **Validation:** convergence requires current evidence for every in-scope criterion, no stale required artifact, and no unresolved in-scope blocker. The separate GitHub repository-name gap remains external and is not silently marked complete.
- **Phase exit:** report success only on convergence; otherwise report partial with categorized gaps and an owner.

## Dependency DAG

```text
TASK-COST-01
  -> TASK-COST-02
  -> TASK-COST-03
  -> TASK-COST-04
  -> TASK-COST-05
  -> TASK-COST-06
  -> TASK-COST-07
  -> TASK-COST-08
```

Tasks are sequential because the suite contract gates runner inputs, the runner gates durable result/compare semantics, and the curated baseline/smoke depends on those interfaces. QA and Reviewer are independent acceptance roles, not implementation owners.

## Cost and execution limits

- Static checks and schema validation are local and deterministic.
- Codex is the target for costly benchmarks and the bounded smoke. Record explicit values for `max_runs`, `max_model_calls`, `max_tokens_if_known`, and `max_failures_before_stop` before model invocation; do not invent a token count when the harness does not report one.
- Copilot remains limited to the minimum required Copilot-specific or portability sample and must carry its allowed `reason` in both invocation and run artifact.
- No massive benchmark matrix, repeated corpus, SkillOpt/GEPA/custom optimizer, or self-improvement loop runs in this phase.

## Known context and risks

- `harness-adapters-phase1.md` documents adapter behavior and 24 deterministic tests, but the local `harness_factory/` and its test file are untracked; re-inspect the live files and preserve them before modification. The parent reports the 24-test baseline passes; record the exact command/run details in the implementation handoff before using it as validation evidence.
- The phase-1 report says a full `agentic-core` run on Codex was refused because the plugin declares MCP servers and Codex could not disable them per plugin. Use an isolated fixture or record this as a limitation; do not claim full plugin-on-Codex conformance.
- The GitHub authorization-boundary note remains blocked pending a known-existing denied repository name. It is an external predecessor gap, not a local evaluator dependency.
- Other unfinished `todos/in_progress` items remain unfinished and outside this phase.

## Handoff

Next: Implementer receives `TASK-COST-01` through `TASK-COST-05` as sequential scoped work after inspecting the shared dirty worktree; return changed files, validation, evidence, and commit SHAs only if the authorized lifecycle requires commits. Then run independent QA `TASK-COST-06`, Reviewer gate `TASK-COST-07`, and SDD convergence task `TASK-COST-08`.
