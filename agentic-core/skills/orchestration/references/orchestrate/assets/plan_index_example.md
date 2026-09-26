## Optional plan context index

For unusually large plans, an agent MAY generate a compact index to locate relevant sections/files without rereading the full document. This is optional context optimization, not a required manifest field or independent source of truth.

```
Repository structure:
- src/datasets/   # dataset loaders, transforms, datamodules
- src/models/     # model implementations (teacher, student)
- src/training/   # training CLI and callbacks
- tests/units/     # unit tests
```

The Orchestrator should pass only the relevant paths and plan sections in each handoff packet. Do not generate or send this index when the task is small enough to inspect directly.
