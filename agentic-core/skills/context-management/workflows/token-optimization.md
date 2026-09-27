---
id: token-optimization
description: 'Apply the token-optimization method: local token/context measurements,
  per-agent projection reviews, and approved semantic-preserving prompt or skill optimization.'
invoke_for:
- local token/context measurements, per-agent projection reviews, and approved semantic-preserving
  prompt or skill optimization
avoid_for:
- external token-counting services, hard token gates, or changing role and product
  semantics
references: []
---
<critical_rules>
- MUST keep work within this subskill’s declared scope and its specific safety or authority constraints.
- MUST NOT replace the parent domain skill’s admission, global routing, or authority boundaries.
</critical_rules>

<general_rules>
- SHOULD load listed references only at the procedure step that needs them.
- MAY report unavailable evidence or unresolved decisions as unknown.
</general_rules>

<risk_assessment>
Consume the Orchestrator-assigned `risk_level` through the parent domain skill; MUST NOT reclassify or downgrade it. SHOULD escalate only when new evidence materially increases risk. Scale evidence depth, not authority or approvals.
</risk_assessment>

<rules>
- MUST follow this selected subskill only within its declared procedure and scope.
- MUST NOT replace the parent domain skill’s admission, global routing, or authority boundaries.
- MUST return the result, evidence, remaining unknowns, risks, and status required by this procedure.
</rules>

<workflow>
## Step 1 - Bound the measurement.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Inspect the approved target and identify which agent definition, top-level skill files, selected immediate workflows, and local tool schemas are actually projected for each agent.
   - Do not count every installed skill or every available tool as if it were loaded.
   - Each `skills` entry MUST point to a package's `SKILL.md`; list only procedures selected for that agent under `workflows`.
   - Reference paths MAY be listed for audit visibility, but generic references MUST NOT contribute to the total. Procedures belong under a package's immediate `workflows/` directory, never under `references/`.
   - Use the [projection example](../references/token-optimization/assets/context-projection.example.json) only when a local target manifest is needed.
   - Read the [recorded source specification](../references/token-optimization/references/original-spec.md) only when provenance is needed; it does not override the current handoff.
2. Record the workspace root and ensure the projection manifest points only to local files within its own directory tree.
   - If a local tool schema is unavailable, report that the tool-schema portion is incomplete rather than substituting an invented schema size.

## Step 2 - Measure locally.

1. Use #tool:execute on [measure_context.py](../references/token-optimization/scripts/measure_context.py) to run `PYTHONDONTWRITEBYTECODE=1 python scripts/measure_context.py --manifest <projection.json>` from this skill package's directory.
   - The script reads agent, `SKILL.md`, selected workflows, and tool-schema files named by the projection and emits per-agent category counts as JSON on stdout; generic reference files are never opened or counted.
   - Its `local-regex-estimate-v1` tokenizer is deterministic and approximate; do not present it as an exact model token count or as the active session's occupancy.
   - Projection paths are relative to the manifest and must remain inside its directory tree. The script does not write source files or make network requests.
2. For one local text file, use #tool:execute to run `PYTHONDONTWRITEBYTECODE=1 python scripts/measure_context.py --file <path>`; it returns that file's approximate count without requiring a projection manifest.
3. Treat any configured `warning_budget_tokens` as advisory only. A warning is not a validation failure or a release gate.
4. For live context-window use, load `multi-harness` and select its `smart-compact` workflow. Do not add account quota or billing usage to a local context projection.

## Step 3 - Optimize only with semantic evidence.

1. Trace high counts to repeated policy, unnecessary always-loaded detail, or support guidance that can be loaded at point of need.
2. Make only approved edits that preserve all required semantics; stop and route if the requested reduction would change ownership, behavior, acceptance, or safety constraints.
3. Rerun the same local projection after each substantive edit and compare category and per-agent totals.

## Step 4 - Report the result.

1. Return the exact projection targets, estimator identity, per-agent definition/skill/workflow/tool counts, excluded reference paths, total counts, warnings, changes, and before/after comparison when available.
2. State approximation or missing-schema limitations. Confirm that no source text was uploaded and that budgets were treated as advisory.
</workflow>
