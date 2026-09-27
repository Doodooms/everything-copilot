# Legacy method-source disposition audit

- Status: body-level semantic review complete; provenance relocation/removal and independent QA remain open.
- Scope: the 33 `method-source.md` files still under `agentic-core/skills/**/references/` after the workflow migration, plus disposition tracking for the 10 removed source wrappers from the original 43-file inventory.
- Current runtime shape: 11 discoverable domain `SKILL.md` entrypoints and 59 nested workflow subskills; no workflow peer packages.
- Current authority: the latest user clarification, `architecture-skill-topology-r6.md`, and `plan-r10.md`. These legacy files and the peer destination map are not runtime routes.

## One-to-one workflow counterparts

The following 27 source files have a same-ID current workflow. Each source procedure was compared with its current workflow body and relevant parent route; material changes and preserved boundaries are summarized below and in the review-coverage table. Independent QA is still required before moving or removing provenance files.

| Domain | Legacy method source | Current nested workflow |
|---|---|---|
| architecture | `architecture/references/architecture-design/method-source.md` | `architecture/workflows/architecture-design.md` |
| context-management | `context-management/references/token-optimization/method-source.md` | `context-management/workflows/token-optimization.md` |
| orchestration | `orchestration/references/commit-message/method-source.md` | `orchestration/workflows/commit-message.md` |
| orchestration | `orchestration/references/implementation-planning/method-source.md` | `orchestration/workflows/implementation-planning.md` |
| orchestration | `orchestration/references/orchestrate/method-source.md` | `orchestration/workflows/orchestrate.md` |
| orchestration | `orchestration/references/resolving-merge-conflicts/method-source.md` | `orchestration/workflows/resolving-merge-conflicts.md` |
| orchestration | `orchestration/references/spec-driven-development/method-source.md` | `orchestration/workflows/spec-driven-development.md` |
| plugin-engineering | `plugin-engineering/references/create-hook/method-source.md` | `plugin-engineering/workflows/create-hook.md` |
| plugin-engineering | `plugin-engineering/references/optimize-skill/method-source.md` | `plugin-engineering/workflows/optimize-skill.md` |
| quality-engineering | `quality-engineering/references/adversarial-testing/method-source.md` | `quality-engineering/workflows/adversarial-testing.md` |
| quality-engineering | `quality-engineering/references/code-review/method-source.md` | `quality-engineering/workflows/code-review.md` |
| quality-engineering | `quality-engineering/references/eval-harness/method-source.md` | `quality-engineering/workflows/eval-harness.md` |
| quality-engineering | `quality-engineering/references/failure-analysis/method-source.md` | `quality-engineering/workflows/failure-analysis.md` |
| quality-engineering | `quality-engineering/references/language-review/method-source.md` | `quality-engineering/workflows/language-review.md` |
| research | `research/references/code-exploration/method-source.md` | `research/workflows/code-exploration.md` |
| research | `research/references/deep-research/method-source.md` | `research/workflows/deep-research.md` |
| research | `research/references/github-evidence-research/method-source.md` | `research/workflows/github-evidence-research.md` |
| research | `research/references/paper-research/method-source.md` | `research/workflows/paper-research.md` |
| research | `research/references/versioned-documentation-research/method-source.md` | `research/workflows/versioned-documentation-research.md` |
| security | `security/references/database-audit/method-source.md` | `security/workflows/database-audit.md` |
| security | `security/references/security-review/method-source.md` | `security/workflows/security-review.md` |
| security | `security/references/security-testing/method-source.md` | `security/workflows/security-testing.md` |
| software-engineering | `software-engineering/references/frontend-patterns/method-source.md` | `software-engineering/workflows/frontend-patterns.md` |
| software-engineering | `software-engineering/references/performance-profiling/method-source.md` | `software-engineering/workflows/performance-profiling.md` |
| software-engineering | `software-engineering/references/prototype/method-source.md` | `software-engineering/workflows/prototype.md` |
| software-engineering | `software-engineering/references/refactor-cleanup/method-source.md` | `software-engineering/workflows/refactor-cleanup.md` |
| software-engineering | `software-engineering/references/tdd/method-source.md` | `software-engineering/workflows/tdd.md` |

### Materially changed one-to-one procedures

- `orchestration/spec-driven-development`: retains the four-stage specification/solution/evidence/convergence lifecycle, while replacing fixed choreography with gate selection, material semantic modeling, staleness handling, and bounded handoffs. The selected `required_gates` policy is supported by the cost-eval-opt request for risk-proportional routing; the validator and convergence contract still require QA whenever Review is selected. The workflow and references were reviewed against the legacy source.
- `plugin-engineering/create-hook`: reviewed one-to-one. It replaces the source's frozen VS Code hook schema with a target-host/version check and requires current official event, input/output, and command-contract verification. This matches the current VS Code docs, which distinguish Local, Copilot, and Codex hook implementations; a regression test guards the host boundary.
- `quality-engineering/eval-harness`: deliberately drops arbitrary fixed pass@k targets from the source. It now requires a model-call/retry ceiling enforceable before invocation, durable per-trial evidence, and `unknown` for unreported values.
- `software-engineering/frontend-patterns`: replaces generic, version-agnostic code recipes with package/router inspection, current React/Next.js boundaries, official version-matched docs, semantic UI behavior, and measured performance changes. No generic code snippets are copied forward as authoritative patterns.
- `security/security-review`: retains the source checklist topics and separates evidence classification, finding severity, and acceptance ownership. Reviewed one-to-one. The source's CORS reminder was absent; a contextual CORS section now distinguishes public non-credentialed wildcard access from credentialed/sensitive access, requires explicit trusted origins and cache variance for dynamic allowlists, and preserves authorization/CSRF boundaries. Independent QA remains open.

## One-to-many workflow counterparts

These six former domain methods now map to several selected subskills. The source method's old admission and routing are owned by the parent domain; procedures are owned by the listed subskills.

| Legacy method source | Current domain/subskills | Preserved boundary |
|---|---|---|
| `architecture/references/domain-modeling/method-source.md` | `semantic-modeling/problem-space` | Reviewed. Project meaning and unresolved user choices stay separate from architecture; canonical semantics live in `SPEC.semantic_model`, with approved glossary/ADR material as supporting views. The legacy ADR decision criteria are now explicit in the parent skill and selected workflow. |
| `plugin-engineering/references/create-agent/method-source.md` | `plugin-engineering/agent-authoring`, `plugin-engineering/agent-validation` | Reviewed. Creation/repair and validate-only review are separate procedures; exact tool/recipient validation and source-owned role contracts remain in the selected workflow and its listed references. |
| `plugin-engineering/references/create-plugin/method-source.md` | `plugin-engineering/plugin-creation`, `plugin-engineering/plugin-update` | Reviewed. New-pack scaffold/composition and existing-pack repair are distinct; canonical CLI, per-target validation/build, and the no-install/no-commit boundary remain explicit. |
| `plugin-engineering/references/create-skill/method-source.md` | `plugin-engineering/skill-authoring`, `plugin-engineering/skill-maintenance` | Reviewed. New package creation and existing-package maintenance are distinct; parent-owned admission and the user-approved immediate-workflow topology supersede the source's reference-directory subskill layout. |
| `quality-engineering/references/testing/method-source.md` | `quality-engineering/test-design`, `quality-engineering/end-to-end`, `quality-engineering/test-quality-review` | Reviewed. Test design, full user journeys, and existing-suite review remain distinct from TDD, independent QA falsification, diagnosis, and security testing. |
| `software-engineering/references/implementation-design/method-source.md` | `software-engineering/algorithm-selection`, `representation-selection`, `state-modeling`, `concurrency-design` | Reviewed. Local design choices are selected by the kind of constraint; system architecture, domain meaning, test-first implementation, and performance diagnosis remain separate owners. |

## Removed source wrappers

These 10 legacy wrappers are no longer in the active plugin tree. Their prior bodies remain available from the Git baseline for provenance; the current workflows own the procedures. Six were reconciled in earlier source-review evidence, and four Operations wrappers were compared against their current routes in this audit. The remaining content review and independent QA below concern the 33 source files still in the tree.

| Removed source | Current owner | Disposition evidence |
|---|---|---|
| `architecture/references/api-design/method-source.md` | `architecture/workflows/api-design.md` + `references/api-design/api-design-patterns.md` | `EVIDENCE-API-DESIGN-WORKFLOW-REFERENCE-R1`; workflow and point-of-need patterns are checked. |
| `architecture/references/architectural-immune-system/method-source.md` | `architecture/workflows/architectural-immune-system.md` + `references/architectural-immune-system/lenses-and-report.md` | `EVIDENCE-AIS-WORKFLOW-RECONCILIATION-R1`; seven lenses and report contract are checked. |
| `context-management/references/iterative-retrieval/method-source.md` | `context-management/workflows/iterative-retrieval.md` | `EVIDENCE-CONTEXT-WORKFLOW-RECONCILIATION-20260927-R1`; bounded-retrieval checks. |
| `context-management/references/memory/method-source.md` | `context-management/workflows/memory.md` | `EVIDENCE-CONTEXT-WORKFLOW-RECONCILIATION-20260927-R1`; memory-safety checks. |
| `context-management/references/strategic-compact/method-source.md` | `context-management/workflows/strategic-compact.md` | `EVIDENCE-CONTEXT-WORKFLOW-RECONCILIATION-20260927-R1`; compact/host-boundary checks. |
| `plugin-engineering/references/create-mcp/method-source.md` | `plugin-engineering/workflows/{create-mcp,create-mcp-rust}.md` + `references/create-mcp/common-transport-security.md` | `EVIDENCE-MCP-COMPLEMENTARY-WORKFLOWS-20260927-R1`; both workflows and shared guidance validate. |
| `operations/references/delivery-operations/method-source.md` | `operations/workflows/delivery-operations.md` | Reviewed against Git baseline; approval/environment boundary, rollback/monitoring return, and runtime-evidence limits are retained. |
| `operations/references/documentation-sync/method-source.md` | `operations/workflows/documentation-sync.md` | Reviewed against Git baseline; plan-assigned scope, verified-behavior boundary, and unsupported-claim blocker are retained. |
| `operations/references/install-agent-plugin/method-source.md` | `operations/workflows/install-agent-plugin.md` | Reviewed against Git baseline; trusted-source approval and installed/active/loaded state separation are retained. |
| `operations/references/verification-loop/method-source.md` | `operations/workflows/verification-loop.md` | Reviewed against Git baseline; applicable-gate evidence and `READY`/`NOT READY` criteria are retained; benchmark-only routing sentinel remains removed. |

## Disposition decision

The body-level semantic comparison is complete for all 33 current method sources: all 27 one-to-one counterparts and all six one-to-many mappings are reviewed. The 33 files are provenance-bearing originals, not generated scratch files. Keep them for now; do not move or delete them before independent QA confirms the retained procedures and provenance/attribution needs. The linter's 33 orphaned `method-source.md` warnings therefore remain visible and acknowledged. After QA, move them to a non-runtime history location or remove them only when provenance and retained content are accounted for. Do not treat lexical similarity as acceptance evidence.

### One-to-one review coverage

| Domain | Reviewed counterparts | Source disposition |
|---|---|---|
| architecture | `architecture-design` | Evidence → design comparison → architecture brief is retained. Domain terminology/ADR decisions now route through `semantic-modeling`; the legacy ADR criteria are explicit in the parent and selected workflow. |
| context-management | `token-optimization` | Local, target-aware projection and approximate counts remain; generic references stay excluded, budgets remain advisory, and live session context has a separate `multi-harness` route. |
| orchestration | `commit-message`, `implementation-planning`, `orchestrate`, `resolving-merge-conflicts`, `spec-driven-development` | Factual commit summaries, task DAG, manifest/event transitions, bounded conflict resolution, risk-selected gates, and handoff/convergence contracts remain. New research routing in `orchestrate` is limited to material build-versus-reuse decisions. |
| plugin-engineering | `create-hook`, `optimize-skill` | Hook event/input/output checks are host/version scoped; optimization keeps the benchmark lock, S0/S* lineage, hidden holdout, structural gates, and report. Target-specific paths and inherited-risk handling are updated. |
| quality-engineering | `adversarial-testing`, `code-review`, `eval-harness`, `failure-analysis`, `language-review` | Independent falsification, severity-ordered findings, evidence-based diagnosis, and language-specific review are retained. `eval-harness` deliberately adds enforceable pre-call budgets, versioned definitions/fixtures/baselines, machine-readable trial artifacts, and `unknown` for unreported values; stale fixed pass@k targets and Markdown-only storage are not carried forward. |
| research | `code-exploration`, `deep-research`, `github-evidence-research`, `paper-research`, `versioned-documentation-research` | Bounded entry-point tracing, finite source composition, pinned GitHub revisions, claim-level paper evidence, and version-matched docs remain. GitHub MCP access boundaries and Context7 source traceability are added at their point of use. |
| security | `database-audit`, `security-review`, `security-testing` | Database integrity/privilege/transaction checks, the security finding rubric, and bounded attacker-driven QA remain. The missing CORS controls are restored in the separately documented security-review reconciliation. |
| software-engineering | `frontend-patterns`, `performance-profiling`, `prototype`, `refactor-cleanup`, `tdd` | TDD gates, measured hotspot analysis, disposable-prototype boundaries, and behavior-preserving cleanup are retained. `frontend-patterns` intentionally replaces generic version-agnostic code recipes with installed-version/router inspection, semantic UI state/accessibility checks, official framework guidance, and measured optimization. |

`frontend-patterns` was checked against official current React and Next.js documentation through Context7. The reviewed guidance supports event-specific work in event handlers, Effects for external-system synchronization, App Router server/client boundaries, and direct source reads from Server Components.

## Source review progress

- `architecture/references/domain-modeling/method-source.md` → `semantic-modeling/SKILL.md` + `semantic-modeling/workflows/problem-space.md`: the canonical `SPEC.semantic_model`, authorization boundary, glossary support, and all three legacy ADR criteria are explicit. This closes the sixth one-to-many review.
- `security/references/security-review/method-source.md`: all 10 core categories and evidence/ownership changes are retained; the missing CORS check was restored with trusted-origin, credential, cache-variance, authorization, and CSRF boundaries. A regression assertion and package validation pass.
- `orchestration/references/spec-driven-development/method-source.md`: risk-proportional selected gates are grounded in the cost-eval-opt request; handoff/convergence references preserve revision, status, evidence, ownership, and resume point, and require QA whenever Review is selected.
- `plugin-engineering/references/create-hook/method-source.md`: reviewed against current official VS Code hook docs; target host/version, event/input/output, timeout/failure behavior, and real lifecycle validation replace the source's frozen universal schema assumption.
- The four removed Operations wrappers were compared with their Git baseline, parent route, and current workflow. Their authorization, evidence, documentation, and readiness boundaries are recorded above and guarded by focused tests.
- All six one-to-many and all 27 one-to-one source mappings are reviewed. Procedure-semantic review is complete; provenance relocation/removal and independent QA/Reviewer acceptance remain open. The focused 25-test suite passes; the quality-engineering validator passes with known provenance/support warnings.
