# Plan — Codex-first behavioral evaluation

## Identity and approval

- `task_id`: `task_3`
- `plan_revision`: 4
- `status`: approved
- `specification`: `SPEC-COST-EVAL-OPT@1`
- `architecture`: not required for this plan; use the existing `harness_factory` boundary and revisit only if implementation evidence shows it cannot satisfy the specification.
- Approval note: this revision preserves `SPEC-COST-EVAL-OPT@1`, task IDs, dependency DAG, and acceptance mappings. It refines r3's smoke source after the parent identified that the current dirty `agentic-core/mcp.json` is user-owned and adds an unapproved GitHub server. The smoke must use a full native plugin snapshot pinned to base revision `5c6dcd401e9a0d115e79c19f02de96ffed694686`, whose checked-in MCP manifest declares only Context7 and Semgrep, in an isolated evaluation workspace. Preserve the dirty source and do not invoke GitHub or mutate user Codex configuration. Keep zero Copilot calls and the fixed Codex budget. The user reports separate tester success, but no tester command, run ID, or result artifact was found locally; treat it as user-reported context, not internal evidence. The Planner attempt `planner-cost-1` was interrupted; no Planner output is claimed.
- Source: `todos/harness/cost-eval-opt.md` (the five referenced task documents remain unchanged).

## Scope and gates

Deliver only the `cost-eval-opt` phase. The two attached `in_progress` notes are unfinished context; the remaining agentic-core backlog is outside this plan. The GitHub authorization-boundary check is a separate external gap and is not a dependency for local evaluation implementation. Do not guess a denied repository name.

Use static local validation before the bounded smoke. Codex is the default for costly evaluation. The product must support the allowed Copilot reason values (`copilot_specific_behavior`, `portability_sample`, `regression_confirmation`, `host_specific_agent_behavior`), but this delivery attempt is budgeted for zero Copilot calls. Run the smoke in an isolated workspace through the complete native `agentic-core` plugin pinned to base revision `5c6dcd401e9a0d115e79c19f02de96ffed694686`, using its two checked-in MCP servers: Context7 and Semgrep. Preserve the current dirty `agentic-core/mcp.json`, which adds an unapproved GitHub server; do not invoke GitHub or change Codex user configuration. In the Codex subprocess, load `agentic-core/skills/quality-engineering/SKILL.md` and its `workflows/eval-harness.md`; do not delegate to another model agent or recursively validate the harness. If the base-pinned full plugin cannot be loaded without mutating user or repository state, block the smoke rather than falling back to the dirty plugin. Do not run a massive benchmark or optimization corpus in this phase.

All implementation tasks must first inspect and preserve the shared dirty worktree, including untracked `harness_factory/` sources and tests. Do not overwrite or attribute pre-existing changes without evidence. This plan does not authorize staging, committing, branch/worktree creation, or other lifecycle changes.

## Revision history

- r2: validation procedures updated to exclude unit, regression, and validator test additions/runs; the source-requested single bounded smoke remains allowed. Acceptance criteria, task IDs, scopes, dependencies, and requirement traceability are unchanged.
- r3: supersedes r2's no-MCP smoke limitation after explicit user steering. The single Codex smoke now targets the full native `agentic-core` plugin and declared MCP servers in an isolated workspace, using the `quality-engineering` / `eval-harness` workflow. Budgets and all acceptance criteria remain unchanged.
- r4: pins that smoke to the clean base-revision plugin snapshot, excluding the current user-modified GitHub MCP declaration from the smoke while preserving it in the shared worktree. The full plugin's Context7 and Semgrep MCP servers remain enabled.

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
- **Bounded components:** existing `harness_factory` models and new suite/validation module(s); deterministic suite fixtures only. Do not modify `tests/` in this session. Preserve current adapter and run APIs unless a required compatibility change is evidenced.
- **Dependencies:** none.
- **Acceptance mapping:** `AC-COST-1`.
- **Expected output:** versioned suite data and explicit validation-error paths that do not invoke either harness.
- **Validation:** static inspection of schema and validator paths; Ruff lint/format checks when available. Do not add or execute unit, regression, or validator test cases.
- **Phase exit:** static evidence confirms versioned suite fields and validation branches are explicit; runtime behavior remains unverified until the one bounded smoke, if reached.

## Phase 2 — Runner, budgets, artifacts, and CLI

### `TASK-COST-02` — Cost policy, budget gates, and cross-harness rules

- **Owner:** Implementer.
- **Objective:** Enforce Codex-first target selection, the Copilot reason enum, explicit run/model-call/known-token/failure budgets, fail-fast conditions, and isolated read-only cross-harness validation with no recursive delegation or validation ownership transfer.
- **Bounded components:** `harness_factory` scenario/run models, adapters, run orchestration, CLI, and product modules only. Reconcile the pre-existing adapter implementation before editing; do not add or run unit/regression tests.
- **Dependencies:** `TASK-COST-01`.
- **Acceptance mapping:** `AC-COST-2`, `AC-COST-4`, `AC-COST-8`.
- **Expected output:** a suite-only Codex invocation path; Copilot requests rejected before launch unless a valid reason is supplied; cost limits checked before launch and during result collection; read-only cross-harness request validation.
- **Validation:** static inspection of policy and budget branches plus Ruff lint/format checks when available. No adapter-mock, unit, regression, or validator test execution. Keep unknown token counts as unknown; enforce token caps only when usage is known.
- **Phase exit:** static evidence shows invalid or over-budget requests are gated before invocation, systemic failures stop subsequent calls, and cross-harness validation is read-only and single-depth.

### `TASK-COST-03` — Durable run records and matched comparison

- **Owner:** Implementer.
- **Objective:** Persist one machine-readable artifact for every completed/failed run and compare candidate profiles over matched fixture, prompt, and expected behavior.
- **Bounded components:** `harness_factory` result/serialization/storage/comparison modules and CLI. Markdown is a projection only; do not add or run unit/regression tests.
- **Dependencies:** `TASK-COST-02`.
- **Acceptance mapping:** `AC-COST-3`, `AC-COST-5`, `AC-COST-6`.
- **Expected output:** run artifact includes suite, harness, model, base revision, profile, results, metrics, failures, token usage, latency, and raw-artifact references; evaluator accepts a profile/plugin input without knowing how it was generated.
- **Validation:** static inspection of record serialization, required fields, comparison identity checks, and unknown-value handling; Ruff lint/format checks when available. The bounded user-requested smoke/evaluation is the only runtime/model validation.
- **Phase exit:** static evidence confirms durable record and paired-comparison paths preserve identical evidence identity; runtime behavior is evidenced only by the bounded smoke, if reached.

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
- **Objective:** Run at most one bounded Codex smoke/evaluation against the complete native `agentic-core` plugin snapshot pinned to base revision `5c6dcd401e9a0d115e79c19f02de96ffed694686`, from an isolated evaluation workspace. Its base-revision manifest declares Context7 and Semgrep MCP. Use the plugin's `quality-engineering` skill and `eval-harness` workflow; exercise the smallest informative case for plugin loading/MCP exposure and the implemented evaluation path, within the run budget.
- **Bounded components:** only the frozen phase-3 fixtures and the new evaluation records; no unrelated benchmark corpus.
- **Dependencies:** `TASK-COST-04`.
- **Acceptance mapping:** `AC-COST-2`, `AC-COST-4`, `AC-COST-5`.
- **Expected output:** exact command/scenario/profile and pinned revision, predeclared budget, durable result ID, outcome of the full plugin and Context7/Semgrep paths, actual tool-call evidence or an explicit unavailable-server gap, and any observed failures; record no Copilot or GitHub MCP invocation for this attempt.
- **Validation:** static inspection only before the single Codex smoke. Budget: `max_runs=1`, `max_model_calls=1`, `max_tokens_if_known=25000`, `max_failures_before_stop=1`, `copilot_max_model_calls=0`. Run the full native plugin snapshot pinned to `5c6dcd401e9a0d115e79c19f02de96ffed694686` in an isolated workspace with its Context7/Semgrep MCP servers enabled and use `quality-engineering` / `eval-harness` in the subprocess. The frozen prompt should request one minimal, task-relevant interaction with each MCP server if its tool is exposed; record exposure separately from a successful tool call. Do not invoke the current worktree's GitHub MCP server; preserve its changed `mcp.json`. Do not edit Codex user configuration. If this exact pinned plugin source is not available in isolation, record a blocked smoke and make no call. Stop at the first systemic materialization/plugin/MCP/schema/routing failure; do not retry, delegate to another model, or recurse into harness validation. Treat this single trial only as a smoke result; do not claim reliability from one success.
- **Phase exit:** the single bounded smoke is complete or blocked with exact evidence; no additional harness run occurs.

### `TASK-COST-06` — Independent QA

- **Owner:** quality-assurance.
- **Objective:** Independently inspect scenario validation, policy gates, budget/fail-fast paths, durable artifacts, matched comparisons, profile-agnostic evaluation, cross-harness restrictions, and the bounded smoke evidence. Do not add or execute unit/regression tests.
- **Dependencies:** `TASK-COST-05` and current implementation evidence from `TASK-COST-01` through `TASK-COST-04`.
- **Acceptance mapping:** all `AC-COST-1` through `AC-COST-8`.
- **Expected output:** QA report ID, findings, static evidence inspected, remaining gaps, and next owner; QA makes no production edits or test invocations.
- **Validation:** inspect the invalid/boundary branches, over-budget handling, systemic fail-fast, artifact shape, fixture identity checks, read-only mutation restrictions, and recursion denial; reconcile the single smoke artifact and verify its predeclared budget. No additional runtime or test invocation.
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
- This attempt makes zero Copilot calls; product invocation policy must still require an allowed `reason` in both invocation and run artifact.
- No unit, regression, or validator test files are added or executed in this session. The user-requested suite fixtures and at most one small Codex smoke/evaluation are in scope; use static inspection and Ruff checks for all other validation.
- One smoke result cannot by itself establish a matched two-profile baseline. Use only valid pre-existing matched artifacts for the flat-versus-hierarchical comparison; if none exist, record `AC-COST-3` as an evidence gap rather than exceeding the run budget or presenting a single run as a pair.
- No massive benchmark matrix, repeated corpus, SkillOpt/GEPA/custom optimizer, or self-improvement loop runs in this phase.

## Known context and risks

- `harness-adapters-phase1.md` documents adapter behavior and 24 deterministic tests, but the local `harness_factory/` and its test file are untracked; re-inspect the live files and preserve them before modification. The parent reports the 24-test baseline passes; record the exact command/run details in the implementation handoff before using it as validation evidence.
- The phase-1 report documents that a full `agentic-core` run was previously refused because its declared MCP servers could not be disabled per plugin. User steering now explicitly authorizes a full-plugin smoke with Context7/Semgrep in an isolated workspace. Parent inspection found a user-owned uncommitted third GitHub declaration in the current `mcp.json`; pin smoke configuration to the clean base revision and preserve the dirty file. The parent confirms the native plugin is installed/enabled; the user's separate tester result is not persisted locally, so do not cite it as internal smoke evidence.
- The GitHub authorization-boundary note remains blocked pending a known-existing denied repository name. It is an external predecessor gap, not a local evaluator dependency.
- Other unfinished `todos/in_progress` items remain unfinished and outside this phase.

## Handoff

Next: Implementer receives `TASK-COST-01` through `TASK-COST-05` as sequential scoped work after inspecting the shared dirty worktree; return changed files, validation, evidence, and commit SHAs only if the authorized lifecycle requires commits. Then run independent QA `TASK-COST-06`, Reviewer gate `TASK-COST-07`, and SDD convergence task `TASK-COST-08`.
