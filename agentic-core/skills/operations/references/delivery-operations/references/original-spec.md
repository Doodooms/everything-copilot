# Original Specification

## Raw intent

Create one reusable DevOps workflow for repository-owned CI, packaging, release, deployment, runtime configuration, and observability changes.

## Normalized requirements

- Inspect the existing delivery/runtime system before changing it.
- Make the smallest operational change consistent with the approved requirements and environment.
- Validate configuration and scripts with the narrowest safe checks; identify rollout, rollback, and monitoring obligations.
- Preserve secret boundaries and report operational evidence, risks, and next owner.

## Constraints

- Do not invent secret values or perform an unapproved production deployment.
- Keep infrastructure/runtime ownership with DevOps; product code belongs to Implementer.
- Treat environment-specific steps and unavailable runtime access as explicit blockers, not simulated success.

## Resolved decisions

- Skill name: `delivery-operations`.
- Workflow location: inline in `SKILL.md`.
- Date: 2026-09-23.
