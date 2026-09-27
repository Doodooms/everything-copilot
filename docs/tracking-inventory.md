# Workspace change classification

Inventory for the local canonical lineage at `main`. This records what belongs in the candidate lineage and classifies current workspace files kept outside Git. It does not authorize changing existing remote refs.

## Released in this checkpoint

| Class | Paths | Decision |
|---|---|---|
| Plugin/runtime source | `agentic-core/`, `expertise/targets/codex.py` | Version the coherent Agentic Core skill, MCP, multi-harness, exchange-validation, and Codex projection work. |
| Tests | `tests/test_agentic_core_sources.py` | Version focused source/topology regression coverage. |
| Codex installer | `scripts/install_codex_agents.py` | Canonical installer: referenced by task plans, plugin guidance, and validation records; uses `expertise.targets.codex.render_codex_agent`. |
| Shared configuration | `.agents/plugins/marketplace.json`, `.markdownlint.json`, `agentic-core/plugin.json`, `agentic-core/mcp.json` | Version portable plugin marketplace, lint, and plugin manifests. |
| Git handoff conventions | `AGENTS.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `docs/git-workflow.md` | Version scoped commit/PR conventions and the minimal handoff template. |
| Task reports and history | `docs/harness-history/task_3/`, `docs/harness-history/task_4/`, `docs/harness-history/task_5/`, matching planner/task records, `todos/` task 3/4/5 records | Preserve task 3's released partial checkpoint and task 4/5 history and follow-up ownership. |
| Harness evaluation | `harness_factory/`, `tests/test_harness_factory.py`, `experiments/harness-evals/`, `experiments/routing/`, `outputs/evals/baseline-inventory-r7.json` | Task 3 commits `12ae228`, `783316b`, and `ec3d700` are preserved in the candidate lineage. External evaluation gates remain documented as partial. |

## Preserved outside this checkpoint

| Class | Paths | Decision |
|---|---|---|
| Machine-local VS Code preference | `.vscode/settings.json` | Local-only editor preference; preserve outside the candidate. |
| Unowned implementation candidate | `expertise/targets/antigravity_plugin.py`, `scripts/project_antigravity_plugin.py`, `tests/test_antigravity_plugin_projection.py`, `docs/skill-optimization.md` | Untracked source/test/documentation with no released task ownership in the current handoff. Preserve outside the candidate pending task 1/2 history reconciliation. |
| Uncertain task history | `docs/harness-history/task_1/{events.jsonl,manifest.json}`, `docs/planner-history/task_1/plan-r1.md` through `plan-r3.md`, `docs/tasks-history/task_1.jsonl`; `docs/harness-history/task_2/{architecture-r1.md,architecture-r2.md,architecture-r3.md,events.jsonl,manifest.json,p0-audit.md}`, `docs/planner-history/task_2/plan-r1.md`, `docs/tasks-history/task_2.jsonl` | Manifests say `in_progress`, while `todos/README.md` lists no active task 1/2 owner. Preserve as task-state/provenance artifacts; do not infer release or completion. |
| Obsolete duplicate candidate | root `install_codex_agents.py` | Untracked duplicate of the tracked canonical `scripts/install_codex_agents.py`. README now references the canonical script. Keep the duplicate untouched pending owner review. |
| User notes and unassigned inputs | root `todo.md`; `todos/harness/*.md`, `todos/plugins/*.md`, `todos/skills/*.md`, `todos/gh-repos/*.md` | Idea intake and research notes; preserve locally without treating ideas as accepted implementation scope. |
| Historical work records | `todos/backlog/2026-09-26/*.md`, `todos/done/2026-09-26/*.md` | Untracked backlog inputs and historical reports/source records. Preserve as documentation artifacts pending a separate history audit. |
| README convergence | root `README.md` | Task 5 Codex/plugin and task 3 harness sections are retained together. The Codex installer command points to the tracked canonical script; this scoped documentation change is included in the convergence commit. |

## Ignored local/generated files

The root `.gitignore` excludes Python bytecode and common local caches, `.vscode/copilot-tools.snapshot.json`, `.tools/bin/waza`, `.tools/bin/extension.yaml`, and the two raw SkillOpt run directories. It does not ignore `outputs/` wholesale: curated evidence under `outputs/evals/` remains trackable, subject to its task owner.

The Waza executable and extension manifest are locally installed artifacts. The Copilot snapshot is generated workspace state. Raw SkillOpt runs are reproducible outputs rather than curated fixtures. On 2026-09-27, the two ignored raw SkillOpt run trees and the generated Copilot snapshot were removed from the working tree; curated benchmark fixtures and `outputs/evals/baseline-inventory-r7.json` were preserved.

## Ownership state

- `task_5` remains `partial`; its manifest still marks implementation `in_progress`, while QA and Reviewer are blocked in this host. The current collaboration surface has no other active agent. Preserve that status rather than infer a task 5 release. Its follow-up is in `todos/backlog/2026-09-27/agentic-core-normalization-review-gates.md`.
- `task_3` is released as `PARTIAL_WITH_DOCUMENTED_GATES`; its manifest has no current implementation tasks and its source, tests, fixtures, baseline inventory, and state records are committed locally. Its remaining gates are unassigned in `todos/backlog/2026-09-27/cost-eval-opt-followups.md`.
- Task 1/2 manifests remain untracked and report `in_progress`, despite not appearing in the active-work index. This inconsistency remains for a separate history/ownership audit.
- `v1.0.0` remains an immutable annotated checkpoint at the previous local `main` tip. No tag or remote ref was changed.
