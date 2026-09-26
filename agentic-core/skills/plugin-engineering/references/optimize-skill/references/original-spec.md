# Original Specification

## Raw intent

Provide a controlled workflow for optimizing an existing skill with SkillOpt while preserving the selected canonical architecture and evaluating the final candidate on an independent holdout.

## Normalized requirements

- Validate the target and benchmark before expensive execution.
- Treat benchmark quality as the primary source of optimization direction.
- Build train, selection, and holdout from observable contract dimensions with disjoint scenarios and leakage checks.
- Keep S0 immutable and materialize complete candidates from `skill_content`.
- Expose only train and selection to SkillOpt.
- Run structural validation before Waza for every candidate.
- Compare S0 and S* on an independent holdout and report machine-readable evidence.

## Constraints

- Preserve inline workflow, grouped admission lists, provenance, support-file references, and rejection contract.
- Never mutate a frozen benchmark during optimization.
- Never select or tune against holdout evidence.
- Never report a score without identifying the behavior and grader that produced it.
- Do not silently replace the target with S*.

## Resolved decisions

- Architecture: `phase-0b-inline-grouped-lists`.
- Date: 2026-09-22.
