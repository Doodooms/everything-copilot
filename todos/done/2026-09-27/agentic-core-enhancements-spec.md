# SPEC-CORE-ENHANCEMENTS, revision 4

Revision 4 supersedes revision 3 after review of the actual architecture input file. That file is a review protocol, not a prioritized proposal list. This revision corrects REQ-6/AC-6 and records the final implementation and tracking scope.

## Objective

Improve the agentic-core plugin's context and harness resource decisions, validate machine-readable handoffs, modernize Rust MCP authoring guidance, assess the supplied integration candidates, and leave a clear backlog record. Preserve the separate harness evaluation task already in progress.

## Requirements

- **REQ-1 — Context-aware compaction.** Add a `smart-compact` procedure that uses exact live context telemetry only when the active host exposes it. Otherwise report a local estimate with its method or `unknown`; never describe an estimate as the active session's exact token count. Compact only at a safe phase boundary after a durable handoff.
- **REQ-2 — Quota-aware harness distribution.** Add a `harness-distribution` procedure that checks the available five-hour and weekly usage data at task start, before expensive dispatches, and at meaningful phase boundaries. It must report used/remaining/reset information with source and timestamp, or mark the field `unknown`. Preserve the user's preference for Codex on heavy workloads and limited Copilot use, while adapting only to observed budget and task-fit evidence. Do not scrape credentials, bypass quotas, or claim timer/heartbeat support.
- **REQ-3 — Validated exchanges.** Define a language-neutral, versioned contract for machine-readable agent/task/harness handoffs and validate it before passing it on. Distinguish Git commit object IDs (40 or 64 hexadecimal characters) from SHA-256 artifact digests (64 hexadecimal characters); verify repository references when a repository is available. Keep explanatory reports in Markdown, with a validated structured envelope for required handoff fields.
- **REQ-4 — Rust MCP authoring.** Integrate the Rust MCP methodology into the existing MCP authoring route as a specialized workflow, grounded in current official `rmcp` documentation. Cover transport choice, typed inputs, errors, state, lifecycle, testing, performance, and host integration without presenting unverified snippets as current APIs.
- **REQ-5 — Candidate feasibility.** Assess every in-scope candidate in `todos/gh-repos/gpt-confirmed.md`. Record fit, integration path, maturity/maintenance/license evidence where available, cost/dependencies, and a recommendation. Do not add integrations merely because they appear in the list; omit the user's excluded subject matter.
- **REQ-6 — Architecture review brief disposition.** Treat `todos/agents/agent_architect_ideas.md` as a review-method brief, not as a prioritized list of architecture proposals or authority to expand this task into an unrelated full-repository audit. Record that distinction, assess the current plugin architecture against the task's bounded requirements, and preserve the source with an accurate disposition report.
- **REQ-7 — Work tracking.** Provide one concise index connecting idea sources, active work, completed reports, and backlog. On task closure, leave no files under `todos/in_progress`. Move unrelated, unassigned, blocked, or trigger-dependent records to a clearly labeled backlog; this relocation must not imply that they are implemented or complete. Put this task's final report and specification under `todos/done`.
- **REQ-8 — Parallel-work preservation.** Preserve the separate `task_3` / `harness_factory` phase-1 source files, tests, and canonical task ledger. Do not make task_4 edits in those paths.

## Acceptance criteria

- **AC-1 (REQ-1):** `multi-harness` exposes `smart-compact`, and its decision table separates host-reported exact usage, locally estimated usage, and unavailable usage; phase-boundary and handoff rules are explicit.
- **AC-2 (REQ-2):** `multi-harness` exposes `harness-distribution`, names the check points and evidence fields, and defines a fail-closed behavior for unavailable or exhausted budgets without changing accounts or permissions.
- **AC-3 (REQ-3):** The plugin contains versioned schemas and a local validator for the selected exchange envelope(s); handoff instructions require a validator result and treat omitted/unverifiable commit information explicitly.
- **AC-4 (REQ-4):** The MCP authoring route links to one Rust-specific workflow, and its API claims are backed by current official documentation or clearly labeled as version-dependent.
- **AC-5 (REQ-5):** A report evaluates all in-scope listed candidates and omits the excluded subject matter.
- **AC-6 (REQ-6):** The architecture report accurately identifies the supplied file as a review brief, records the bounded architecture conclusion and any task-related changes, and does not attribute proposals that the source does not contain.
- **AC-7 (REQ-7):** The tracking index distinguishes idea intake, active work, backlog, and completed reports and links this task's exact artifacts.
- **AC-8 (REQ-8):** Existing `task_3` / `harness_factory` phase-1 files are preserved; no changes are made to that workstream.
- **AC-9:** At closure, `todos/in_progress` contains no files. Unfinished material remains discoverable in `todos/backlog` with its uncompleted or blocked state stated accurately; `task_3` remains active in its canonical task ledger and is not modified.

## Constraints and assumptions

- The current worktree contains unrelated, uncommitted work, including the other session's harness evaluation. Preserve it; do not stage, commit, reset, or clean the repository.
- User-provided usage preference is a routing default, not proof of live remaining quota.
- Provider reporting differs. Current documented surfaces include Codex `/status` and its usage dashboard; Copilot CLI `/context` reports live context-window use, `/usage` reports per-session model token/credit totals, and account settings report plan-cycle consumption. Codex plan allowances can include rolling five-hour and weekly windows; do not project those exact windows onto Copilot.
- These interactive/private usage surfaces are not callable through this session's tool catalog. Record outputs only when supplied by the user or a harness host; do not inspect private session stores.
- Cross-harness calls require fresh provider evidence. A quota/authentication denial blocks the call and is recorded as a limitation; do not bypass it by changing accounts or providers.
- Research candidates for integration; implementation is limited to selected compact plugin workflow improvements, schemas/validator, and durable work-tracking artifacts. Do not import candidate code or add broad runtime architecture.

## Semantic model

- **SM-1 — Context observation:** A token count is an observation with `value`, `unit=tokens`, `source`, `observed_at`, and optional `context_window`. Its knowledge state is `host_reported`, `local_estimate`, or `unknown`. Only `host_reported` can be called exact for the active session. A local estimate must name its estimator and input coverage; unknown is not zero.
- **SM-2 — Harness budget snapshot:** A provider usage snapshot has `harness`, `window` (`rolling_5h` or `weekly`), `observed_at`, `source`, `used`, `remaining`, `reset_at`, and a knowledge state. Each numeric field may be unavailable; unknown values are omitted or null with an explicit state, never inferred from a past report.
- **SM-3 — Handoff envelope:** A handoff has a schema version, task/attempt identity, producer and intended recipient, outcome, bounded payload/evidence references, changed paths, validation results, and commit references. `git_commit` is a repository object ID (40- or 64-character hex); `artifact_sha256` is a SHA-256 content digest (64-character hex). Validation confirms structure and can resolve commit IDs only when the named repository is available; it cannot prove claims in the payload.
- **INV-1:** A compaction or session transfer is eligible only at a safe phase boundary after current task state, changed files, evidence, blockers, and next action are preserved.
- **INV-2:** An exchange is not considered validated or accepted merely because it was emitted, queued, or structurally parsed; those are separate states.
- **Unknowns:** The current tool catalog exposes no active-session telemetry or authenticated provider usage query. Current official CLI documentation does provide user-invoked surfaces (Codex `/status`; Copilot `/context` and `/usage`; account usage dashboards), but this task cannot query another active session or establish its actual current context or quota.

## Scope exclusions

- Omit the user's explicitly excluded subject matter from research and reports.
- No implementation or modification of the separate harness-evaluation phase.
- No automatic account/quota access, credentials inspection, or external deployment. A local cache refresh of the already-installed plugin is authorized by the user's earlier request; marketplace additions or account/configuration changes are out of scope.
- No general-purpose audit of unrelated repository code.
