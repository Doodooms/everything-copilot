# Original Specification

## Raw intent

Create a reusable QA workflow for independently trying to falsify a completed implementation against its approved contract and test assumptions.

## Normalized requirements

- Derive high-signal adversarial checks from requirements, acceptance criteria, changed behavior, and risk.
- Exercise boundary values, invalid states, sequences, errors, integration, persistence, compatibility, concurrency, security, and performance when relevant.
- Report reproducible counterexamples and test-surface gaps with evidence and the correct owner.
- Keep QA independent from implementation and final acceptance.

## Constraints

- Do not edit production code to make a check pass.
- Do not claim coverage for checks that were not executed.
- Use bounded, risk-proportional testing; do not create noisy tests without a falsifiable purpose.

## Resolved decisions

- Skill name: `adversarial-testing`.
- Workflow location: inline in `SKILL.md`.
- Date: 2026-09-23.
