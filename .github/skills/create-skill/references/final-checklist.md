# Final checklist

Run this checklist after the validation script. Treat any unchecked line as a blocker unless you can explain why it does not apply.

```text
+----+--------------------------------+-------------------------------------------------------------+
| ID | Check                          | Pass condition                                              |
+----+--------------------------------+-------------------------------------------------------------+
| 01 | Name and folder                | `name` matches the skill folder exactly                     |
| 02 | Discovery text                 | `description` uses WHAT, USE FOR, and DO NOT USE FOR        |
| 03 | Metadata                       | `metadata` exists and records authorship or provenance      |
| 04 | Package shape                  | SKILL.md, assets/, references/, and scripts/ all exist      |
| 05 | Workflow structure             | Step 0 confirms scope and later steps start with ordered 1. |
| 06 | Point-of-need references       | Support files are cited only where the workflow uses them   |
| 07 | Support-doc hygiene            | No active #tool or #file markers appear in support markdown |
| 08 | Contrastive docs placement     | Each decision surface has one dense matrix in refs or assets |
| 09 | Access mode                    | user-invocable and disable-model-invocation are deliberate  |
| 10 | Compatibility                  | `compatibility` exists when `context: fork` or newer tools or behavior are used |
| 11 | Validation output              | Errors are fixed and warnings were reviewed intentionally   |
| 12 | Example invocation             | The final summary names one concrete way to invoke the skill |
+----+--------------------------------+-------------------------------------------------------------+
```