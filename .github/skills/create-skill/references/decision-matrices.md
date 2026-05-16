# Decision matrices

Use these matrices only when the primitive, scope, or invocation mode is still unclear after the Step 0 confirmation matrix. Do **NOT** duplicate the Step 0 yes or no routing boundary here.

## Primitive selection

```text
+-----------------------------------------------+--------------+----------------------------------------------+
| Need                                          | Choose       | Why                                          |
+-----------------------------------------------+--------------+----------------------------------------------+
| Repeatable workflow with bundled references   | Skill        | Same procedure each time, support files fit  |
| One focused task with parameterized input     | Prompt       | Single invocation, not a bundled workflow    |
| Context isolation or tool restrictions        | Agent        | Separate tool surface or staged handoff      |
| Always-on project policy                      | Instructions | Guidance should apply continuously           |
| External systems, APIs, or tool resources     | MCP server   | New executable capability is required        |
| Deterministic lifecycle shell gate            | Hook         | Policy must run automatically, not by choice |
+-----------------------------------------------+--------------+----------------------------------------------+
```

## Scope selection

```text
+-----------------------------------------------+----------------------+----------------------------------------------+
| Constraint                                    | Choose               | Why                                          |
+-----------------------------------------------+----------------------+----------------------------------------------+
| Team-shared repository behavior               | Workspace skill      | Lives with the repo and travels with it      |
| Personal workflow across many repositories    | User-profile skill   | Avoids coupling to one workspace             |
| Unsure, but the current repo needs it now     | Workspace skill      | Start where the problem exists               |
| Purely private experiment                     | User-profile skill   | Keep noise out of the shared repository      |
+-----------------------------------------------+----------------------+----------------------------------------------+
```

## Access-mode selection

```text
+--------------------------------+-----------------------------------------------+----------------------------------------------+
| Need                           | Frontmatter choice                             | Result                                       |
+--------------------------------+-----------------------------------------------+----------------------------------------------+
| Auto-load, hide from slash     | user-invocable: false                          | Background skill                             |
| Slash command only             | disable-model-invocation: true                 | On-demand skill                              |
| Both slash and auto-load       | Omit both flags                                | General-purpose skill                        |
| Disabled placeholder           | user-invocable: false plus disable-model-invocation: true | Usually avoid                     |
+--------------------------------+-----------------------------------------------+----------------------------------------------+
```

Use ASCII tables for contrastive choices like these. Keep the actual executable workflow in markdown headings and ordered steps.