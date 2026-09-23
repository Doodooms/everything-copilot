# Original Specification

## Raw intent

Create and maintain a production-ready skill authoring workflow that follows the selected `phase-0b-inline-grouped-lists` architecture, favors structured lists over Markdown tables for procedural guidance, and keeps the user in the review loop before the skill is considered ready.

## Normalized requirements

- Preserve inline workflow placement and grouped `ACCEPT` and `REJECT` admission lists.
- Preserve the exact structured JSON rejection contract.
- Require deterministic scaffolding, provenance, point-of-need support references, and structural validation.
- Cover direct creation, repair, restructuring, validation, review, and application-oriented skill requests.

## Constraints

- Use the repository-selected canonical architecture.
- Prefer structured lists; reserve Markdown tables for true multi-dimensional contrastive comparisons and do not use ASCII tables for procedural content.
- Do not create agents, prompts, MCP servers, hooks, or general application implementations through this skill.
- Do not treat an unvalidated or unreviewed draft as ready.

## Resolved decisions

- Architecture: `phase-0b-inline-grouped-lists`.
- Workflow: inline in `SKILL.md`.
- Required provenance: this file.
- Date: 2026-09-22.
