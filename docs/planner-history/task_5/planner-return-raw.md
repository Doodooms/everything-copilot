Message Type: FINAL_ANSWER
Task name: /root
Sender: /root/workflow_skill_plan
Payload:
> **SUPERSEDED by plan r10 and architecture r6.** Historical planner return only; its peer-package migration proposal is not the current topology.

## Planner handoff — TASK-5-03

- **Status:** `success`
- **Agent:** `planner`
- **Specification:** `SPEC-AGENTIC-CORE-NORMALIZATION@1`
- **Specification revision:** 1
- **Architecture:** `architecture-skill-topology`, revision 1; consumed decisions `ADR-ACN-001` and `ADR-ACN-002`
- **Current plan:** `plan-r3.md`, revision 3
- **Assigned risk:** `L2` (preserved)
- **Base revision:** `5c6dcd401e9a0d115e79c19f02de96ffed694686`
- **Objective:** Complete the routed-method peer-skill migration, MCP skill composition, and safe same-harness coordination method without changing scope or acceptance criteria.
- **Scope:** `TASK-5-03`, `TASK-5-05`, `TASK-5-06`; preserve completed `TASK-5-01`, `TASK-5-02`, and `TASK-5-04`.

### Findings and evidence

The current checkout has **57** routed method files, each with a non-empty stable `id`. The approved architecture directs each to `agentic-core/skills/<id>/SKILL.md`, with a complete method procedure and package contract. The 11 domain skills remain the organization and first disclosure layer; the selected peer skill is the second. `agentic-core/plugin.json` already points to the root skill collection, and the controller materializes immediate child directories containing `SKILL.md`. The architecture record documents the Codex and Copilot direct-child discovery assumption.

The current tests enforce the old topology: `test_only_domain_skills_are_discoverable_and_workflows_are_immediate` expects only domain skills and validates methods under `workflows/`. Domain `SKILL.md` files route using relative links to those workflow files. The linter in `agentic-core/skills/plugin-engineering/references/create-skill/scripts/skill_lint_core.py` parses and validates `workflows/`, including IDs, links and support references, then checks domain routing links point to immediate workflow children. Its scaffold, validation guidance, and tests encode the same assumptions and need updating. `agentic-core/runtime/pluginctl/controller.py` discovers immediate skill directories with `SKILL.md` and collects their support files; no second converter is indicated.

Many methods link to support files under their current domain package, such as `../references/.../assets`, `references`, and `scripts`. Those paths will not resolve from peer package roots. Move or compose each consumed support file into the destination package and update links/metadata; keep shared material single-source only where the package contract explicitly supports composition. There are **43** `references/*/method-source.md` files in the current tree; inventory their consumers and provenance before removal or retention to avoid duplicate editable procedures or breaking links.

Current MCP guidance lives in `plugin-engineering/workflows/create-mcp.md`, `create-mcp-rust.md`, and `references/create-mcp/{assets,references,scripts}`. The general workflow covers language/transport selection and common MCP references; the Rust workflow covers version-pinned `rmcp`, typed inputs, features, lifecycle, and performance constraints. Keep shared transport/security guidance in one canonical support location with explicit references from both skills, and keep Rust-specific constraints only in the Rust skill.

Same-harness coordination belongs in the existing `multi-harness` domain, alongside its cross-harness workflows. Add a peer method with boundaries for read-only status observation, explicit user authorization before contact, queue acceptance versus actual consumption/reply, and bounded handoff/resume. A shared artifact is evidence of its contents only, not proof another session received or consumed it. No message should be sent or queued by this work.

**Dirty worktree:** `git status --short` shows numerous existing modified, deleted, and untracked files, including plugin sources and `docs/`. Implementation owners must preserve them and avoid broad cleanup.

### Stable method ID → destination

Destination for each ID below is `agentic-core/skills/<ID>/SKILL.md`.

| Domain | IDs (each maps to the destination above) |
|---|---|
| `architecture` | `api-design`, `architectural-immune-system`, `architecture-design` |
| `context-management` | `iterative-retrieval`, `memory`, `strategic-compact`, `token-optimization` |
| `multi-harness` | `codex`, `copilot`, `harness-distribution`, `smart-compact` |
| `operations` | `delivery-operations`, `documentation-sync`, `install-agent-plugin`, `verification-loop` |
| `orchestration` | `commit-message`, `implementation-planning`, `orchestrate`, `resolving-merge-conflicts`, `spec-driven-development` |
| `plugin-engineering` | `agent-authoring`, `agent-validation`, `create-hook`, `create-mcp`, `create-mcp-rust`, `optimize-skill`, `plugin-creation`, `plugin-update`, `skill-authoring`, `skill-maintenance` |
| `quality-engineering` | `adversarial-testing`, `code-review`, `end-to-end`, `eval-harness`, `failure-analysis`, `language-review`, `test-design`, `test-quality-review` |
| `research` | `code-exploration`, `deep-research`, `existing-solution-research`, `github-evidence-research`, `paper-research`, `versioned-documentation-research` |
| `security` | `database-audit`, `security-review`, `security-testing` |
| `semantic-modeling` | `problem-space` |
| `software-engineering` | `algorithm-selection`, `concurrency-design`, `frontend-patterns`, `performance-profiling`, `prototype`, `refactor-cleanup`, `representation-selection`, `state-modeling`, `tdd` |

## Proposed task graph

Owners below are proposed delivery owners; the Orchestrator should assign them in canonical task state. Validation commands are proposed commands, not runs performed by this Planner.

| ID / objective | Owner; allowed scope | Inputs and dependencies | Output and validation | Exit criterion |
|---|---|---|---|---|
| `TASK-5-03A` Convert 57 routed methods into peer skill packages; reconcile support paths | Implementer; `agentic-core/skills/**`, with each method’s source/destination and consumed support files bounded to its domain and destination packages | SPEC-1 AC-1; ADR-ACN-001/002; current 57 method files and support paths; depends on `TASK-5-02` (complete) | 57 complete `SKILL.md` packages and package-local consumed support paths; validate each package with `PYTHONDONTWRITEBYTECODE=1 python agentic-core/skills/plugin-engineering/references/create-skill/scripts/validate.py --skill-dir <dir>` | Every ID has exactly one peer package; methods contain their procedure, references resolve within package, no duplicate editable source remains |
| `TASK-5-03B` Update domain routers and agent skill references to two-step method loading | Implementer; 11 domain `SKILL.md` files and affected agent skill references under `agentic-core/` | `TASK-5-03A`; ADR-ACN-001/002 | Domain routers point to stable peer skill IDs using supported host loading; update applicable routing tests | All route edges resolve; method does not route onward; domain then method disclosure remains clear |
| `TASK-5-03C` Redesign skill linter, templates/guidance, source inventory tests | Implementer; linter and related create-skill assets/guidance under `agentic-core/skills/plugin-engineering/references/create-skill/`; `tests/test_agentic_core_sources.py` | `TASK-5-03A` package contract; `TASK-5-03B` route shape | Validate complete peer packages, ID uniqueness, local references, and route edges; replace “domain-only discovery” assertions. Run `uv run pytest tests/test_agentic_core_sources.py` and the package validator across domain and method packages | Tests assert peer inventory and route coverage, and no longer require methods remain nested or undiscoverable |
| `TASK-5-05A` Compose complementary MCP skills with shared common guidance | Implementer; `agentic-core/skills/plugin-engineering/{SKILL.md,references/create-mcp/**,workflows/create-mcp.md,workflows/create-mcp-rust.md}` during transition, then peer destinations established by `TASK-5-03A` | `TASK-5-03A`; SPEC-1 AC-2 | Shared common transport/security guidance remains one canonical file with explicit references; `create-mcp-rust` retains only Rust/`rmcp` specialization. Validate both skill packages and run relevant source tests | Both packages pass validation, no copied procedure remains, Rust constraints are present |
| `TASK-5-06A` Add same-harness coordination method and route | Implementer; `agentic-core/skills/multi-harness/**` and source routing tests, then the new peer skill package after `TASK-5-03A` | `TASK-5-03A`; SPEC-1 AC-4 | Add method covering observation, authorization, queue/receipt/consumption/reply distinction, bounded handoff/resume; no external contact. Validate package and route tests | Required distinctions are explicit, route resolves, and no sending or queueing operation is performed |
| `TASK-5-03D` Independent migration QA and final review | QA, then Reviewer; read-only review of the above diff and test evidence | `TASK-5-03A/B/C`, `TASK-5-05A`, `TASK-5-06A` | QA checks inventory completeness, broken/escaping links, duplicate sources, domain routes and package validation. Reviewer checks AC trace, architecture conformance and residual risks | QA returns falsifiable evidence; Reviewer records acceptance or actionable findings |

### Phases and dependency edges

1. **Peer migration:** `03A → 03B → 03C`. `03A` and initial source-test updates may be developed in parallel only if ownership is split by file and integrated before validation.
2. **MCP and session guidance:** `05A` and `06A` depend on `03A` to place final content in peer packages. They can proceed in parallel with each other after `03A`.
3. **Independent gates:** `03D` follows all implementation tasks.

Edges: `TASK-5-02 → TASK-5-03A → TASK-5-03B → TASK-5-03C → TASK-5-03D`; `TASK-5-03A → TASK-5-05A → TASK-5-03D`; `TASK-5-03A → TASK-5-06A → TASK-5-03D`. The later `TASK-5-07` in plan r3 remains dependent on `TASK-5-03`, `TASK-5-04`, `TASK-5-05`, and `TASK-5-06`; `TASK-5-08` remains after `TASK-5-07`.

**File ownership:** avoid concurrent edits to shared domain routers, shared linter, and shared source tests. Assign one Implementer ownership for `skill_lint_core.py` and test inventory changes; method-package content can be split by disjoint IDs. Assign MCP and session method content to separate owners only after peer package roots are established. QA and Reviewer are read-only.

### Validation, compatibility, rollback

- Package validation: `PYTHONDONTWRITEBYTECODE=1 python agentic-core/skills/plugin-engineering/references/create-skill/scripts/validate.py --skill-dir <skill-dir>` for all 11 domain and 57 method packages.
- Source tests: `uv run pytest tests/test_agentic_core_sources.py`.
- Lint changes using the repository’s configured Ruff command for modified Python files; confirm its exact project command before execution.
- Migration completeness check: enumerate immediate `skills/*/SKILL.md`, compare with the expected 11 domains + 57 methods; test every router ID and all local metadata/Markdown/#file references.
- Host discoverability follows as `TASK-5-07`: after approved package version/cache refresh, compare native Copilot skill inventory and a fresh Codex process against the 68 expected IDs. This Planner did not run host operations.
- Compatibility: keep package IDs stable; no duplicate `.github/skills` editable projection; ensure profiles/materializers continue recognizing each immediate child package. Treat existing task ledgers and completed task artifacts as preserved.
- Rollback: retain the pre-migration source revision and restore the prior tree if migration validation fails; do not remove old method sources until package and route checks pass. Rollback is an Orchestrator/authorized Git lifecycle decision; this plan does not authorize Git actions.

### Acceptance-criteria ownership

- **AC-1 / REQ-1:** `03A`, `03B`, `03C`, independently checked by `03D`.
- **AC-2 / REQ-2:** `05A`, validated by `03D`.
- **AC-4 / REQ-4:** `06A`, validated by `03D`.
- **AC-3 / REQ-3:** already owned by completed `TASK-5-04`; plan r3 records the cleanup evidence. No new work proposed here.
- **AC-5 / REQ-5:** already owned by completed `TASK-5-01`; final dual-host/cache verification remains with `TASK-5-07`.
- **AC-6 / REQ-6:** outside this handoff’s implementation scope; remains with `TASK-5-08` after host verification. `task_3` ownership constraint stands.

### Risks, assumptions, gaps, and skipped work

- **Risk:** moving procedures can invalidate package-relative links and `#file:` references; package support must move with the owning method or have deliberate composition.
- **Risk:** old fixtures and architecture-era tests encode the 11-skill topology; updating only the linter or only tests leaves contradictory contracts.
- **Assumption:** existing non-empty workflow IDs are suitable stable package names as ADR-ACN-001 states.
- **Assumption:** current host inventory/cache refresh remains assigned to `TASK-5-07`.
- **Blockers/gaps:** none identified that prevent producing this plan. Revisit to the Orchestrator if implementers discover a missing method ID or product-semantic conflict; route package topology contradictions to Architect.
- **Skipped:** native todo updates, because this session exposes no todo tool; no task artifact was created. No repository tests, host operations, external research, credential inspection, Copilot runtime, `task_3`/`harness_factory` changes, Git lifecycle actions, or inter-session messages were performed. None were needed to produce this plan; downstream validation and host verification are assigned above.
- **Changed files:** `[]`
- **Commit SHAs:** `[]`
- **No files changed:** confirmed; inspection was read-only. Existing dirty worktree state was observed and left untouched.
- **Suggested next owner:** root Orchestrator to reconcile this proposed task graph with canonical task state and approve bounded Implementer handoffs; then Implementer owns `TASK-5-03A` first.
