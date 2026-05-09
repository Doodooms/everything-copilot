# Memory Vault Templates

## Decision Record Template (decisions/YYYY-MM-DD-<slug>.md)

```markdown
---
type: decision
date: YYYY-MM-DD
status: accepted | proposed | deprecated | superseded
tags: [architecture, agents, security, ...]
related: [[learnings/<slug>]], [[glossary/<term>]]
---
# <Title as a claim>

## Context
<What situation forced this decision? What constraints exist?>

## Decision
<The exact choice made. Be specific and unambiguous.>

## Consequences
- Positive: <what improves>
- Negative: <what gets harder>
- Risk: <what could go wrong>
```

## Learning Template (learnings/<slug>.md)

```markdown
---
type: learning
date: YYYY-MM-DD
confidence: 0.0-1.0
domain: <agents|architecture|testing|security|...>
tags: [...]
related: [[decisions/<slug>]]
---
# <Pattern as a claim sentence>

## Trigger
<When does this pattern apply? What problem does it solve?>

## Pattern
<Exact steps or rules to follow.>

## Evidence
<Where was this validated? How many times?>

## Counter-examples
<When does this pattern NOT apply?>
```

## Blocker Template (blockers/<slug>.md)

```markdown
---
type: blocker
date: YYYY-MM-DD
status: open | resolved | wont-fix
tags: [...]
---
# <Blocker as a question or obstacle>

## Context
<What are you trying to do? Why is this a blocker?>

## Attempts
- <What was tried>: <result>

## Next steps
<What would unblock this?>

## Resolved (fill in when done)
Date: YYYY-MM-DD
Resolution: <How was it resolved?>
```

## Glossary Entry Template (glossary/<term>.md)

```markdown
---
type: glossary
related: [[decisions/<slug>]], [[learnings/<slug>]]
---
# <Term>

<One-sentence definition>

## Usage in this project
<How this term is specifically used here, if it differs from general usage.>

## Related terms
[[glossary/<related-term>]]
```

## INDEX.md Template

```markdown
# Memory Vault Index
<!-- Read this FIRST in every session to expand query vocabulary -->

## Vocabulary
- <term>: [[glossary/<term>]]

## Recent Decisions
- YYYY-MM-DD: [[decisions/<slug>]] -- one-line summary

## Active Work
- [[active/current-session]]

## Key Learnings
- [[learnings/<slug>]] -- one-line summary

## Open Blockers
- [[blockers/<slug>]] -- one-line description
```

## Session Template (active/current-session.md)

```markdown
---
date: YYYY-MM-DD
task: <task id or description>
---
# Current Session

## Goal
<What are we doing this session?>

## Context Loaded
- [x] INDEX.md
- [ ] decisions/<relevant>
- [ ] learnings/<relevant>

## Progress
<In-progress notes>

## Next Steps
1. <step>
2. <step>

## To Persist
<Facts to write to decisions/ or learnings/ at end of session>
```
