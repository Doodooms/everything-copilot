# Skill authoring patterns

- Keep `description` as the global discovery surface; put shared admission and expertise in `SKILL.md`, and each distinct same-domain procedure in an immediate workflow.
- Use `MUST`/`MUST NOT` for invariants, `SHOULD`/`SHOULD NOT` for preferences, `MAY` for optional behavior, and `DO`/`DO NOT` for local actions.
- Use ordered lists for procedure and tables only to compare matching dimensions.
- Link knowledge, assets, and scripts at the step that consumes them; load support only when needed. Never hide a second procedure behind a reference.
- Use exact `#tool:` and `#file:` markers only in active skill, agent, or prompt bodies. Support Markdown uses ordinary links and tool names.
- For agent/skill composition, pass bounded objective, inputs, constraints, expected output, and resume point; validate the child's return before resuming.

The routing depth is `Agent → Skill → Workflow → Reference / Asset / Tool`. The workflow contains the method; references contain knowledge, examples, or data only.

```text
Weak discovery: API helper.
Useful discovery: WHAT: [domain capability]. USE FOR: [matching work]. DO NOT USE FOR: [adjacent work].
```
