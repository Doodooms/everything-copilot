```yaml
---
id: "[workflow-id]"
description: "[what this procedure does]"
invoke_for:
  - "[specific trigger]"
avoid_for:
  - "[nearby case that does not need this procedure]"
references:
  - "../references/[reference].md"
---
```

```markdown
## Step 1 - [specific action]
1. [Describe the procedure, its required evidence, and the relevant point-of-need references.]
```

Replace every bracketed field. Keep the file directly under `workflows/`; it is the complete specialized procedure in its parent skill package, not a wrapper around another method. References contain supporting knowledge only. A distinct procedure becomes a sibling workflow or is integrated into the selected workflow.
