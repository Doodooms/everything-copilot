---
id: optimize-skill
description: 'Apply the optimize-skill method: baseline measurement, SkillOpt candidate
  training, structural candidate validation, selection, and independent holdout evaluation.'
invoke_for:
- baseline measurement, SkillOpt candidate training, structural candidate validation,
  selection, and independent holdout evaluation
avoid_for:
- first-time skill authoring, general prompt editing, or application implementation
references: []
---

## Step 1 - Resolve the target

1. Use #tool:read to inspect the target `SKILL.md`, [provenance](../references/optimize-skill/references/original-spec.md), architecture configuration, and consumed support files.
2. Use #tool:search to locate its existing validator, benchmark, SkillOpt adapter, and output directory.
3. Stop if the target is missing, structurally invalid, or outside the selected canonical architecture.

## Step 2 - Verify the benchmark boundary

1. Use #tool:execute to run the target structural validator.
2. Read [benchmark policy](../references/optimize-skill/references/benchmark-policy.md) to design or audit the measurement before any run.
  - Confirm that tasks are derived from the target's semantic contract and cover success, near misses, ambiguity, missing information, sequencing, over-eager actions, recovery, and cost-sensitive failures.
  - Confirm that train, selection, and holdout use disjoint task instances and scenarios, with holdout hidden from all optimization inputs and reports used during selection.
  - Confirm that graders measure observable behavior, distinguish hard constraints from quality preferences, and have fixtures sufficient to reproduce the task without hidden assumptions.
3. Use #tool:execute to verify the benchmark lock and confirm that train and selection are available while holdout remains outside the SkillOpt configuration.
4. Record the benchmark digest, target digest, model, seed, and command versions before any run.

## Step 3 - Establish S0

1. Materialize the unchanged target as the S0 candidate workspace.
2. Use #tool:execute to run Waza on train and selection with structural validation enabled.
3. Record hard structural pass rate, semantic grader score, completion rate, tool cost, and failures. Do not call Waza status a quality score.

## Step 4 - Train and select candidates

1. Use #tool:execute to launch the repository SkillOpt configuration with only train data and the permitted selection interface.
2. Materialize every returned `skill_content` into a complete candidate workspace copied from the target package.
3. Reject candidates failing structural validation before evaluation and record the rejection reason.
4. Evaluate surviving candidates on selection, retain the best candidate by the declared objective, and label it S*.

## Step 5 - Run independent holdout

1. Verify the benchmark digest again before evaluation.
2. Use #tool:execute to evaluate S0 and S* on holdout without exposing holdout prompts, transcripts, or scores to SkillOpt.
3. Use [the optimization report template](../references/optimize-skill/assets/optimization-report-template.md) to compare hard gates first, then semantic quality, completion, efficiency, and failure categories.
4. Declare optimization successful only when S* preserves all hard gates and improves the predeclared selection objective without unacceptable holdout regression.

## Step 6 - Report

1. Write a reproducible report containing target and benchmark digests, commands, configuration, candidate lineage, structural failures, S0/S* train-selection-holdout scores, and residual risks.
2. Preserve rejected candidates and their validation reasons, but do not replace the target package until S* passes the independent holdout.
3. Summarize the exact selected content changes and the next manual review decision.
4. Before accepting a candidate, use [the target validator](../references/optimize-skill/scripts/validate_optimize_target.py) for any target-specific checks that are not covered by the canonical scaffold validator.
