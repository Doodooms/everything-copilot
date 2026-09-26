---
name: delivery-operations
description: "WHAT: Safely change repository CI, packaging, release, deployment, runtime configuration, and observability. USE FOR: approved delivery-pipeline or operational work in an existing environment. DO NOT USE FOR: product features, architecture ownership, unapproved production deployment, or generic verification-only requests."
user-invocable: false
metadata:
  creation-date: 2026-09-23
  creator: Doodooms
---

<definitions>

- **operational change**: A change to how software is built, configured, released, deployed, monitored, or recovered.
- **rollout guard**: A precondition, staged exposure, health signal, or rollback action that limits deployment impact.
- **runtime evidence**: Actual validation of the target configuration or service; a syntax check alone is not runtime evidence.

</definitions>

<admission>

Classify the request into exactly one outcome: `ACCEPT` or `REJECT`.

## ACCEPT

- Implement an explicitly approved change to CI/CD, packaging, release, deployment, runtime configuration, observability, or operational documentation.
- Diagnose operational delivery/configuration failures and define a bounded repair within the approved environment.

## REJECT

- Product behavior or application code -> `implementer`.
- Architecture decisions or deployment-system design -> `architect`.
- Delivery sequencing -> `planner`.
- Code-only verification -> `verification-loop`.
- Security policy/design review -> `reviewer` using `security-review`; dynamic security testing -> `quality-assurance`.
- Unapproved production action or missing environment authorization -> `orchestrate` for clarification.

For REJECT, return exactly:

```json
{"status":"rejected","skill":"delivery-operations","reason":"<concise reason>","routing":"<route or null>"}
```

</admission>

<rules>

- Inspect existing workflows, environments, configuration sources, deployment permissions, secrets boundaries, health checks, and rollback practices before editing.
- Preserve the established platform and least-privilege model; do not add tooling or infrastructure without an approved need.
- MUST NOT invent secret values, expose credentials, or execute irreversible/production changes without explicit authorization.
- Separate static validation from target-environment verification; unavailable credentials or runtime access are blockers, not successful checks.
- Every operational change MUST state blast radius, rollout/rollback plan, monitoring signals, validation, and handback owner.
- Keep persistent state/configuration changes backward-compatible or provide an explicit migration and recovery path.

</rules>

<workflow>

## Step 1 - Establish the operational boundary.

1. Use #tool:read to inspect the approved task, repository CI/release/deployment files, environment configuration, applicable runbooks, and existing validation commands.
2. Use #tool:todo to create native todos for distinct phases only; mark deployment as blocked until authorization and required environment evidence are available.
3. Identify affected environments, permissions, secrets, data/state risk, rollback path, and non-goals.

## Step 2 - Apply and validate the operational change.

1. Use #tool:edit to make the smallest change in the owning workflow/configuration/runbook surface.
2. Use #tool:execute to run syntax, schema, lint, or dry-run checks before any external side effect.
3. Perform deployment or live verification only when explicitly authorized; verify health and rollback signals with actual evidence.
4. Update operational documentation only to reflect verified behavior.

## Step 3 - Return operational evidence.

1. Report changed files, exact commands/results, environments actually exercised, unverified assumptions, risks, and blockers.
2. State rollout/rollback/monitoring guidance and the next owner.
3. Use #tool:todo to mark todos complete only after the corresponding evidence is recorded; never infer deployment success from configuration validity.

</workflow>

Source provenance: [original specification](./references/original-spec.md).