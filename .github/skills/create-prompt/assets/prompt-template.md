```yaml
---
description: "What: <one-sentence prompt job>. Use when: <scenarios or trigger phrases that should make this prompt relevant>."
# name: Prompt Name
# argument-hint: "Optional hint shown in the chat input"
# agent: agent
# model: GPT-5.4 (copilot)
# tools: [read, search]
---
```

```markdown
# Task

State the single task this prompt should perform.

## Inputs

- Name the user argument, selected code, files, or workspace context this prompt expects.
- Omit this section when the prompt is only one short instruction with obvious inputs.

## Constraints

- Keep the task focused.
- Name any required style, scope, or safety boundaries.

## Output Contract

- Describe exactly what the prompt should produce.
- Name any required sections, fields, or formatting expectations.
```

Notes

- Keep the body direct. A prompt is a task request, not a multi-step workflow.
- Use one `#` heading and short `##` sections when the prompt covers multiple concerns.
- Keep `description` strong enough to route the prompt without reading the body first.
- Add `tools`, `agent`, `model`, or `argument-hint` only when they materially improve execution.