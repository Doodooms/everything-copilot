# Conditional package shape

```text
[skill-directory]/
├── SKILL.md                       # Required discovery and workflow routing.
├── workflows/[workflow-id].md    # Optional direct procedures.
├── references/[topic].md         # Optional point-of-need knowledge.
├── assets/[reusable-input]       # Optional templates or structured payloads.
└── scripts/[domain-tool]         # Optional self-contained package automation.
```

Start with `SKILL.md`; add only directories with files consumed by a workflow step. Workflows MUST be immediate children routed from `SKILL.md` and contain the complete method; references contain supporting knowledge only. Scripts MUST NOT import workspace modules.
