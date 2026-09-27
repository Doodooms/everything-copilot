# Routed workflow migration source map

> **SUPERSEDED as a destination map.** The `Target package` column reflects an erroneous attempt to promote workflow subskills to peer skill packages. Preserve the `Domain`, `Skill ID`, and `Current source` columns only as historical inventory; use plan r10 and `workflow-subskill-inventory.md` for current in-place work.

- Source state: task_5 plan r4, captured before migration.
- Inventory: 57 existing routed methods; every ID is unique and non-empty. A separate 58th method is added for same-harness coordination under `TASK-5-06`.
- Destination: one peer package at `agentic-core/skills/<id>/SKILL.md`.
- Keep the source method text intact during conversion; relocate only support resources proven to be consumed by it.
- Resolve every relative link/reference against the resulting package, and retain source provenance where required.

| Domain | Skill ID | Current source | Target package |
|---|---|---|---|
| `architecture` | `api-design` | `agentic-core/skills/architecture/workflows/api-design.md` | `agentic-core/skills/api-design/SKILL.md` |
| `architecture` | `architectural-immune-system` | `agentic-core/skills/architecture/workflows/architectural-immune-system.md` | `agentic-core/skills/architectural-immune-system/SKILL.md` |
| `architecture` | `architecture-design` | `agentic-core/skills/architecture/workflows/architecture-design.md` | `agentic-core/skills/architecture-design/SKILL.md` |
| `context-management` | `iterative-retrieval` | `agentic-core/skills/context-management/workflows/iterative-retrieval.md` | `agentic-core/skills/iterative-retrieval/SKILL.md` |
| `context-management` | `memory` | `agentic-core/skills/context-management/workflows/memory.md` | `agentic-core/skills/memory/SKILL.md` |
| `context-management` | `strategic-compact` | `agentic-core/skills/context-management/workflows/strategic-compact.md` | `agentic-core/skills/strategic-compact/SKILL.md` |
| `context-management` | `token-optimization` | `agentic-core/skills/context-management/workflows/token-optimization.md` | `agentic-core/skills/token-optimization/SKILL.md` |
| `multi-harness` | `codex` | `agentic-core/skills/multi-harness/workflows/codex.md` | `agentic-core/skills/codex/SKILL.md` |
| `multi-harness` | `copilot` | `agentic-core/skills/multi-harness/workflows/copilot.md` | `agentic-core/skills/copilot/SKILL.md` |
| `multi-harness` | `harness-distribution` | `agentic-core/skills/multi-harness/workflows/harness-distribution.md` | `agentic-core/skills/harness-distribution/SKILL.md` |
| `multi-harness` | `smart-compact` | `agentic-core/skills/multi-harness/workflows/smart-compact.md` | `agentic-core/skills/smart-compact/SKILL.md` |
| `operations` | `delivery-operations` | `agentic-core/skills/operations/workflows/delivery-operations.md` | `agentic-core/skills/delivery-operations/SKILL.md` |
| `operations` | `documentation-sync` | `agentic-core/skills/operations/workflows/documentation-sync.md` | `agentic-core/skills/documentation-sync/SKILL.md` |
| `operations` | `install-agent-plugin` | `agentic-core/skills/operations/workflows/install-agent-plugin.md` | `agentic-core/skills/install-agent-plugin/SKILL.md` |
| `operations` | `verification-loop` | `agentic-core/skills/operations/workflows/verification-loop.md` | `agentic-core/skills/verification-loop/SKILL.md` |
| `orchestration` | `commit-message` | `agentic-core/skills/orchestration/workflows/commit-message.md` | `agentic-core/skills/commit-message/SKILL.md` |
| `orchestration` | `implementation-planning` | `agentic-core/skills/orchestration/workflows/implementation-planning.md` | `agentic-core/skills/implementation-planning/SKILL.md` |
| `orchestration` | `orchestrate` | `agentic-core/skills/orchestration/workflows/orchestrate.md` | `agentic-core/skills/orchestrate/SKILL.md` |
| `orchestration` | `resolving-merge-conflicts` | `agentic-core/skills/orchestration/workflows/resolving-merge-conflicts.md` | `agentic-core/skills/resolving-merge-conflicts/SKILL.md` |
| `orchestration` | `spec-driven-development` | `agentic-core/skills/orchestration/workflows/spec-driven-development.md` | `agentic-core/skills/spec-driven-development/SKILL.md` |
| `plugin-engineering` | `agent-authoring` | `agentic-core/skills/plugin-engineering/workflows/agent-authoring.md` | `agentic-core/skills/agent-authoring/SKILL.md` |
| `plugin-engineering` | `agent-validation` | `agentic-core/skills/plugin-engineering/workflows/agent-validation.md` | `agentic-core/skills/agent-validation/SKILL.md` |
| `plugin-engineering` | `create-hook` | `agentic-core/skills/plugin-engineering/workflows/create-hook.md` | `agentic-core/skills/create-hook/SKILL.md` |
| `plugin-engineering` | `create-mcp-rust` | `agentic-core/skills/plugin-engineering/workflows/create-mcp-rust.md` | `agentic-core/skills/create-mcp-rust/SKILL.md` |
| `plugin-engineering` | `create-mcp` | `agentic-core/skills/plugin-engineering/workflows/create-mcp.md` | `agentic-core/skills/create-mcp/SKILL.md` |
| `plugin-engineering` | `optimize-skill` | `agentic-core/skills/plugin-engineering/workflows/optimize-skill.md` | `agentic-core/skills/optimize-skill/SKILL.md` |
| `plugin-engineering` | `plugin-creation` | `agentic-core/skills/plugin-engineering/workflows/plugin-creation.md` | `agentic-core/skills/plugin-creation/SKILL.md` |
| `plugin-engineering` | `plugin-update` | `agentic-core/skills/plugin-engineering/workflows/plugin-update.md` | `agentic-core/skills/plugin-update/SKILL.md` |
| `plugin-engineering` | `skill-authoring` | `agentic-core/skills/plugin-engineering/workflows/skill-authoring.md` | `agentic-core/skills/skill-authoring/SKILL.md` |
| `plugin-engineering` | `skill-maintenance` | `agentic-core/skills/plugin-engineering/workflows/skill-maintenance.md` | `agentic-core/skills/skill-maintenance/SKILL.md` |
| `quality-engineering` | `adversarial-testing` | `agentic-core/skills/quality-engineering/workflows/adversarial-testing.md` | `agentic-core/skills/adversarial-testing/SKILL.md` |
| `quality-engineering` | `code-review` | `agentic-core/skills/quality-engineering/workflows/code-review.md` | `agentic-core/skills/code-review/SKILL.md` |
| `quality-engineering` | `end-to-end` | `agentic-core/skills/quality-engineering/workflows/end-to-end.md` | `agentic-core/skills/end-to-end/SKILL.md` |
| `quality-engineering` | `eval-harness` | `agentic-core/skills/quality-engineering/workflows/eval-harness.md` | `agentic-core/skills/eval-harness/SKILL.md` |
| `quality-engineering` | `failure-analysis` | `agentic-core/skills/quality-engineering/workflows/failure-analysis.md` | `agentic-core/skills/failure-analysis/SKILL.md` |
| `quality-engineering` | `language-review` | `agentic-core/skills/quality-engineering/workflows/language-review.md` | `agentic-core/skills/language-review/SKILL.md` |
| `quality-engineering` | `test-design` | `agentic-core/skills/quality-engineering/workflows/test-design.md` | `agentic-core/skills/test-design/SKILL.md` |
| `quality-engineering` | `test-quality-review` | `agentic-core/skills/quality-engineering/workflows/test-quality-review.md` | `agentic-core/skills/test-quality-review/SKILL.md` |
| `research` | `code-exploration` | `agentic-core/skills/research/workflows/code-exploration.md` | `agentic-core/skills/code-exploration/SKILL.md` |
| `research` | `deep-research` | `agentic-core/skills/research/workflows/deep-research.md` | `agentic-core/skills/deep-research/SKILL.md` |
| `research` | `existing-solution-research` | `agentic-core/skills/research/workflows/existing-solution-research.md` | `agentic-core/skills/existing-solution-research/SKILL.md` |
| `research` | `github-evidence-research` | `agentic-core/skills/research/workflows/github-evidence-research.md` | `agentic-core/skills/github-evidence-research/SKILL.md` |
| `research` | `paper-research` | `agentic-core/skills/research/workflows/paper-research.md` | `agentic-core/skills/paper-research/SKILL.md` |
| `research` | `versioned-documentation-research` | `agentic-core/skills/research/workflows/versioned-documentation-research.md` | `agentic-core/skills/versioned-documentation-research/SKILL.md` |
| `security` | `database-audit` | `agentic-core/skills/security/workflows/database-audit.md` | `agentic-core/skills/database-audit/SKILL.md` |
| `security` | `security-review` | `agentic-core/skills/security/workflows/security-review.md` | `agentic-core/skills/security-review/SKILL.md` |
| `security` | `security-testing` | `agentic-core/skills/security/workflows/security-testing.md` | `agentic-core/skills/security-testing/SKILL.md` |
| `semantic-modeling` | `problem-space` | `agentic-core/skills/semantic-modeling/workflows/problem-space.md` | `agentic-core/skills/problem-space/SKILL.md` |
| `software-engineering` | `algorithm-selection` | `agentic-core/skills/software-engineering/workflows/algorithm-selection.md` | `agentic-core/skills/algorithm-selection/SKILL.md` |
| `software-engineering` | `concurrency-design` | `agentic-core/skills/software-engineering/workflows/concurrency-design.md` | `agentic-core/skills/concurrency-design/SKILL.md` |
| `software-engineering` | `frontend-patterns` | `agentic-core/skills/software-engineering/workflows/frontend-patterns.md` | `agentic-core/skills/frontend-patterns/SKILL.md` |
| `software-engineering` | `performance-profiling` | `agentic-core/skills/software-engineering/workflows/performance-profiling.md` | `agentic-core/skills/performance-profiling/SKILL.md` |
| `software-engineering` | `prototype` | `agentic-core/skills/software-engineering/workflows/prototype.md` | `agentic-core/skills/prototype/SKILL.md` |
| `software-engineering` | `refactor-cleanup` | `agentic-core/skills/software-engineering/workflows/refactor-cleanup.md` | `agentic-core/skills/refactor-cleanup/SKILL.md` |
| `software-engineering` | `representation-selection` | `agentic-core/skills/software-engineering/workflows/representation-selection.md` | `agentic-core/skills/representation-selection/SKILL.md` |
| `software-engineering` | `state-modeling` | `agentic-core/skills/software-engineering/workflows/state-modeling.md` | `agentic-core/skills/state-modeling/SKILL.md` |
| `software-engineering` | `tdd` | `agentic-core/skills/software-engineering/workflows/tdd.md` | `agentic-core/skills/tdd/SKILL.md` |

## New method added by TASK-5-06

| Domain | Skill ID | Source | Target package |
|---|---|---|---|
| `multi-harness` | `same-harness-session-coordination` | `todos/harness/codex-session-communication.md` (input; author a complete skill procedure) | `agentic-core/skills/same-harness-session-coordination/SKILL.md` |
