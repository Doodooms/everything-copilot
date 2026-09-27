# Plan — Codex-first behavioral evaluation

## Identity and approval

- `task_id`: `task_3`
- `plan_revision`: 7
- `status`: approved
- `specification`: `SPEC-COST-EVAL-OPT@1`
- `architecture`: not required for this plan; use the existing `harness_factory` boundary and revisit only if implementation evidence shows it cannot satisfy the specification.
- Approval note: r7 preserves `SPEC-COST-EVAL-OPT@1`, requirement/acceptance mappings, task IDs, scopes, and dependency DAG. It supersedes r6 only for the smoke source and isolation controls. The smoke now targets the installed `agentic-core@0.2.0` shared-cache plugin with normal Codex user configuration (`codex exec`, no `--ignore-user-config`) so the updated `multi-harness` skill and `workflows/codex.md` are discoverable. The cache files match local source by SHA256: `SKILL.md` `72330f25c58e6a99f235a3ad459c3caac4e8ab9fd297884f01bdf73042d2ba46`, `workflows/codex.md` `2c204f19efbc4d249e4beac175c4c3e591a7faca0e5363ea1e2688972a8aca29`, `workflows/copilot.md` `2dc39d384848e99ba067d2e13bdab43b2e5ca114000bfa85f5d96adbe65da028`. The cache declares Context7, GitHub, and Semgrep. Parent reports official configuration supports disabling the plugin GitHub server via a project-level setting; a `-c` override is not proof of effective isolation, and Codex prompt-input diagnostics expose no MCP tools either way. Codex has no tool allowlist or provider-call/turn cap, so the one-invocation objective cannot guarantee `max_model_calls=1`. Therefore the model smoke is blocked before execution unless a safe enforceable path is established within scope; no Codex model call or MCP invocation has occurred. Keep budgets unchanged, including zero Copilot. `HarnessRunManager` alone may manage the one ephemeral detached smoke workspace and clean it only after exact ownership-marker verification. Preserve all user changes and configuration. User-reported Context7/Semgrep runtime success remains separate and is not evidence from this run. Planner attempt `planner-cost-1` was interrupted; no Planner output is claimed.
- Source: `todos/harness/cost-eval-opt.md` (the five referenced task documents remain unchanged).

## Scope and gates

Deliver only the `cost-eval-opt` phase. The two attached `in_progress` notes are unfinished context; the remaining agentic-core backlog is outside this plan. The GitHub authorization-boundary check is a separate external gap and is not a dependency for local evaluation implementation. Do not guess a denied repository name.

Use static local validation before any bounded model invocation. Codex is the default for costly evaluation. The product must support the allowed Copilot reason values (`copilot_specific_behavior`, `portability_sample`, `regression_confirmation`, `host_specific_agent_behavior`), but this delivery attempt is budgeted for zero Copilot calls. Verify the installed/enabled `agentic-core@0.2.0` plugin and synchronized `multi-harness` skill in the shared Codex cache. The cached MCP manifest declares Context7, GitHub, and Semgrep; the GitHub server must be disabled without editing user/global configuration. A process-only `-c` override is not accepted as proof of isolation: `codex plugin list` continues to report other plugins enabled, and `codex debug prompt-input` shows skill discovery but does not expose MCP tools. The local `codex exec` has no tool allowlist or max-turn/provider-call cap, so one invocation cannot enforce one provider call. Unless an enforceable, non-persistent isolation and call-bound can be established before the model invocation, record the smoke as blocked and make no model call. The user reports a separate successful Context7/Semgrep test; do not present it as internal evidence. Keep the run-manager ownership-marker boundary and do not edit Codex configuration. Do not run a massive benchmark or optimization corpus in this phase.

All implementation tasks must first inspect and preserve the shared dirty worktree, including untracked `harness_factory/` sources and tests. Do not overwrite or attribute pre-existing changes without evidence. No delivery branch/worktree, cherry-pick, staging, commit, PR, merge, or manual cleanup is authorized. The only exception is the temporary detached worktree created and managed by `HarnessRunManager` for the single isolated smoke; its exact normal cleanup is permitted only under a verified ownership marker. If the marker is missing or mismatched, stop and preserve it.

## Revision history

- r2: validation procedures updated to exclude unit, regression, and validator test additions/runs; the source-requested single bounded smoke remains allowed. Acceptance criteria, task IDs, scopes, dependencies, and requirement traceability are unchanged.
- r3: supersedes r2's no-MCP smoke limitation after explicit user steering. The single Codex smoke now targets the full native `agentic-core` plugin and declared MCP servers in an isolated workspace, using the `quality-engineering` / `eval-harness` workflow. Budgets and all acceptance criteria remain unchanged.
- r4: pins that smoke to the clean base-revision plugin snapshot, excluding the current user-modified GitHub MCP declaration from the smoke while preserving it in the shared worktree. The full plugin's Context7 and Semgrep MCP servers remain enabled.
- r5: clarifies that only `HarnessRunManager` may manage the ephemeral detached worktree used for the isolated smoke; cleanup is allowed only when its exact ownership marker is verified, otherwise preserve the workspace. Delivery lifecycle remains prohibited.
- r6: pinned the smoke to the clean base snapshot and prohibited tool/agent follow-up because Codex exposes no provider-call/turn cap. Superseded by r7 for the current installed skill version.
- r7: use installed shared-cache plugin v0.2.0 and the hash-matched `multi-harness` skill. Disable GitHub MCP and isolate other enabled plugins only through a proven non-persistent mechanism. Since current CLI diagnostics do not prove MCP isolation and `codex exec` has no tool allowlist or turn cap, block before model invocation unless those guarantees are established; do not claim a runtime pass.

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
- **Objective:** At most one bounded Codex smoke/evaluation in the HarnessRunManager-owned isolated workspace using the installed/enabled `agentic-core@0.2.0` plugin from the shared Codex cache and its synchronized `multi-harness` skill plus Codex workflow. The cache `mcp.json` declares Context7, GitHub, and Semgrep. The GitHub server must be disabled without persistent user/global config changes. Keep zero MCP/tool invocations, zero Copilot contact, and zero delegation.
- **Bounded components:** only the frozen phase-3 fixture and new evaluation record; no unrelated benchmark corpus.
- **Dependencies:** `TASK-COST-04`.
- **Acceptance mapping:** `AC-COST-2`, `AC-COST-4`, `AC-COST-5`.
- **Expected output:** exact command/scenario/profile, plugin version/cache identity and skill SHA256s, isolated workspace ID, ownership-marker and cleanup outcome, isolation method, predeclared budget, durable result ID, skill/workflow discovery evidence, declared-MCP inventory (separate from invocation), actual model-turn/call count if exposed, and any failure. Do not claim successful MCP execution from this run.
- **Validation:** Budget remains `max_runs=1`, `max_model_calls=1`, `max_tokens_if_known=25000`, `max_failures_before_stop=1`, `copilot_max_model_calls=0`. Use `codex exec` with normal user config and no `--ignore-user-config`. Before model invocation, prove a non-persistent way to isolate all other plugins and disable GitHub MCP, and prove the call/turn bound is enforceable. Current evidence is insufficient: `codex plugin list` reports other installed plugins enabled despite attempted `-c ...enabled=false`; `codex debug prompt-input` proves `agentic-core:multi-harness` discovery from the cache but does not reveal MCP tools; `codex exec --help` has no tool allowlist or provider-call/turn cap. Therefore, unless new bounded evidence establishes both isolation and the one-call guarantee without changing persistent config or exceeding scope, mark the smoke blocked before invocation and make no model call. Do not invoke Copilot, any MCP/tool, or recursive validation. Keep the prompt read-only and prohibit writes/delegation. `HarnessRunManager` may clean only its own workspace after an exact ownership-marker match; if missing or mismatched, preserve it. Do not retry after any systemic failure or unknown/greater-than-one call count. User-reported Context7/Semgrep runtime success is not proof from this smoke; one trial cannot establish reliability.
- **Phase exit:** the single bounded smoke is complete only with exact evidence, or blocked before invocation with the isolation/budget evidence; no additional harness run occurs.

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
- Parent reports the shared Codex cache contains the current v0.2.0 `multi-harness` skill and the three files match local source by SHA256; our read-only `codex debug prompt-input` also shows skill discovery from that cache. The cache MCP manifest includes GitHub in addition to Context7 and Semgrep. Parent reports official project configuration can disable MCP/server exposure, but neither `-c` nor prompt-input output proves effective isolation. Codex has no tool allowlist/call cap, so the bounded smoke stays blocked before model invocation unless safety can be enforced. The user's separate MCP tester remains user-reported only.
- The GitHub authorization-boundary note remains blocked pending a known-existing denied repository name. It is an external predecessor gap, not a local evaluator dependency.
- Other unfinished `todos/in_progress` items remain unfinished and outside this phase.

## Handoff

Next: Implementer continues TASK-COST-03 through TASK-COST-05 sequentially under r7, preserving all added shared modules and the user-owned test file; return exact changed files and static evidence with no commits. Record the smoke as blocked before model invocation unless the isolation and call-bound gates are met. Then run independent QA TASK-COST-06, Reviewer gate TASK-COST-07, and SDD convergence TASK-COST-08.
