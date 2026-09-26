# Original Specification

## Raw intent

Provide a focused failure-diagnosis method: establish a reliable feedback signal, reproduce and minimize the observed symptom, test competing explanations, and return evidence to the owning specialist.

## Normalized requirements

- Diagnose observed failures without taking ownership of code or operational repair.
- Prefer a tight, deterministic reproducer; preserve original reproduction data while minimizing.
- Use falsifiable hypotheses, targeted probes, and proportional repetition for intermittent behavior.
- Record actual behavior, failure chain, evidence, uncertainty, and next owner.
- Redact secrets and preserve user state.

## Constraints and resolved decisions

- The imported debugging workflow's diagnostic techniques were adopted selectively; its implementation, commit, instrumentation, and user-checkpoint instructions were excluded to preserve QA/Implementer/DevOps boundaries.
- Date: 2026-09-24.
