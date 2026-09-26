# Final checklist

Run this checklist after the validation script. Treat any unchecked line as a blocker unless you can explain why it does not apply.

```text
+----+--------------------------------+-------------------------------------------------------------+
| ID | Check                          | Pass condition                                              |
+----+--------------------------------+-------------------------------------------------------------+
| 01 | File and name                  | `.github/agents/<slug>.agent.md` by default, or the handoff's pack path; frontmatter `name` matches |
| 02 | Discovery text                 | `description` uses WHAT, INVOKE FOR, and DO NOT INVOKE FOR  |
| 03 | Primitive choice                | The request needs an agent persona/tool/delegation boundary, not a skill, prompt, MCP, hook, or product implementation |
| 04 | Runtime source                  | One `.agent.md` contains role, workflow, delegation, invocation, constraints, and output; siblings are authoring guidance only |
| 05 | Tool surface                   | Every tool is necessary, valid, and no broader than needed  |
| 06 | Delegation boundary            | `agent` and `agents:` agree, or both are omitted intentionally |
| 07 | Description routing             | `WHAT:`, `INVOKE FOR:`, and `DO NOT INVOKE FOR:` are clear |
| 08 | Body routing                    | `<routing>` has local ACCEPT/REJECT lists; every REJECT names an exact receiving agent |
| 09 | Priority and risk              | Critical rules, preferences, and risk are separate; Orchestrator assigns L0-L3, specialists consume it, and Step 1 applies the contract |
| 10 | Body contract                  | Optional meaningful definitions, required role sections, and separate ordered Steps 1-3 stay canonical |
| 11 | Forbidden work                 | Constraints and output contract block adjacent drift        |
| 12 | Invocation mode                | `user-invocable` and `disable-model-invocation` are deliberate |
| 13 | Example prompt                 | The final summary gives one prompt that should route correctly |
+----+--------------------------------+-------------------------------------------------------------+
```