## Planner handoff — TASK-5-03

> **SUPERSEDED by plan r10 and architecture r6.** Preserve this as historical handoff data; do not implement any peer-package topology described by old planning artifacts.

**Status:** The Planner returned `success`. It preserved the assigned **L2** risk and inspected the checkout read-only. No files changed.

- Specification: `SPEC-AGENTIC-CORE-NORMALIZATION@1`, revision 1
- Architecture: `architecture-skill-topology`, revision 1; decisions `ADR-ACN-001` and `ADR-ACN-002`
- Current plan: `plan-r3.md`, revision 3
- Base revision: `5c6dcd401e9a0d115e79c19f02de96ffed694686`
- Handoff packet: [TASK-5-03-planner.md](/home/pm/projets-persos/agentic-workflow/docs/harness-history/task_5/handoffs/TASK-5-03-planner.md)

### Findings

The Planner found 57 routed methods with non-empty stable IDs. The proposed destination for each is `agentic-core/skills/<id>/SKILL.md`. The 11 domain skills remain the first disclosure layer; the method peer skill becomes the second. Plugin metadata and the controller’s immediate-child discovery support this layout, while current source tests, routers, and `skill_lint_core.py` still encode the old workflow layout.

Moving methods will require handling package-relative links and support assets. The Planner found 43 `references/*/method-source.md` files and recommends inventorying their consumers and provenance before changing or removing them.

For MCP guidance, it recommends keeping common transport and security material in one referenced location, with Rust and `rmcp` constraints in `create-mcp-rust`. Same-harness coordination belongs with `multi-harness` and should distinguish observed status, authorization, queue acceptance, actual consumption or reply, and bounded handoff/resume. No message was sent or queued.

The worktree contains existing modified and untracked files. The Planner recommends preserving them.

### Proposed task graph

| Task | Owner and scope | Dependency and exit check |
|---|---|---|
| `TASK-5-03A` — Create the 57 peer packages and handle consumed support paths | Implementer; bounded to method packages and their source/destination support files | Depends on completed `TASK-5-02`. Every ID has one complete package and its references resolve. |
| `TASK-5-03B` — Update domain routers and agent skill references | Implementer; domain `SKILL.md` files and affected agent references | After 03A. Routes resolve through the two disclosure layers. |
| `TASK-5-03C` — Update linter, guidance, templates, and source tests | Implementer; create-skill assets and `tests/test_agentic_core_sources.py` | After 03A/03B. Tests cover peer inventory, uniqueness, references, and routes. |
| `TASK-5-05A` — Compose the MCP skills | Implementer; MCP guidance and resulting peer packages | After 03A. Common guidance is shared by reference; Rust constraints remain present. |
| `TASK-5-06A` — Add and route same-harness coordination | Implementer; `multi-harness` guidance, peer package, and routing tests | After 03A. Required status/authorization/consumption distinctions are explicit; no contact occurs. |
| `TASK-5-03D` — Independent QA, then Reviewer gate | QA and Reviewer; read-only | After all implementation tasks. QA provides falsifiable evidence; Reviewer checks acceptance criteria, architecture, and residual risks. |

The proposed sequence is `03A → 03B → 03C`, followed by `03D`. Tasks `05A` and `06A` can proceed in parallel after `03A`. Completed tasks `5-01`, `5-02`, and `5-04` are preserved. The Planner assigns AC-1 to 03A/B/C, AC-2 to 05A, AC-4 to 06A, and leaves AC-3 with completed 5-04, AC-5 with completed 5-01 and later 5-07 verification, and AC-6 with 5-08.

### Validation and rollback

The proposed checks are package validation for all 68 packages, `uv run pytest tests/test_agentic_core_sources.py`, Ruff on modified Python files, and inventory/link/route checks. Dual-host discovery remains with `TASK-5-07`. The rollback plan is to preserve the pre-migration revision and retain old method sources until package and route checks pass; Git actions remain an Orchestrator authorization decision.

### Coverage gap and skipped work

The handoff lists all 57 IDs by domain and gives their destination pattern, but does not provide an individual source-file path for each method. It describes link and asset relocation patterns rather than enumerating them per method. The Planner reported no blockers to producing the plan, so these are gaps in the requested inventory detail.

Native todo updates were skipped because no todo tool was available. Tests, host operations, external research, and Git lifecycle actions were not performed. The proposed next owner is the root Orchestrator to reconcile and approve bounded implementation handoffs, beginning with `TASK-5-03A`.
