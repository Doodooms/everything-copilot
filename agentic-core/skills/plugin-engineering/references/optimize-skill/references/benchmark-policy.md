# Benchmark Policy

A benchmark contains explicit `train`, `selection`, and `holdout` surfaces. The lock digest covers every benchmark task, fixture, grader, and configuration file, excluding only the lock file itself.

Freeze before baseline. Verify before every candidate evaluation and after optimization. Mutation is a hard failure. The holdout is executed only after S* selection and is never passed to SkillOpt configuration or training inputs.

## Measurement first

Optimization can only improve what the benchmark measures. Before selecting a
model, learning rate, or candidate, establish which observable behaviors define
success for the target skill. A benchmark is useful when a better score means
the skill followed its contract more reliably, not merely that it matched the
wording of the task more closely.

Derive benchmark dimensions from the target's ontology and semantic contract:

- correct admission and rejection decisions;
- correct use of required tools, files, and workflow order;
- preservation of structural invariants and provenance;
- useful behavior when information is missing or ambiguous;
- recovery after an invalid input or failed action;
- avoidance of unnecessary actions, unsupported assumptions, and excess cost;
- quality of the final artifact, not only intermediate narration.

## Building the task pool

Write each task as a reproducible scenario with a user request, workspace
fixture, expected observable outcomes, hard constraints, and grader evidence.
Tasks should vary the situation while keeping the contract stable. Include
both representative cases and adversarial near misses:

- direct valid requests;
- requests missing one decision-critical detail;
- requests that resemble the skill but belong elsewhere;
- conflicting constraints or wrong sequencing;
- realistic empty, malformed, stale, or partially complete files;
- recovery after a failed validation or interrupted action;
- cases where doing more work is worse than asking or stopping.

Avoid tasks whose answer is determined by a single keyword, whose fixture hides
the intended decision, or whose grader rewards stylistic similarity instead of
observable compliance.

## Split construction

- **Train** should contain broad representative coverage and enough variation
for candidate changes to receive a useful learning signal. It may expose
detailed grader feedback to the optimizer.
- **Selection** should contain unseen instances of the same contract and should
be difficult enough to reject superficial improvements. Use it only for
candidate comparison and selection.
- **Holdout** should contain unseen scenarios, fixtures, and task wording. Keep
it outside optimizer configuration, prompts, candidate feedback, and any
decision made before S* is selected.

Separate splits by scenario identity, not only by prompt text. Do not place
near-duplicate requests, shared mutable fixtures, or grader-specific hints in
different splits. When a domain requires the same fixture family, partition by
the underlying case and verify that no solution artifact leaks across splits.

## Grader design

Every grader should state what it observes and how it passes or fails. Keep
hard gates separate from soft quality scores:

- hard gates cover routing, required files, structural invariants, safety, and
rejection behavior;
- semantic graders cover whether the result solves the requested task;
- efficiency graders cover unnecessary tool calls, latency, or resource cost;
- recovery graders cover failure handling and incomplete information.

Prefer deterministic assertions for files, commands, schemas, and invariants.
Use rubric-based grading only for genuinely semantic output, with examples of
passing and failing behavior. A score without an actionable failure category is
poor feedback for optimization.

## Freeze and audit checklist

Before baseline, verify:

- all tasks, fixtures, graders, and configuration files are included in the
digest;
- task IDs and split membership are stable and disjoint;
- holdout paths are absent from optimizer inputs and candidate feedback;
- graders do not read hidden expected answers through the candidate workspace;
- the benchmark can be executed from a clean checkout;
- the lock file is generated after, not before, the final audit.

After every candidate mutation, recompute and compare the digest. Any change
to a task, fixture, grader, split assignment, or benchmark configuration is a
hard failure and requires a new benchmark version.
