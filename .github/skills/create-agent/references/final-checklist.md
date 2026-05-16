# Final checklist

Run this checklist after the validation script. Treat any unchecked line as a blocker unless you can explain why it does not apply.

```text
+----+--------------------------------+-------------------------------------------------------------+
| ID | Check                          | Pass condition                                              |
+----+--------------------------------+-------------------------------------------------------------+
| 01 | File and name                  | `.github/agents/<slug>.agent.md` and frontmatter `name` match |
| 02 | Discovery text                 | `description` uses WHAT, USE FOR, and DO NOT USE FOR        |
| 03 | Tool surface                   | Every tool is necessary, valid, and no broader than needed  |
| 04 | Delegation boundary            | `agent` and `agents:` agree, or both are omitted intentionally |
| 05 | Step 0 routing                 | Step 0 embeds `### USE FOR` and `### DO **NOT** USE FOR`    |
| 06 | Refusal payload                | Step 0 rejects mismatches with the full refusal JSON        |
| 07 | Body contract                  | Definitions, workflow, Role, rules, and Steps 1-3 stay canonical |
| 08 | Forbidden work                 | Constraints and output contract block adjacent drift        |
| 09 | Invocation mode                | `user-invocable` and `disable-model-invocation` are deliberate |
| 10 | Example prompt                 | The final summary gives one prompt that should route correctly |
+----+--------------------------------+-------------------------------------------------------------+
```