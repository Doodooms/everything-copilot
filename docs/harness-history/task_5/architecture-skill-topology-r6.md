# Agentic Core skill and subskill topology

- Revision: 6; preserves the nested package topology from r5 and clarifies the content structure required inside each workflow subskill.
- Specification: `SPEC-AGENTIC-CORE-NORMALIZATION@2`.
- Requirements: `REQ-1`.
- Acceptance criteria: `AC-1`.
- Risk: `L2`.
- Decision authority: the user's clarification on 2026-09-27.
- Status: adopted for current implementation.

## ADR-ACN-001 — Domain package owns structured subdomain expertise

Keep the 11 domain expertise packages as the only discoverable Agent Skill packages under `agentic-core/skills/<domain>/SKILL.md`. Each domain owns its subdomain expertise as `agentic-core/skills/<domain>/workflows/<id>.md`.

Each nested subskill uses the canonical skill **content structure**: `<critical_rules>`, `<general_rules>`, `<risk_assessment>`, `<rules>`, and `<workflow>` in that order. The `<workflow>` block contains the complete, specialized procedure. Workflow frontmatter keeps `id`, `description`, `invoke_for`, `avoid_for`, and `references`; it does not gain Agent Skill package identity such as a peer `SKILL.md`, `user-invocable`, or a separate global routing entry.

The parent domain `SKILL.md` owns discoverability and first-stage routing. It loads only the relevant workflow subskill, which supplies the second-stage subdomain expertise and execution procedure. This preserves progressive disclosure: domain → selected subskill. The subskill's critical/general/risk/rules blocks express only its local scope, constraints, inherited risk handling, and output contract; they do not duplicate global admission or broaden authority.

Do not create peer `skills/<id>/SKILL.md` packages for workflows, a third taxonomy level, or a flat list of 59 globally routed skills.

## Evidence and implementation constraints

- The user clarified that “same structure as a skill” means the same canonical body sections, not a standalone Agent Skill package. This clarification supersedes the earlier interpretation that only the workflow metadata and stepwise procedure needed to match.
- Update `agentic-core/skills/plugin-engineering/references/create-skill/assets/workflow-template.md` to encode the required nested-subskill structure.
- Extend the workflow-specific validator and tests to check the canonical section order, inherited risk contract, complete procedure, metadata, and reference containment without applying standalone-skill package validation to nested subskills.
- Inventory exactly 11 domain entrypoints and 59 nested subskills. Verify no workflow gained a peer package and each parent router exposes only its relevant procedures.
- Keep references as supporting knowledge; do not hide the actual procedure in `references/` or create another method-source layer.

## Supersession and limits

This decision defines package topology and authored structure. It does not establish that all 59 procedure bodies preserve their source semantics or that host projections load workflow links correctly; those still require focused implementation, QA, and fresh host verification.
