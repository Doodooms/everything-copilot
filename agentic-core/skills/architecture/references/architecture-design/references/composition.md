# Domain modeling handoff

Use this composition only when architecture work requires changing domain terminology, a project glossary, or an ADR. Loading provides the child skill's instructions; the Architect executes its bounded workflow and retains ownership of the architecture decision.

The packet carries the objective, current requirements, relevant glossary/ADR paths, code evidence, constraints, expected status and fields, and the exact parent resume point declared by `architecture-design/SKILL.md`.

```mermaid
flowchart TD
    scope["Architecture design: identify domain or ADR question"]
    packet["Prepare bounded domain-modeling packet"]
    child["Load and execute domain-modeling"]
    validate{"Validate child status, terms, evidence, and open decisions"}
    resume["Resume architecture-design Step 2, action 4"]
    brief["Produce architecture brief"]
    blocked["Stop or return unresolved domain decision"]
    scope --> packet --> child --> validate
    validate -->|valid success| resume --> brief
    validate -->|partial, failed, or malformed| blocked
```
