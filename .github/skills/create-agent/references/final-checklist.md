# Final checklist

Run this checklist after the validation script. Treat any unchecked line as a blocker unless you can explain why it does not apply.

```text
+----+--------------------------------+-------------------------------------------------------------+
| ID | Check                          | Pass condition                                              |
+----+--------------------------------+-------------------------------------------------------------+
| 01 | File and name                  | `.github/agents/<slug>.agent.md` and frontmatter `name` match |
| 02 | Discovery text                 | `description` uses WHAT, INVOKE FOR, and DO NOT INVOKE FOR  |
| 03 | Primitive choice                | The request needs an agent persona/tool/delegation boundary, not a skill, prompt, MCP, hook, or product implementation |
| 04 | Runtime source                  | One `.agent.md` contains routing, workflow, refusal, delegation, and output; siblings are authoring guidance only |
| 05 | Tool surface                   | Every tool is necessary, valid, and no broader than needed  |
| 06 | Delegation boundary            | `agent` and `agents:` agree, or both are omitted intentionally |
| 07 | Step 0 routing                 | Ordinary agents embed one dense decision matrix; direct-user orchestrator uses the documented no-Step-0 exception |
| 08 | Refusal payload                | Step 0 rejects mismatches with the full refusal JSON        |
| 09 | Body contract                  | Definitions, workflow, Role, rules, and Steps 1-3 stay canonical |
| 10 | Forbidden work                 | Constraints and output contract block adjacent drift        |
| 11 | Invocation mode                | `user-invocable` and `disable-model-invocation` are deliberate |
| 12 | Example prompt                 | The final summary gives one prompt that should route correctly |
+----+--------------------------------+-------------------------------------------------------------+
```