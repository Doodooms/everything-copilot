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
## Step 1 - Inspect the UI contract and existing patterns.

1. DO consume the assigned `risk_level`; inspect the package manifest/lockfile, exact React/Next.js versions, router (App or Pages), existing component boundaries, state/data flow, and design conventions.
2. Identify observable loading, empty, error, success, validation, keyboard, and responsive states relevant to the request; record which components or server boundaries own each state.

## Step 2 - Apply the smallest suitable pattern.

1. Prefer the repository's component composition and state conventions. Keep state at its narrowest correct owner; add a custom hook only for behavior that is reused or independently meaningful.
2. For Next.js App Router, use [the official Server and Client Components guidance](https://nextjs.org/docs/app/getting-started/server-and-client-components) for the installed version: keep server rendering/data access on the server and add a client boundary only for interactivity or browser APIs. Read server-side data from its source instead of looping through the app's Route Handler; use Server Actions for mutations only when supported by the installed version and existing app pattern. Do not apply App Router rules to a Pages Router app.
3. In React, keep event-specific actions in their event handlers and use Effects to synchronize with external systems; consult [You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect) when deciding whether an Effect is warranted. Prefer semantic HTML and native controls for forms and keyboard interaction; use custom ARIA widgets only when their full keyboard and announcement behavior is implemented.
4. Use Context7 to check official, version-matched React or Next.js documentation when an API or framework behavior determines the design. Measure a rendering bottleneck before memoization, virtualization, or code splitting; follow the installed compiler and framework behavior rather than copying a generic example.

## Step 3 - Validate the user-visible behavior.

1. Verify relevant success, empty, loading, validation, and failure states plus keyboard and responsive behavior with the smallest faithful tests; inspect accessibility output when custom controls or live status are involved.
2. Return the component/server boundary, changed UI surfaces, exact validation evidence, assumptions, and residual risks; do not claim browser behavior that was not exercised.
</workflow>
