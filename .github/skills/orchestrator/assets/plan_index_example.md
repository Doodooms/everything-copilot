## Plan repo-structure example

This is an example repo-structure block that can appear at the start of the plan and be referenced by `plan_index`.

```
Repository structure:
- src/datasets/   # dataset loaders, transforms, datamodules
- src/models/     # model implementations (teacher, student)
- src/training/   # training CLI and callbacks
- tests/units/     # unit tests
```

The Orchestrator will include a compact `plan_index` mapping to this block when sending payloads to subagents.
