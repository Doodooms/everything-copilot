---
id: api-design
description: Design or review REST endpoint and compatibility contracts.
invoke_for:
- REST resource naming, methods, status codes, and error responses
- Pagination, filtering, sorting, versioning, and rate-limit contracts
- New or changed public and partner-facing REST endpoints
avoid_for:
- Product-domain semantics, system topology, server implementation, and non-REST APIs
references:
  - ../references/api-design/api-design-patterns.md
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
## Step 1 - Establish the API contract boundary.

1. DO consume the assigned `risk_level`; inspect approved requirements, existing endpoints, consumers, compatibility constraints, and repository conventions.
2. Return unresolved product semantics to the Orchestrator; keep this workflow within REST interface design.

## Step 2 - Specify the REST contract.

1. Use the [API design patterns reference](../references/api-design/api-design-patterns.md) for resource naming, status codes, response shapes, pagination, authentication, authorization, rate limits, and framework examples.
2. Define plural resource paths and sub-resources; choose HTTP methods by their safety and idempotency semantics.
3. Specify status codes, request/response shapes, validation errors, and pagination/filter/sort behavior.
4. Set versioning and rate-limit behavior only when required by the compatibility or operational contract.

## Step 3 - Check compatibility and return the contract.

1. Check method semantics, error cases, naming consistency, client impact, and backward compatibility against the stated acceptance criteria.
2. Confirm input validation, standardized errors, list pagination, explicit authentication/authorization policy, rate limiting, no internal-detail leakage, and updated API documentation.
3. Return the endpoint contract, representative request/response examples, alternatives, assumptions, and unresolved decisions; do not implement endpoints or decide product semantics.
</workflow>
