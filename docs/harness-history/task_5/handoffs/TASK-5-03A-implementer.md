# Implementer handoff — TASK-5-03A

> **SUPERSEDED.** This handoff asks for 57 peer skill packages, which is the mistaken topology. Do not execute it; use plan r10 and architecture r6 for nested workflow subskills and their canonical body structure.

- Parent task: `task_5`
- Task: `TASK-5-03A`
- Attempt: `peer-skill-packages-implementer-1`
- Assigned role: plugin `implementer`
- Risk: `L2` (already assigned; do not downgrade)
- Specification: `SPEC-AGENTIC-CORE-NORMALIZATION@1`, revision 1
- Architecture: `architecture-skill-topology-r3.md`, revision 3; decisions `ADR-ACN-001`–`ADR-ACN-004`
- Approved plan: `docs/planner-history/task_5/plan-r7.md`, revision 7
- Source map: `docs/planner-history/task_5/workflow-skill-source-map.md` (57 existing IDs and source paths)

## Request

Convert all 57 routed workflow methods into complete peer skill packages at `agentic-core/skills/<skill-id>/SKILL.md`. This is package creation only; domain routers, source workflow deletion, linter, templates, and tests belong to later tasks.

For each method:

1. Preserve its complete procedure and stable ID as the skill name. Use host-compatible `name` and `description` frontmatter; preserve `invoke_for`/`avoid_for` meaning in the skill description or body, not unsupported custom frontmatter. Do not drop required steps or lower risk/authorization rules.
2. Add explicit, bounded `## Skill relationships` body tables where relevant. Use ADR-ACN-004 edge types `compose` (execution), `read` (context only), and `support` (file resource); domain `route` tables are TASK-5-03B. Preserve existing method compositions such as `create-mcp` → `create-mcp-rust`, bounded research composition, conditional orchestration procedures, and reciprocal paired reads. Do not infer an execution edge from an ordinary Markdown link.
3. Inventory each method's support paths and consumers. Move/create method-specific support inside that method's package and rewrite links. For content shared across methods, do not add broad sibling-package paths or duplicate procedures; report exact consumers/paths for an Orchestrator decision. Preserve provenance sources until their consumers are known.
4. Preserve the existing workflow source files and references during this task as a migration checkpoint. TASK-5-03B will switch routers and retire obsolete workflow duplicates after package contents are reconciled. Do not refresh/install either host during this task.

## Allowed scope

- Create `agentic-core/skills/<id>/SKILL.md` for the 57 entries in the source map.
- Add/move support files only when they are method-specific and their consumers/provenance are verified; limit moves to the corresponding source domain references and target peer package.
- Add or update the focused handoff/evidence artifact for shared support-path questions.

Do not edit domain `SKILL.md` routers, the create-skill linter/templates/tests, `plugin.json`, `mcp.json`, `runtime/mcp`, Codex projection code, `task_3`, `harness_factory`, or unrelated dirty files. Do not stage, commit, reset, clean, contact sessions, inspect credentials, or use Copilot runtime.

## Validation and return

- Run focused content/link/inventory checks with the repository's existing validator where it applies; do not rewrite the linter in this task.
- Confirm exactly 57 new peer packages exist, one per mapped ID, and report remaining source links/support paths that require TASK-5-03B/C or a design decision.
- Use `uv` for Python commands; use Ruff for any Python edits (expected none).
- Return status, IDs/revisions consumed, exact changed files, validation commands/results, preserved composition edges, unresolved support owners, rollback/reversibility, and next owner. No Git commit is authorized.
