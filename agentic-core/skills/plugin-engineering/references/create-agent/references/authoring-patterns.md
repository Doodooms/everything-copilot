# Agent authoring patterns

- `description` is the global selection surface; `<routing>` confirms local ownership and names exact receivers.
- Use `MUST`/`MUST NOT` for invariants, `SHOULD`/`SHOULD NOT` for preferences, `MAY` for optional behavior, and `DO`/`DO NOT` for workflow actions.
- Keep `<definitions>` only for terms that change routing or decisions; omission is valid.
- Include only necessary, exact tools. Add `skill` when loading packaged workflows; add `agent` only with explicit recipients in `agents:`.
- Make the output contract observable: status, evidence, artifacts, blockers, and next owner as applicable.
- Put required context and the risk assessment in Step 1; keep the workflow to Steps 1-3.

```text
Weak discovery: Helpful assistant.
Useful discovery: WHAT: [owned outcome]. INVOKE FOR: [matching tasks]. DO NOT INVOKE FOR: [adjacent work].
```
