# Original specification

## Raw intent

`TASK-CORE01` adds the approved P7 `token-optimization` workflow and local token/context measurement. Preserve semantic richness while identifying unnecessary context. Keep agent definitions, skills, and tool projections local; do not submit private text to external token counters.

## Normalized requirements

- Measure a selected agent definition, its selected skills, and its local tool-schema projection per agent.
- Report category counts, per-agent totals, tokenizer/estimator identity, and uncertainty.
- Offer semantic-preserving optimization guidance, then remeasure the same target.
- Treat optional numeric budgets as advisory warnings, never as rejection or release gates.

## Constraints

- Do not upload source text or schemas, call external counting services, or add network behavior.
- Do not remove required responsibilities, constraints, evidence, or safety boundaries merely to reduce counts.
- Do not claim model-exact token counts from an approximation.

## Resolved decisions

- The package lives at `agentic-core/skills/token-optimization/`.
- Its self-contained `measure_context.py` reads a local JSON projection and only files contained under the projection's directory; it emits a report to stdout and does not mutate source files.
- The built-in local regex tokenizer is explicitly approximate. Optional budgets only add warnings.

**Provenance:** `SPEC-EXPERTISE1@3`, `TASK-CORE01`, `REQ-CORECORRECTIONS1`, `REQ-CONTEXT1`, `AC-CORECORRECTIONS1`, and `ADR-CORE007`. Recorded 2026-09-24.
