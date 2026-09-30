---
name: materialize-idea
description: Create or update a Foam ideas note with justified metadata and honest uncertainty.
---

# Materialize Idea

Create or update an idea note under `ideas/` using the Foam MCP server's ordinary resource tools.

## Procedure

1. Identify the idea and its source text. Preserve quoted/source wording verbatim when it is material; separate it from summaries or interpretation.
2. Read the candidate note if one exists. Update it rather than creating a duplicate. Otherwise create the resource under `ideas/` with justified properties, then write the complete note using `update_resource`; `create_resource` does not accept initial content.
3. Use only metadata supported by the source. Preserve `status: fuzzy` when the idea is not yet sufficiently understood. Add project properties or wikilinks only when evidence supports them; do not guess links.
4. Read the resulting resource back and verify its content, properties, source provenance, and status. Report the resource URI and any unresolved uncertainty.

## Boundaries

- Do not create, promote, or update Control objects implicitly.
- Do not convert an uncertain idea into a task, decision, or commitment.
- Do not consume an Inbox entry; `process-inbox` owns that sequence and must verify durable materialization first.
