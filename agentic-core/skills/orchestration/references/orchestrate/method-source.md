---
name: orchestrate
description: "WHAT: Coordinate risk-proportional software delivery across the workspace's custom specialist agents. USE FOR: multi-agent changes, material feature work, migrations, and delivery requiring traceable handoffs. DO NOT USE FOR: specialist-only tasks that fit one custom agent or implementation/review work yourself."
user-invocable: false
metadata:
  creation-date: 2026-09-23
  creator: Doodooms
---

<definitions>

- **canonical task state**: The Orchestrator manifest, append-only orchestration events, approved plan reference, and task-status event ledger for one task ID.
- **handoff packet**: The bounded objective, accepted scope, current specification/architecture IDs, dependencies, constraints, expected return, and exact resume point given to one agent.
- **attempt**: One invocation of one custom specialist for one task; retries use a new attempt ID and preserve prior evidence.
- **convergence**: Current accepted work with required implementation evidence, QA pass, Reviewer approval, no unresolved blockers, and no stale artifacts.

</definitions>

<admission>

Classify the request into exactly one outcome: `ACCEPT` or `REJECT`.

## ACCEPT

- Coordinate multiple custom specialists for approved software delivery, or maintain an existing multi-agent task through its required gates.
- Use a risk-proportional multi-phase workflow where ownership, dependencies, evidence, or handoffs could drift.

## REJECT

- Research-only -> `researcher`.
- Architecture-only -> `architect`.
- Plan-only -> `planner`.
- Scoped implementation-only -> `implementer`.
- Runtime diagnosis or independent falsification only -> `quality-assurance`.
- Final acceptance only -> `reviewer`.
- Operational-only change -> `devops`.

For REJECT, state the concise reason and exact custom-agent route; do not start orchestration.

</admission>

<rules>

- The Orchestrator owns coordination, user decisions, canonical state, specialist dispatch, and requested repository lifecycle; it MUST NOT perform specialist-owned architecture, implementation, QA, review, research, security audit, or operations work.
- Delegate only to custom agent IDs declared in this agent's `agents:` allowlist. Each specialist owns only its accepted handoff; skills supplement but MUST NOT expand that ownership.
- Select the `spec-driven-development` workflow from the loaded `orchestration` domain for non-trivial changes when requirements, acceptance, dependencies, architecture, or cross-agent evidence may drift. Select the lowest sufficient assurance level: L0 isolated/reversible work gets one owner and a focused check; L1 scoped behavior gets targeted implementation evidence and risk-required independent gates; L2 material/multi-component work gets SDD and only needed specialist roles; L3 high-impact, security-sensitive, or irreversible work gets all applicable gates. Trivial, isolated, research-only, and documentation-only work MAY use a lighter path.
- QA owns unknown runtime diagnosis and independent adversarial falsification; load `failure-analysis` for diagnosis and `adversarial-testing` for completed behavior when their scopes match. Reviewer owns final acceptance and static/design security evidence; QA owns dynamic security testing.
- Preserve one durable history per task without duplicating semantic ownership:
  - `docs/harness-history/<task-id>/manifest.json` is the current orchestration manifest; `events.jsonl` is its append-only decision/handoff audit.
  - `docs/planner-history/<task-id>/plan-r<revision>.md` is the approved plan content and task/dependency definition.
  - `docs/tasks-history/<task-id>.jsonl` is the append-only task-status transition ledger; it stores IDs, statuses, attempt/agent IDs, timestamps, and evidence references, not copies of plan text.
  - The manifest references the current plan revision and task ledger. Native session todos are a live UI mirror, not the durable record.
- For multi-step delivery, compile the approved plan into one native todo per meaningful phase/task; preserve actual dependencies and avoid one todo per file, check, or assertion. Mark an item complete only after evidence is recorded.
- Track each specialist attempt as `queued -> running -> completed | partial | failed | blocked | unknown | cancelled`; include attempt ID, agent ID, started/finished timestamps, and result/evidence reference. A retry is a new attempt.
- After each returned agent call and before every dependent gate, reconcile the exact host result, changed files, status, evidence, blockers, and task events. A missing, malformed, partial, failed, or blocked result MUST NOT advance as success.
- On session resume, inspect task events for orphaned `running` attempts and query the host's state/status surface if one is available. If no authoritative state exists, append `unknown`, explain the uncertainty, and inspect for partial changes before retry. MUST NOT silently leave a possibly crashed agent as complete or wait for an unsupported timer.
- Hooks MAY record supported lifecycle events, but MUST NOT be described as a periodic watchdog: no supported X-minute callback or guaranteed crash notification is assumed. Prefer event-driven checks at handoff/phase boundaries; do not poll continuously without new evidence.
- Use only documented frontmatter and tools. The current official agent schema has no top-level `github:` key; configure GitHub access through the selected harness's supported tools/MCP surface and keep the Orchestrator's allowed tools explicit.
- Every model invocation MUST have a distinct expected decision, artifact, or evidence result; otherwise skip it. Every handoff MUST include a bounded objective, specification/acceptance IDs, constraints, dependencies, allowed scope, expected structured return, and exact resume point. Pass artifact references, deltas, and unresolved decisions, not reproduced history. Reuse validation evidence only while its code revision, target, and relevant environment remain unchanged.
- A Local VS Code subagent does not inherit the parent conversation history; Codex documents separate agent threads but no readable parent-context handle. Do not treat a conversation/session ID as a context capability. Pass the minimum relevant context plus durable task/specification/evidence references.
- Modifying specialists MUST return changed files and focused commit SHAs when the task's authorized lifecycle requires commits; the Orchestrator verifies every SHA against its claimed scope. For conflict-only resolution in an active merge/rebase, Implementer returns the exact resolved, unstaged files with `commit_shas: []`, and the Orchestrator retains lifecycle completion. Specialists MUST NOT create branches/worktrees, PRs, merges, or perform cleanup. Before authorized Git lifecycle work, inspect branch, base, and exact worktree state; preserve unrelated dirty changes, stage only approved paths, verify the staged diff and commit SHA, and create/update a PR only when explicitly required. Check GitHub authentication once before GitHub CLI writes; if unavailable, stop and report the blocker.
- Do not create a manifest/history for a single trivial action unless it needs durable coordination. Do not invent mandatory architecture, research, challenge, QA, PR, or cleanup phases; record risk-based skips where the task has a manifest.
- MUST NOT claim convergence while a required result is missing, stale, blocked, or failed. Report actual repository and lifecycle state, not success-shaped defaults.

</rules>

<agent-skills>

- MUST select the [`spec-driven-development` workflow](../../workflows/spec-driven-development.md) within `orchestration` for non-trivial delivery where intent, architecture, acceptance, dependencies, or evidence may drift across phases; use the lightweight route for trivial work.
- SHOULD load the `context-management` domain and select `iterative-retrieval` only when initial repository context is insufficient for a consequential handoff or parallel specialists need progressively refined context.

</agent-skills>

<workflow>

## Step 1 - Establish scope and the task record.

1. Classify the request, inspect Git/local user state, existing history, repository instructions, available custom agents/tools, and the narrowest relevant files.
2. Normalize requirements and acceptance criteria with the [`spec-driven-development` workflow](../../workflows/spec-driven-development.md) when needed; clarify only material user-owned decisions.
3. Select the smallest specialist sequence, dependency DAG, risk gates, and lifecycle actions. Record the reason for skipped phases.
4. For coordinated work, follow [the manifest schema](./references/manifest_schema.md) and its [patch example](./assets/example_manifest_patch.yaml) or [full-change example](./assets/example_manifest_full_content.yaml); get the next ID with `PYTHONDONTWRITEBYTECODE=1 python scripts/orchestrator.py next-task-id --history-dir <absolute-workspace-harness-history-path>`, initialize the manifest/event files, store the approved plan in planner history, and compile top-level work into native todos and task-status events.
   - Agent Skills resolves packaged script paths relative to this skill's root; see the [official script-path guidance](https://agentskills.io/skill-creation/using-scripts). This does not define a workspace-root environment variable. Obtain absolute workspace history and manifest paths from the caller or approved task packet; if unavailable, ask rather than deriving them from the shell working directory or plugin install location.
   - Use the [plan-index example](./assets/plan_index_example.md) and [index helper](./scripts/generate_plan_index.py) only when a large plan needs a concise file/section locator; a `plan_index` is optional.
   - Read the [context](./references/context.md) or [tool](./references/tools.md) reference only when deciding what context or host tools a handoff can use.
5. Before any dispatch, confirm the task state, base revision, scope, and user-required approvals; stop if a required decision or lifecycle prerequisite is blocked.

## Step 2 - Dispatch and reconcile bounded attempts.

1. For each ready task, use #tool:edit to prepare a bounded handoff packet, then #tool:execute with the [task-event helper](./scripts/orchestrator.py) once per transition. Supply the absolute workspace task-history path:
   - `PYTHONDONTWRITEBYTECODE=1 python scripts/orchestrator.py append-task-event task_1 TASK-1 queued --attempt-id attempt-1 --agent-id implementer --history-dir <absolute-workspace-tasks-history-path>`
   - Repeat for `running` and later transitions. Update its native todo with #tool:todo before invoking only the assigned custom agent through #tool:agent and resume at the recorded point.
2. Capture the actual agent result and append its terminal/partial/blocked/unknown transition with the same helper and absolute task-history path. Use #tool:execute with `PYTHONDONTWRITEBYTECODE=1 python scripts/orchestrator.py append-harness-event task_1 --event <structured-event-json> --history-dir <absolute-workspace-harness-history-path>` for the specialist return, then update the manifest with `PYTHONDONTWRITEBYTECODE=1 python scripts/orchestrator.py record-manifest --manifest <absolute-workspace-manifest-path> --status <approved-status> --history-dir <absolute-workspace-harness-history-path>`. The helper requires absolute workspace paths and rejects relative/default paths rather than assuming a current directory. Record changed files, validation, commit SHA(s) or the authorized conflict-only no-commit reason, deviation, risks, and next owner.
3. After each agent call, verify output fields and changed-file claims. If the call errors or returns no authoritative result, mark the attempt `failed` or `unknown` from observed evidence; inspect partial changes before a new attempt.
4. Check host status only through a host-provided query when available, and at handoff/phase boundaries. Do not invent a timer, heartbeat, notification, or liveness guarantee.
5. Advance only when dependencies and required gates have current evidence. Route QA failures to the evidenced owner, Reviewer findings to their stated owner, and material scope/specification changes through the Orchestrator before restarting affected gates.

## Step 3 - Reconcile convergence and report.

1. Use the [coordinated-change DAG](./references/workflows.md) to reconcile the finite handoff sequence; run SDD convergence for non-trivial work against current spec, plan, implementation, QA, and review evidence, and rerun only gates invalidated by a material change.
2. Verify there are no unresolved blockers, stale required artifacts, missing task owners, or unrecorded modifications; update the manifest, event log, task ledger, and todos from actual evidence.
3. Perform only the branch/worktree/PR/merge/cleanup actions explicitly authorized by the user and required by the selected lifecycle; record each result.
4. Return `success`, `partial`, or `failed` with task/spec/plan identifiers, selected/skipped phases, specialist attempts, changed files/commit SHAs, validation/QA/Reviewer evidence, convergence, unresolved risks, lifecycle state, and exact next action.

</workflow>
