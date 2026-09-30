---
name: capture-source
description: Capture a Foam source note while preserving its URL, provenance, and uncertainty.
---

# Capture Source

Create or update a source note under `sources/` using the Foam MCP server's ordinary resource tools.

## Procedure

1. Preserve the source URL, title, author/date when available, and how the source was provided. Keep unavailable fields unknown; do not fabricate metadata.
2. Record a concise summary separately from direct quotations. Preserve exact quotation boundaries and identify interpretation as interpretation. Keep unresolved or unverified claims explicitly uncertain.
3. Read an existing candidate before creating. For a new note, create the resource and then write its full content with `update_resource`; `create_resource` does not accept initial content.
4. Add `source_kind`, status, project properties, and wikilinks only when justified. Use an unexplored state when the source has not been evaluated.
5. Read the saved resource back and verify the URL/provenance and content. Report the note URI and any research still needed.

## Research boundary

Use the canonical Agentic Core research skill only when answering a substantive question requires research. Source capture alone does not require research. Do not create a separate GitHub research skill.

## Boundaries

- Do not create Control objects or promote ideas implicitly.
- Do not consume Inbox entries; `process-inbox` owns that sequence and requires successful destination readback.
- Keep Foam queries and graph operations as direct MCP primitives.
