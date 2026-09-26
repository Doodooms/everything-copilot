---
id: frontend-patterns
description: Apply React and Next.js patterns for components, state, forms, rendering, and accessibility.
invoke_for:
- React or Next.js component composition, state, and data fetching
- Frontend forms, validation, rendering performance, or accessibility
avoid_for:
- Non-frontend work, backend-only behavior, and system architecture decisions
references: []
---

## Step 1 - Inspect the UI contract and existing patterns.

1. DO consume the assigned `risk_level`; inspect the current framework, component boundaries, state/data flow, design conventions, and accessibility expectations.
2. Identify observable loading, empty, error, success, and validation states relevant to the request.

## Step 2 - Apply the smallest suitable pattern.

1. Prefer existing project conventions and simple component composition; choose state, data-fetching, form, or error-boundary patterns only when the contract needs them.
2. Keep rendering and state ownership explicit; avoid speculative memoization, abstractions, or dependencies.

## Step 3 - Validate the user-visible behavior.

1. Verify relevant success and failure states, keyboard/accessibility behavior, and responsive expectations with the smallest faithful tests.
2. Return changed UI surfaces, validation evidence, assumptions, and residual risks; do not claim browser behavior that was not exercised.
