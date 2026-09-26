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

## Step 0 - **CONFIRMATION**

1. USE #tool:read **IMMEDIATELY** on #file:../references/database-audit/references/USEFOR.md ([when to use](../references/database-audit/references/USEFOR.md)) and **IMMEDIATELY** on #file:../references/database-audit/references/DONOTUSEFOR.md ([when not to use](../references/database-audit/references/DONOTUSEFOR.md)) to confirm with certainty if this skill should be used.
2. Now read the following rules and workflow steps to understand how the skill works and what it requires for execution.

<rules>

- Review integrity, security, performance, and operational safety together.
- Prefer real access patterns over abstract schema opinions.
- Reference support files only at the point of need.

</rules>

## Step 1 - Inspect the database-facing change surface.

1. Use #tool:read on the queries, schema definitions, migrations, and data-access code under review.
2. Use #tool:search to locate related indexes, constraints, transaction boundaries, and multi-tenant access points.
3. Use #tool:read on #file:../references/database-audit/references/guide.md ([database audit guide](../references/database-audit/references/guide.md)) only if the audit checklist is still needed.

## Step 2 - Evaluate integrity, performance, and operational safety.

1. Check parameterization, constraints, indexes, transaction scope, and delete behavior.
2. Review privilege boundaries, tenant isolation, and unsafe migration assumptions.
3. Separate confirmed findings from optional hardening ideas.

## Step 3 - Return the database audit findings.

1. Use #tool:read to verify any referenced schema or query location before finalizing the audit.
2. Return severity, location, impact, and remediation direction for each material finding.
