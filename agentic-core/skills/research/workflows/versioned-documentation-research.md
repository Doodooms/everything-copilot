---
id: versioned-documentation-research
description: 'Apply the versioned-documentation-research method: library, SDK, API,
  language, and product behavior or compatibility questions tied to a version.'
invoke_for:
- library, SDK, API, language, and product behavior or compatibility questions tied
  to a version
avoid_for:
- GitHub source/history research, scholarly evidence, implementation, or unversioned
  claims presented as exact
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
## Step 1 - Resolve the target product and version.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Read the approved question and inspect the relevant project manifest, lockfile, or usage site with #tool:read or #tool:search when the repository is available.
2. Record the product/package, target version, API surface, runtime/platform constraints, and supported artifact or decision.
   - If the version is not available and materially changes the answer, return `partial` with the missing version; do not assume `latest`.
3. When authoring or materially repairing this package, consult the [original specification](../references/versioned-documentation-research/references/original-spec.md) as provenance only.

## Step 2 - Inspect authoritative, version-matched sources.

1. When available, use #tool:mcp_context7_resolve_library_id to resolve the canonical library, then #tool:mcp_context7_query_docs with the target version and narrow API question.
2. Use #tool:web to locate and #tool:browser to inspect the official versioned page or release source identified by Context7; Context7 snippets alone are not sufficient evidence.
3. If Context7 is unavailable, has no exact version, or returns no traceable official source, use the official documentation and release history directly and label any version fallback.
4. Record the exact URL, product/version, page/section, observation date, relevant statement or example, platform applicability, and any fallback or contradiction.

## Step 3 - Return version-scoped findings.

1. Return `status: success | partial | failed`, the supported question/artifact, concise findings, exact version and source links, evidence location, applicability, fact-versus-inference distinction, and uncertainty.
2. Stop when the required documented behavior or compatibility fact is established; do not generalize beyond the cited version.
</workflow>
