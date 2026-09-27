---
id: database-audit
description: 'Apply the database-audit method: SQL review, migration safety, schema
  design checks, query-shape analysis, transaction review, and multi-tenant data-boundary
  checks.'
invoke_for:
- SQL review, migration safety, schema design checks, query-shape analysis, transaction
  review, and multi-tenant data-boundary checks
avoid_for:
- generic application review, writing the migration itself, or non-database infrastructure
  work
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
- Review integrity, security, performance, and operational safety together.
- Prefer real access patterns over abstract schema opinions.
- Reference support files only at the point of need.
- MUST return the result, evidence, remaining unknowns, risks, and status required by this procedure.
</rules>

<workflow>
## Step 1 - Inspect the database-facing change surface.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Use #tool:read on the queries, schema definitions, migrations, and data-access code under review.
2. Use #tool:search to locate related indexes, constraints, transaction boundaries, and multi-tenant access points.
3. Use #tool:read on #file:../references/database-audit/references/guide.md ([database audit guide](../references/database-audit/references/guide.md)) only if the audit checklist is still needed.

## Step 2 - Evaluate integrity, performance, and operational safety.

1. Check parameterization, constraints, indexes, transaction scope, and delete behavior.
2. Review privilege boundaries, tenant isolation, and unsafe migration assumptions.
3. Separate confirmed findings from optional hardening ideas.

## Step 3 - Return the database audit findings.

1. Use #tool:read to verify any referenced schema or query location before finalizing the audit.
2. Return severity, location, impact, and remediation direction for each material finding.
</workflow>
