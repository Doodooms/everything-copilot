---
name: architecture-design
description: "WHAT: Produce a grounded architecture brief and implementation blueprint before coding begins. USE FOR: system design, file-level change planning, ADR candidates, dependency sequencing, and structural tradeoff analysis. DO NOT USE FOR: writing production code, reviewing diffs, bug fixing, or general documentation maintenance."
user-invocable: false
metadata:
  creation-date: 2026-05-14
  creator: Doodooms
---

<definitions>

- **architecture brief** : A compact design artifact that names the target files, responsibilities, risks, tradeoffs, and execution order for a proposed change.

</definitions>

<workflow>

## Step 0 - **CONFIRMATION**

1. USE #tool:read **IMMEDIATELY** on #file:./references/USEFOR.md and **IMMEDIATELY** on #file:./references/DONOTUSEFOR.md to confirm with certainty if this skill should be used.
2. Now read the following rules and workflow steps to understand how the skill works and what it requires for execution.

<rules>

- Keep the design grounded in existing repository patterns.
- Separate architecture decisions from implementation details.
- Reference support files only at the point of need.

</rules>

## Step 1 - Inspect the current structural context.

1. Use #tool:read on the existing plan, owning files, and nearby architecture notes.
2. Use #tool:search to locate the controlling modules, shared boundaries, and integration points.
3. Use #tool:read on #file:./references/guide.md only if the architecture checklist is still needed.

## Step 2 - Produce the architecture brief and implementation blueprint.

1. Name the target files, responsibilities, dependencies, and build order.
2. State the tradeoffs, risks, and alternatives only where they affect the chosen design.
3. Keep the output concrete enough that a planner or implementer can act without reopening structural discovery.

## Step 3 - Check the proposed structure before returning it.

1. Use #tool:search to confirm the referenced file paths and patterns actually exist.
2. Return the architecture brief with assumptions, non-goals, and follow-up risks explicit.

</workflow>