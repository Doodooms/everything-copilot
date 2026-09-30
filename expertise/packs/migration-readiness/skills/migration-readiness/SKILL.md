---
name: migration-readiness
description: Assess readiness evidence for concrete database schema or data migrations across client versions, backfills, rollout, and recovery. Do not write or execute migration code or SQL.
---

# Database Migration Readiness

Use this skill to assess whether a concrete database schema or data migration has enough compatibility, integrity, rollout, and recovery evidence to proceed.

## Boundaries

This skill reviews plans and evidence. It does not author migration code, generate or execute SQL, run backfills, alter databases, or operate deployment systems. It is independent of general software-engineering implementation guidance.

Accept requests that assess a database schema or data migration, including:

- coexistence of old and new application clients during rolling deployment;
- schema expansion, backfills, cutover, and destructive cleanup;
- data invariants, idempotency, reconciliation, and verification evidence;
- deployment order, rollback, forward recovery, and operational dependencies.

Do not use this skill for:

- generic SQL explanations or SQL/query generation;
- API-only compatibility without a database migration;
- live incident diagnosis or immediate production commands;
- performance tuning or index/query-plan optimization;
- choosing a database product;
- implementing, executing, or operating a migration.

If a request combines readiness review with implementation, keep the review bounded and route implementation to the appropriate software-engineering owner.

## Assessment procedure

1. Identify the database change, affected data, old and new application versions, rollout stages, and requested decision. Mark unavailable facts as unknown.
2. Assess compatibility across each period when old and new clients or schemas coexist. Consider reads, writes, defaults, nullability, constraints, and removal timing only where applicable to the supplied plan.
3. Assess data integrity evidence: source and target invariants, backfill scope, idempotency or restart behavior, reconciliation, and verification thresholds. Do not assume an unreported check passed.
4. Assess rollout dependencies and ordering, observation points, stop conditions, rollback feasibility, and forward-recovery path. Identify irreversible steps and the evidence required before them.
5. Return one bounded result: `READY`, `CONDITIONAL`, or `BLOCKED`. Missing material evidence must remain an explicit unknown and may require `CONDITIONAL` or `BLOCKED`; never turn unknown into a favorable fact.
6. Separate evidence-backed findings from assumptions. State conditions that must be met before proceeding and identify who or what can supply missing evidence.

## Output contract

Return:

- `status`: `READY`, `CONDITIONAL`, or `BLOCKED`;
- `scope`: database change and rollout stage assessed;
- `evidence`: supplied facts and checks, with provenance when available;
- `compatibility`: old/new client and schema coexistence findings;
- `data_integrity`: invariants, backfill, reconciliation, and verification findings;
- `rollout_recovery`: ordering, dependencies, rollback, and forward-recovery findings;
- `unknowns`: material facts not established by the inputs;
- `conditions`: evidence or action required before proceeding;
- `rationale`: concise basis for the bounded status.

Do not claim that the database, migration, or backfill was inspected or executed unless the user supplied verifiable evidence of that action.
