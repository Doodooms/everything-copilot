# Workspace change classification

Checkpoint inventory for the local canonical lineage at `main`. This records why files are included, excluded, or held for their current owner; it does not authorize remote GitHub changes.

## Released in this checkpoint

| Class | Paths | Decision |
|---|---|---|
| Plugin/runtime source | `agentic-core/`, `expertise/targets/codex.py` | Version the coherent Agentic Core skill, MCP, multi-harness, exchange-validation, and Codex projection work. |
| Tests | `tests/test_agentic_core_sources.py` | Version focused source/topology regression coverage. |
| Codex installer | `scripts/install_codex_agents.py` | Canonical installer: referenced by task plans, plugin guidance, and validation records; uses `expertise.targets.codex.render_codex_agent`. |
| Shared configuration | `.agents/plugins/marketplace.json`, `.markdownlint.json`, `agentic-core/plugin.json`, `agentic-core/mcp.json` | Version portable plugin marketplace, lint, and plugin manifests. |
| Git handoff conventions | `AGENTS.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `docs/git-workflow.md` | Version scoped commit/PR conventions and the minimal handoff template. |
| Task reports and history | `docs/harness-history/task_4/`, `docs/harness-history/task_5/`, matching task 4/5 planner and task records, `todos/` task 4/5 records | Preserve implementation history, current partial status, and review follow-up ownership. |

## Preserved outside this checkpoint

| Class | Paths | Decision |
|---|---|---|
| Active other-session ownership | `harness_factory/`, `tests/test_harness_factory.py`, `experiments/harness-evals/`, `experiments/routing/`, `outputs/evals/baseline-inventory-r7.json`, task 3 histories and `todos/harness/cost-eval-opt.md` | `task_3` remains active. Do not stage or commit these files until its owner releases them. |
| Machine-local VS Code preference | `.vscode/settings.json` | Contains the user's editor preference; preserve locally and do not include in this checkpoint. |
| Redundant installer candidate | root `install_codex_agents.py` | Not referenced by canonical task plans and duplicates `scripts/install_codex_agents.py`; retain untracked pending owner review. |
| User notes and unassigned inputs | root `todo.md`, `todos/harness/`, `todos/plugins/`, `todos/skills/`, `todos/gh-repos/`, `todos/agents/`, `todos/mcp/` | Preserve as intake material; do not treat an idea as accepted implementation scope. |
| Stale ownership records | `docs/` task 1 and task 2 records | Not listed as active in `todos/README.md`; preserve pending an explicit history audit rather than claim completion. |
| Overlapping README | root `README.md` | Its current diff mixes task 3 harness work with plugin/Codex updates; leave intact until the active owner or a later scoped edit resolves it. |
| Tracked bytecode drift | tracked `__pycache__/*.pyc` changes | Root ignore prevents new untracked bytecode, but ignored rules do not untrack files already in Git. Keep their current changes unstaged. |

## Ignored local/generated files

The root `.gitignore` excludes Python bytecode and common local caches, `.vscode/copilot-tools.snapshot.json`, `.tools/bin/waza`, `.tools/bin/extension.yaml`, and the two raw SkillOpt run directories. It does not ignore `outputs/` wholesale: curated evidence under `outputs/evals/` remains trackable, subject to its task owner.

The Waza executable and extension manifest are locally installed artifacts. The Copilot snapshot is generated workspace state. Raw SkillOpt runs are reproducible outputs rather than curated fixtures. On 2026-09-27, the two ignored raw SkillOpt run trees and the generated Copilot snapshot were removed from the working tree; curated benchmark fixtures and `outputs/evals/baseline-inventory-r7.json` were preserved.

## Ownership state

- `task_5` implementation and automated validation are recorded; its QA and Reviewer handoffs remain unexecuted due to the active host's missing custom-role dispatch surface. The task manifest remains partial and the next action is in `todos/backlog/2026-09-27/agentic-core-normalization-review-gates.md`.
- `task_3` remains the sole currently active implementation task in `todos/README.md` and was not edited by this checkpoint.
- `v1.0.0` remains an immutable annotated checkpoint at the previous local `main` tip. No tag or remote ref was changed.
