# Original Specification

## Raw intent

Add a narrowly scoped skill for keeping repository documentation synchronized with approved and verified implementation behavior.

## Normalized requirements

- Consume the current approved specification and plan, implementation evidence, changed paths, and assigned documentation scope.
- Find the existing authoritative pages and update only the sections affected by the approved change.
- Preserve product intent and avoid unsupported claims, duplicate guidance, and direct edits to generated output.
- Run the narrowest available documentation-specific checks and return changed paths, evidence, and remaining gaps.

## Constraints

- Do not decide requirements, implementation behavior, or acceptance criteria.
- Do not infer facts from external research when implementation or specification evidence is missing.
- Do not edit product code or expand the documentation scope beyond the approved plan.
- Do not stage, commit, or change repository lifecycle state.

## Resolved decisions

- Package name: `documentation-sync`.
- Owner: Implementer, conditionally, when the approved plan assigns a documentation change.
- Research and implementation remain owned by their existing agents.
- Date: 2026-09-24.
