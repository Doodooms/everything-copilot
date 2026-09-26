# Original Specification

## Raw intent

Create a focused static review workflow for completed software changes that reports grounded correctness, regression, maintainability, compatibility, and architecture findings without modifying files.

## Normalized requirements

- Review the approved contract, change diff, relevant call sites, tests, and validation evidence.
- Report only actionable, evidence-backed findings with severity, location, impact, confidence, and appropriate owner.
- Distinguish blockers from optional hardening and state residual uncertainty.
- Leave implementation, adversarial execution, security-design review, and final acceptance to their owners.

## Constraints

- No production/test edits, speculative findings, or duplicated broad QA.
- Scope review to the requested change and consequential dependencies.

## Resolved decisions

- Skill name: `code-review`.
- Workflow location: inline in `SKILL.md`.
- Date: 2026-09-23.
