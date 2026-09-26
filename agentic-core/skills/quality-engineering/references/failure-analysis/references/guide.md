# Failure Analysis Guide

Use this guide only when the workflow needs a reminder for constructing or tightening a failure signal.

- Start from the exact observed symptom, not the first plausible code location.
- Prefer an existing test or command that exercises the same boundary as the report.
- Reduce one input or step at a time and rerun the same signal; keep the original case for end-to-end comparison.
- For nondeterministic behavior, record trigger count, failures, environment, and any seed or timing control.
- Form causal explanations as predictions that can be disproved by a small, safe probe.
- For performance claims, keep workload, environment, and measurement window comparable.
- If no faithful signal can be built, return the evidence gap instead of presenting a theory as a root cause.