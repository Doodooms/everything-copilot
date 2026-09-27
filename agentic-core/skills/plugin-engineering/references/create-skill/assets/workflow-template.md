```yaml
---
id: "[workflow-id]"
description: "[what this procedure does]"
invoke_for:
  - "[specific trigger]"
avoid_for:
  - "[nearby case that does not need this procedure]"
references:
  - "../references/[reference].md"
---
```

```markdown
<critical_rules>
- MUST stay within this subskill's declared procedure and authority boundaries.
- MUST NOT take over domain admission or global workflow routing from the parent skill.
</critical_rules>

<general_rules>
- SHOULD load listed references only at the procedure step that needs them.
- MAY report unavailable evidence or unresolved decisions as unknown.
</general_rules>

<risk_assessment>
Consume the Orchestrator-assigned `risk_level` through the parent domain skill; MUST NOT reclassify or downgrade it. SHOULD escalate only when new evidence materially increases risk. Scale evidence depth, not authority or approvals.
</risk_assessment>

<rules>
- MUST state this subskill's role, constraints, and expected result in the selected procedure.
- MUST return the result, evidence, remaining unknowns, risks, and status required by the procedure.
</rules>

<workflow>
## Step 1 - [specific action]
1. [Describe the procedure, its required evidence, and the relevant point-of-need references.]
</workflow>
```

Replace every bracketed field with subskill-specific content. Keep workflow metadata (`id`, `description`, `invoke_for`, `avoid_for`, and `references`) and the canonical `<critical_rules>`, `<general_rules>`, `<risk_assessment>`, `<rules>`, and `<workflow>` body structure. The file stays directly under the parent's `workflows/` directory: it is a complete subdomain expertise definition inside that package, not an independently registered Agent Skill and not a peer `SKILL.md` package. The parent domain skill remains the discoverable routing entrypoint. References contain supporting knowledge only; a distinct procedure becomes a sibling subskill or is integrated into the selected subskill.
