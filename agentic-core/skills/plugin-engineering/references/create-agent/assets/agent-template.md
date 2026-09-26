```yaml
---
name: "[agent-slug]"
description: "WHAT: [unique role and outcome]. INVOKE FOR: [admitted work]. DO NOT INVOKE FOR: [nearest out-of-scope work]."
target: vscode
tools: [read, search]            # Add only needed tools; add `skill` for packaged workflows.
# model: [model]                 # Pin only when needed.
# reasoning-effort: [effort]     # Static role default; reserve max for exceptional roles.
# agents: [[recipient-id]]       # If present, allowlist exact recipients and include `agent` in tools.
user-invocable: false            # Choose deliberately.
# user-invocable: true           # Example for a directly user-invocable agent.
# argument-hint: "[short hint]"  # Optional picker hint.
# disable-model-invocation: true # Only when subagent invocation is forbidden.
---
```

```markdown
<!-- Optional: keep definitions only for terms that materially affect decisions; otherwise omit this block. -->
<definitions>
- **[decision-relevant term]** : [meaning in this agent's domain]
</definitions>

<routing>
## ACCEPT
- [admitted task] → this agent.
## REJECT
- [out-of-scope task] → `[exact-agent-id]`.
</routing>

<critical_rules>
- MUST [non-negotiable authority, scope, or safety invariant].
- MUST NOT [forbidden action or invalid success condition].
</critical_rules>

<general_rules>
- SHOULD [preferred method, including when an exception is reasonable].
</general_rules>

<risk_assessment>
[Orchestrator: assess impact/blast radius, reversibility, security/data exposure, external contracts, and uncertainty; assign and record the highest applicable level: L0 isolated/reversible, L1 bounded to one component, L2 cross-component/contract/migration, or L3 high-impact/sensitive/destructive/hard to reverse. Specialist: consume the assigned `risk_level`; MUST NOT downgrade it; SHOULD escalate only when new evidence warrants it.]
</risk_assessment>

<rules>
## Role
[State the durable role and boundary.]
## Responsibilities
- [Name work owned by this role.]
## Constraints
- [Name adjacent work and tool/delegation limits.]
## Output Contract
- [List exact status, evidence, artifacts, blockers, and next-owner fields.]
</rules>

<agent-skills>
- [MUST|SHOULD|MAY] load `[skill name]` when [specific condition]; select `[workflow]`.
<!-- Replace with relevant policies, or state that no default skill is prescribed. -->
</agent-skills>

<workflow>
## Step 1 - Gather and route.
1. Assign risk if this agent owns coordination; otherwise consume `risk_level`. Resolve matching skill policies and inspect [required inputs, evidence, and constraints].
## Step 2 - Perform the role.
1. [Apply the role-owned method and validate its result.]
## Step 3 - Return the handoff.
1. [Return the output contract, evidence, blockers, and next owner.]
</workflow>
```

Replace every `[placeholder]`, remove unused optional fields and instructional comments, and omit `<definitions>` unless its terms materially affect routing or decisions. Keep the runtime contract in one `.agent.md`; examples and authoring advice are in [authoring patterns](../references/authoring-patterns.md).
