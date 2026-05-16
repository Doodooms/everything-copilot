---
name: database-audit
description: "WHAT: Review database-facing changes for integrity, performance, security, and operational safety. USE FOR: SQL review, migration safety, schema design checks, query-shape analysis, transaction review, and multi-tenant data-boundary checks. DO NOT USE FOR: generic application review, writing the migration itself, or non-database infrastructure work."
user-invocable: false
metadata:
  creation-date: 2026-05-14
  creator: Doodooms
---

<definitions>

- **database finding** : A concrete issue in schema, query shape, transaction scope, privilege boundary, or migration safety that can affect correctness or operations.

</definitions>

<workflow>

## Step 0 - **CONFIRMATION**

1. USE #tool:read **IMMEDIATELY** on #file:./references/USEFOR.md and **IMMEDIATELY** on #file:./references/DONOTUSEFOR.md to confirm with certainty if this skill should be used.
2. Now read the following rules and workflow steps to understand how the skill works and what it requires for execution.

<rules>

- Review integrity, security, performance, and operational safety together.
- Prefer real access patterns over abstract schema opinions.
- Reference support files only at the point of need.

</rules>

## Step 1 - Inspect the database-facing change surface.

1. Use #tool:read on the queries, schema definitions, migrations, and data-access code under review.
2. Use #tool:search to locate related indexes, constraints, transaction boundaries, and multi-tenant access points.
3. Use #tool:read on #file:./references/guide.md only if the audit checklist is still needed.

## Step 2 - Evaluate integrity, performance, and operational safety.

1. Check parameterization, constraints, indexes, transaction scope, and delete behavior.
2. Review privilege boundaries, tenant isolation, and unsafe migration assumptions.
3. Separate confirmed findings from optional hardening ideas.

## Step 3 - Return the database audit findings.

1. Use #tool:read to verify any referenced schema or query location before finalizing the audit.
2. Return severity, location, impact, and remediation direction for each material finding.

</workflow>