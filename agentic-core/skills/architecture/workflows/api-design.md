---
id: api-design
description: Design or review REST endpoint and compatibility contracts.
invoke_for:
- REST resource naming, methods, status codes, and error responses
- Pagination, filtering, sorting, versioning, and rate-limit contracts
- New or changed public and partner-facing REST endpoints
avoid_for:
- Product-domain semantics, system topology, server implementation, and non-REST APIs
references: []
---

## Step 1 - Establish the API contract boundary.

1. DO consume the assigned `risk_level`; inspect approved requirements, existing endpoints, consumers, compatibility constraints, and repository conventions.
2. Return unresolved product semantics to the Orchestrator; keep this workflow within REST interface design.

## Step 2 - Specify the REST contract.

1. Define plural resource paths and sub-resources; choose HTTP methods by their safety and idempotency semantics.
2. Specify status codes, request/response shapes, validation errors, and pagination/filter/sort behavior.
3. Set versioning and rate-limit behavior only when required by the compatibility or operational contract.

## Step 3 - Check compatibility and return the contract.

1. Check method semantics, error cases, naming consistency, client impact, and backward compatibility against the stated acceptance criteria.
2. Return the endpoint contract, representative request/response examples, alternatives, assumptions, and unresolved decisions; do not implement endpoints or decide product semantics.
