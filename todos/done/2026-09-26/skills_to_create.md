# Installed skill capability map

This file is an inventory and pruning guide, not a requirement to create every skill named in an old backlog. Agent `<agent-skills>` sections are the source of truth for role recommendations and admission contexts. Skills remain packaged workflows; the native `skill` tool loads a workflow and is not a generated per-skill operation.

## Role domains and conditional workflows

| Agent | Domain skills and matching internal workflows |
|---|---|
| Orchestrator | `orchestration` (`orchestrate`, `spec-driven-development`) for coordinated delivery; `context-management` (`iterative-retrieval`) only when handoffs or context limits create evidence gaps; `plugin-engineering` (`plugin-creation`, `plugin-update`) for plugin changes; `commit-message` only after an explicitly authorized, validated commit. |
| Architect | `architecture` (`architecture-design`, `api-design` for REST contracts, `domain-modeling` for agreed vocabulary and justified ADRs). |
| Challenger | `architecture` (`architectural-immune-system`) for material architecture, governance, workflow, or high-impact proposal challenges. |
| Planner | `orchestration` (`implementation-planning`) for approved, dependency-aware delivery decomposition. |
| Researcher | `research` (`code-exploration`, `deep-research`, `github-evidence-research`, `paper-research`, and `versioned-documentation-research`) according to source class and question. |
| Implementer | `software-engineering` (`tdd`; select local-design, frontend, profiling, prototype, or refactor workflows only when matched); `quality-engineering` (`test-design`) for test design; `plugin-engineering` (`create-mcp`) only for MCP server implementation; `operations` (`documentation-sync`) when assigned documentation changes; `orchestration` (`resolving-merge-conflicts`) only for an authorized active merge/rebase conflict. |
| Quality Assurance | `quality-engineering` (`adversarial-testing`, `failure-analysis`, `test-quality-review`, `end-to-end`, or `eval-harness`) according to the QA task; `security` (`security-testing`) for dynamic security testing; `software-engineering` (`performance-profiling`) for an evidenced performance issue. |
| Reviewer | `quality-engineering` (`code-review`, `test-quality-review`, `language-review`) for completed diffs and test adequacy; `security` (`security-review`, `database-audit`) only for applicable trust boundaries or database surfaces. |
| DevOps | `operations` (`delivery-operations`, `verification-loop`) for approved operational changes and validation; owns MCP hosting, configuration, packaging, and deployment, not server implementation. |

## Specialized workflows, not default role methods

- `agent-authoring`, `create-hook`, `skill-authoring`, `plugin-creation`, `create-mcp`, and `optimize-skill` are specialized `plugin-engineering` workflows, not default product-development methods. `create-mcp` is routed to Implementer for server code; DevOps owns hosting and deployment.
- `memory` and `strategic-compact` are cross-session/context utilities. They MUST NOT replace the canonical task/specification history or become a competing task-state store.

The eight Codex-origin folders were identified by their `agents/openai.yaml` files under `.github/skills/`; no root `skills/` directory existed. The host-specific `openai.yaml` and Windows `Zone.Identifier` files have been removed from those imports.

## Integrated concerns and pruning decisions

- Requirement normalization, risk routing, canonical task state, specialist handoffs, and repository lifecycle remain in `orchestrate` plus `spec-driven-development`; they are not split into speculative micro-skills.
- `codebase-design`'s useful module/interface/depth/seam/testability vocabulary and `improve-codebase-architecture`'s evidence-led hot-spot selection are integrated into `architecture-design`. Mandatory HTML/CDN reports, fixed subagent counts, absolute vocabulary bans, and brittle one-adapter rules were rejected.
- `domain-modeling` remains a distinct bounded method for agreed project terms, `CONTEXT.md` glossaries, and ADRs that pass a reversibility/surprise/tradeoff test. `architecture-design` composes it only when needed.
- `diagnosing-bugs`' high-signal reproduction, reduction, falsifiable hypotheses, and one-variable probes are integrated into QA-owned `failure-analysis`. Its implementation, production instrumentation, forced user checkpoint, and commit steps were rejected; fixes remain with Implementer or DevOps.
- `prototype` is retained only for an explicitly approved, disposable state/UI artifact; it uses fake state, a narrow smoke check, and transfers the insight rather than unreviewed code.
- `resolving-merge-conflicts` is retained for scoped file-content reconciliation in an active merge/rebase. Implementer leaves the Git operation unstaged and active; Orchestrator owns continuation, abort, and commit. The imported instruction to always resolve and commit was rejected.
- The existing `code-review` package already matched the local review contract and remains canonical; the imported host descriptor was not retained.
- Existing `tdd` is enriched with interface-level behavior testing, careful use of boundary test doubles, and independent expectations from its imported guidance. Its blanket 80% coverage requirement and a dangling routing-probe prerequisite were removed; project policy and observable acceptance determine coverage gates.
- Dependency, rollout, and validation decomposition remain inside `implementation-planning`; do not split them into narrow wrappers without a repeated, distinct workflow.
- QA uses the existing adversarial, diagnostic, security, end-to-end, performance, and evaluation methods conditionally; do not create wrapper skills that only rename a test category.
- Agent liveness is checked at returned handoffs and phase boundaries. An interrupted task left `running` becomes `unknown` until host state or fresh evidence resolves it; no periodic timer or crash hook is promised without a host-supported, validated mechanism.
- The focused research/documentation additions are `github-evidence-research`, `paper-research`, `versioned-documentation-research`, and `documentation-sync`; `deep-research` composes the first three through bounded packets and explicit returns.
- The imported `codebase-design`, `diagnosing-bugs`, and `improve-codebase-architecture` packages were removed after their useful methods were merged into canonical owners; their standalone workflow duplication was not retained.
- No distinct behavior was discarded without review: each remaining imported workflow is either already canonical, rewritten under workspace rules, or merged into an existing owner.

## Deferred

No additional package from the former aspirational list is required by the current plan. New language-specific implementation/review skills, migration subskills, dependency-management, and narrow architecture or QA wrappers remain deferred until a repeated use case demonstrates a unique owner, method, and validation contract.
