# Optional Detailed Workflow Fragment

Use this copyable fragment only when a role needs a more specific sequence than the basic workflow in `agent-template.md`. Replace every bracketed placeholder before using it. Keep `<routing>` and `<rules>` in the canonical agent template; this fragment supplies only `<workflow>`.

```markdown
<workflow>

## Step 1 - [gather required context]

1. DO assess and assign task risk if this is the Orchestrator; otherwise consume the assigned `risk_level`. Inspect [the exact inputs, evidence, repository surfaces, and constraints needed before acting].
   - [specific sub-check or exception]

## Step 2 - [apply the role method]

1. DO [perform the primary role-specific action].
   - [branch or condition that remains within this role]
2. DO [validate the result against the accepted task and its evidence].

## Step 3 - [return the handoff]

1. DO [return the promised output fields, evidence, blockers, and next owner].

</workflow>
```
