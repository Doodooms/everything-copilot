```yaml
---
name: "[skill-name]"
description: "WHAT: [capability]. USE FOR: [matching tasks]. DO NOT USE FOR: [nearest out-of-scope tasks]."
user-invocable: true
metadata:
  creation-date: "[YYYY-MM-DD]"
  creator: "[author]"
# disable-model-invocation: true # Only for slash-command-only skills.
# context: fork                 # Use for lengthy or multi-step work.
# compatibility: [host/version] # Add when behavior is version-gated.
# license: [license]            # Optional.
---
```

```markdown
<!-- Optional: retain only decision-relevant terms; omit this block when none are needed. -->
<definitions>
- **[decision-relevant term]** : [meaning in this domain]
</definitions>

<critical_rules>
- MUST preserve [authority, admission, and rejection contract].
- MUST NOT [forbidden scope or failure behavior].
</critical_rules>

<general_rules>
- SHOULD [preference with its reasonable exception].
- MAY [optional behavior and when it applies].
</general_rules>

<risk_assessment>
Consume the Orchestrator-assigned `risk_level`; MUST NOT reclassify or downgrade it. SHOULD escalate only when new evidence materially increases risk. Scale evidence depth, not authority or approvals.
</risk_assessment>

<rules>
- MUST use `MUST`/`MUST NOT` for invariants, `SHOULD`/`SHOULD NOT` for preferences, `MAY` for optional behavior, and `DO`/`DO NOT` for local actions.
- Keep admission, routing, and essential shared invariants here; put each specialized procedure in an immediate `workflows/` child and substantive domain expertise in point-of-need references. Every immediate subskill MUST use the same `<critical_rules>`, `<general_rules>`, `<risk_assessment>`, `<rules>`, and `<workflow>` body structure and contain its actual specialized procedure. Its workflow metadata does not make it an independently registered Agent Skill or a global route. References are supporting knowledge, never hidden workflow layers.
</rules>

<workflow>
## Workflow routing (omit when there are no specialized procedures)
- [task condition] → [workflow](./workflows/[workflow-id].md)

## Step 1 - [inspect or prepare]
1. DO consume the assigned `risk_level`, then inspect [the required inputs, evidence, and constraints].
   - Load [reference](./references/[guide].md) only if this step needs it.
## Step 2 - [decide or apply the method]
1. [Resolve the key decision or perform the domain procedure.]
   - Use #tool:vscode/askQuestions with #file:./assets/ask_questions.json only for material missing input.
## Step 3 - Validate and return.
1. Use #tool:execute on [the narrowest validation command]; return [evidence, risks, and status].
   - For a distinct installed domain skill, use the host's native skill mechanism.
   - For a distinct procedure in this domain, route to its immediate workflow; do not create a nested workflow or method-source layer.
   - Before composing an agent or skill, bound `objective`, `inputs`, `constraints`, `expected_output`, and [resume point]; validate the child's status and fields before resuming.
</workflow>
```

Replace every `[placeholder]` and remove unused optional fields, comments, and sections. Keep `SKILL.md` concise and self-contained; include only support files consumed by a step. Templates and detailed examples are in [authoring patterns](../references/authoring-patterns.md).
