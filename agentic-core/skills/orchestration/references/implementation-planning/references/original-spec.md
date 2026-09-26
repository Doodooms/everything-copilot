# Original Specification

## Raw intent

Create a reusable Planner workflow that turns an approved specification and architecture into a sequenced, dependency-aware implementation plan with concrete validation and handoffs.

## Normalized requirements

- Derive plan tasks from current requirements, acceptance criteria, and architecture decisions.
- Identify file/component scope, dependencies, parallelism, phases, owners, risks, and validation evidence.
- Keep product acceptance owned by the specification; the plan may add execution exit checks but MUST NOT redefine requirements.
- Return an actionable plan and traceable task IDs without writing implementation code.

## Constraints

- Scope is generic software delivery across repositories and stacks.
- Preserve one source of truth for user intent and task execution state.
- Avoid ceremonies or artifacts not justified by risk and work size.

## Resolved decisions

- Skill name: `implementation-planning`.
- Workflow location: inline in `SKILL.md`.
- Date: 2026-09-23.
