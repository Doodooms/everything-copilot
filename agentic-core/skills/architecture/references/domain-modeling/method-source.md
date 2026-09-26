---
name: domain-modeling
description: "WHAT: Sharpen project-specific domain language and record durable domain decisions. USE FOR: resolving terminology, creating or updating a CONTEXT.md glossary or map, or deciding and recording an ADR. DO NOT USE FOR: generic code concepts, implementation design, or unresolved product decisions."
user-invocable: false
metadata:
  creation-date: 2026-09-24
  creator: Doodooms
---

<definitions>

- **domain term**: A project-specific concept whose meaning, relationships, states, or boundaries affect product behavior.
- **project context**: The shared vocabulary and relationships that let contributors describe the domain consistently; it is not a specification or implementation manual.
- **architecture decision record (ADR)**: A concise record of a material structural or product-domain tradeoff and the reason for the chosen option.

</definitions>

<admission>

## ACCEPT

- Resolve project-specific terms or domain relationships using existing context and code evidence.
- Create or update the project's `CONTEXT.md` / `CONTEXT-MAP.md` vocabulary.
- Decide whether a material, durable tradeoff warrants an ADR, or record an approved ADR.

## REJECT

- Unresolved product intent or an unapproved domain decision -> `orchestrator`.
- System topology, interface, or technology ownership -> `architect` using `architecture-design`.
- Delivery decomposition or task ownership -> `planner`.
- Implementation or defect repair -> `implementer`.
- Final acceptance -> `reviewer`.

For REJECT, return exactly:

```json
{"status":"rejected","skill":"domain-modeling","reason":"<concise reason>","routing":"<route or null>"}
```

</admission>

<rules>

- MUST use project-specific concepts; generic programming terminology belongs in code or technical documentation, not the domain glossary.
- A glossary entry MUST state the agreed meaning concisely and SHOULD list likely competing terms under `Avoid` when that prevents ambiguity.
- MUST compare proposed terminology with existing context documents, requirements, and relevant code. A contradiction is evidence to reconcile, not permission to silently overwrite one source.
- MUST NOT invent domain facts or resolve a user-owned product decision. Return the competing interpretations and the exact unresolved decision.
- A `CONTEXT.md` MUST record vocabulary and domain relationships only; MUST NOT become a specification, scratchpad, architecture manual, or implementation inventory.
- Create context and ADR directories only when a real, approved entry is ready to write.
- MUST respect the invoking agent's role, approved file scope, and available tools. If it does not own documentation edits or lacks an edit tool, return proposed content to the authorized owner instead of claiming to have written it.
- Record an ADR only when all are true: changing the choice later is materially costly, future readers would not infer the decision, and a real alternative was selected for a reason.
- Keep ADRs concise. Add status, alternatives, or consequences only when they preserve decision-relevant context.
- MUST preserve repository naming, numbering, and existing document structure.

</rules>

<workflow>

## Step 1 - Establish the existing domain record.

1. Use #tool:read to inspect the approved domain question, relevant requirements, and code or product evidence.
2. Use #tool:search to locate `CONTEXT-MAP.md`, `CONTEXT.md`, nearby ADRs, and existing terminology before proposing new terms.

## Step 2 - Resolve terms and decision boundaries.

1. For each material term, state its candidate meaning, neighboring concepts, relationships, and alternatives; use #tool:read and #tool:search to test the distinction against concrete product scenarios and relevant code.
2. If evidence or existing documents conflict, describe the contradiction and return the smallest unresolved question to the product decision owner; do not write an assumed meaning.
3. For a proposed ADR, verify the three decision criteria in the rules and identify the approved choice and rationale. Do not create an ADR for routine, reversible, or self-evident changes.

## Step 3 - Record and hand off.

1. When the meaning or decision is approved, read [the context format](./references/CONTEXT-FORMAT.md) before proposing or editing a glossary, or [the ADR format](./references/ADR-FORMAT.md) before proposing or recording an ADR.
2. If the handoff authorizes domain-document edits and the current agent has the required tool, use #tool:edit only on the in-scope document; otherwise return the exact proposed content and intended path to the authorized owner.
3. Verify terminology against neighboring entries and relevant evidence; confirm a glossary contains no implementation detail and an ADR records only the approved tradeoff.
4. Return the resolved terms, code/document evidence, proposed or changed content, changed files, ADR rationale or reason no ADR was warranted, unresolved items, and the next owner.

</workflow>

Source provenance: [original specification](./references/original-spec.md).
