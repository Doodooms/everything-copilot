---
name: token-optimization
description: "WHAT: Measure and reduce unnecessary agent, skill, and tool-schema context while preserving meaning. USE FOR: local token/context measurements, per-agent projection reviews, and approved semantic-preserving prompt or skill optimization. DO NOT USE FOR: external token-counting services, hard token gates, or changing role and product semantics."
user-invocable: true
metadata:
  creation-date: 2026-09-24
  creator: Doodooms
license: MIT
---

<definitions>

- **context projection** : A target agent definition plus each loaded top-level `SKILL.md`, selected workflow, selected subskill, and available local tool-schema file.
- **subskill** : A package-local specialized method explicitly selected by a workflow and counted only when it is part of the projected path.
- **reference** : Generic point-of-need supporting knowledge under `references/`; references MUST NOT be included in projected token totals unless they are explicitly selected as a subskill.
- **local estimate** : A deterministic count produced from local text without sending source content to a remote service; the built-in regex estimate is not model-tokenizer exact.
- **semantic-preserving optimization** : A reduction of duplication or unnecessary always-loaded detail that retains every required decision, responsibility, constraint, and safety boundary.

</definitions>

<rules>

- MUST keep source text, schemas, and counts local and report measurements without external uploads; MUST NOT upload private text or use external token counters.
- MUST report the tokenizer/estimator and its limitations alongside target-aware counts.
- Numeric budgets are advisory signals; MUST NOT reject work or remove required content solely because a count exceeds a budget.
- MUST preserve behavior, role ownership, evidence requirements, and safety constraints while optimizing.

</rules>

<admission>

## ACCEPT

- Measure local token/context cost for explicitly selected agent definitions, skills, or tool schemas.
- Review an agent's local skill/tool projection and identify redundant or unnecessary context.
- Apply an approved, semantic-preserving reduction and compare before/after counts for the same targets.

## REJECT

- Upload or submit source text to a hosted token counter → refuse; do not transmit the text.
- Change responsibilities, acceptance criteria, architecture, or product behavior to meet a token budget → `architect` or `orchestrator`.
- Implement a tokenizer service, pack compiler, or lifecycle tool → `implementer` within an approved task.

For REJECT, return exactly:

```json
{"status":"rejected","skill":"token-optimization","reason":"<concise reason>","routing":"<route or null>"}
```

</admission>

<workflow>

## Step 1 - Bound the measurement.

1. Inspect the approved target and identify which agent definition, top-level skill files, selected workflows/subskills, and local tool schemas are actually projected for each agent.
   - Do not count every installed skill or every available tool as if it were loaded.
   - Each `skills` entry MUST point to a package's `SKILL.md`; list only procedures selected for that agent under `workflows` and `subskills`.
   - Reference paths MAY be listed for audit visibility, but generic references MUST NOT contribute to the total. A reference file explicitly selected as a subskill MUST be listed once under `subskills`, not also counted as a generic reference.
   - Use the [projection example](./assets/context-projection.example.json) only when a local target manifest is needed.
   - Read the [recorded source specification](./references/original-spec.md) only when provenance is needed; it does not override the current handoff.
2. Record the workspace root and ensure the projection manifest points only to local files within its own directory tree.
   - If a local tool schema is unavailable, report that the tool-schema portion is incomplete rather than substituting an invented schema size.

## Step 2 - Measure locally.

1. Use #tool:execute on [measure_context.py](./scripts/measure_context.py) to run `PYTHONDONTWRITEBYTECODE=1 python scripts/measure_context.py --manifest <projection.json>` from this skill package's directory.
   - The script reads agent, `SKILL.md`, selected workflows, selected subskills, and tool-schema files named by the projection and emits per-agent category counts as JSON on stdout; generic reference files are never opened or counted.
   - Its `local-regex-estimate-v1` tokenizer is deterministic and approximate; do not present it as an exact model token count.
   - Projection paths are relative to the manifest and must remain inside its directory tree. The script does not write source files or make network requests.
2. For one local text file, use #tool:execute to run `PYTHONDONTWRITEBYTECODE=1 python scripts/measure_context.py --file <path>`; it returns that file's approximate count without requiring a projection manifest.
3. Treat any configured `warning_budget_tokens` as advisory only. A warning is not a validation failure or a release gate.

## Step 3 - Optimize only with semantic evidence.

1. Trace high counts to repeated policy, unnecessary always-loaded detail, or support guidance that can be loaded at point of need.
2. Make only approved edits that preserve all required semantics; stop and route if the requested reduction would change ownership, behavior, acceptance, or safety constraints.
3. Rerun the same local projection after each substantive edit and compare category and per-agent totals.

## Step 4 - Report the result.

1. Return the exact projection targets, estimator identity, per-agent definition/skill/workflow/subskill/tool counts, excluded reference paths, total counts, warnings, changes, and before/after comparison when available.
2. State approximation or missing-schema limitations. Confirm that no source text was uploaded and that budgets were treated as advisory.

</workflow>