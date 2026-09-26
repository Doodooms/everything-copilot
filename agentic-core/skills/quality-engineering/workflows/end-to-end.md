---
id: end-to-end
description: Test a browser or complete user journey through the application's real
  boundaries.
invoke_for:
- browser-visible behavior
- complete user journeys spanning UI and backend boundaries
- browser test flakiness or evidence review
avoid_for:
- isolated logic with a faithful lower-level test
references:
  - ../references/testing/references/test-levels.md
---

## Step 1 - Bound the user journey.

1. State the user-visible contract and smallest complete flow; reuse the repository's browser framework, configuration, fixtures, and test data conventions.
2. Keep each test isolated and deterministic; prepare only the data and services the journey needs.

## Step 2 - Exercise the real browser contract.

1. Prefer accessible role/name selectors or stable project test IDs and framework auto-waiting; synchronize on the required DOM or network condition instead of arbitrary sleeps.
2. Assert observable user outcomes at the integration boundary; avoid coupling to internal component structure or adding page-object layers without repeated interaction complexity.

## Step 3 - Diagnose and report execution.

1. Run the focused browser test and inspect its trace, screenshot, or video on failure; retries MAY expose flakiness but DO NOT repair it.
2. Report the exact command/environment, flow covered, outcome, artifacts, and residual risk; MUST NOT hide a flaky test with a skip or broad retry.
