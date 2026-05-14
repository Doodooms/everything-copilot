---
description: "Use when creating or editing workspace skills, custom agents, prompts, or their linked Markdown support docs. Keeps customization Markdown human-readable with lightweight hierarchy and progressive-loading-friendly support docs."
applyTo: ".github/skills/**/*.md, .github/agents/**/*.agent.md, .github/prompts/**/*.prompt.md"
---

# Customization Markdown Structure

## Goals

- Keep human-facing customization files easy to scan without turning every file into a long outline.
- Preserve progressive loading: support docs should explain and guide, not steal focus from the skill, agent, or prompt that loads them.
- Use stronger structure only where a validator, template, or fixed contract needs it.

## Definition Files

- Keep the required contract first. If a skill, agent, or prompt template already defines the canonical sections, preserve that shape.
- Prefer one top-level `#` heading and short `##` sections when the file covers distinct concerns.
- Do not add decorative headings that duplicate nearby XML wrappers or template scaffolding.

## Support Docs

- Use one `#` title.
- If the file covers more than one concern, prefer short `##` sections such as `## Purpose`, `## When to use this file`, `## How to use it`, `## Mapping`, `## Fix patterns`, `## Examples`, or `## Status codes`.
- Avoid bare labels such as `Purpose` or `When to use this file` on a line by themselves followed by bullets.
- Keep sections brief. If the file is only one short concern, a title plus bullets is enough.
- Use markdown links for files and inline tool names in support docs. Active `#tool:` and `#file:` markers stay reserved for frontmatter-bearing definition files.

## Emphasis

- Use bold only for scanning-critical lead terms, status words, or field names.
- Prefer normal title case headings over all-caps headings unless the status term itself is fixed.
- Keep lists flat and direct.

## Anti-patterns

- Flat support docs with no headings beyond the title.
- Decorative bolding on nearly every line.
- Long paragraphs where short sections would scan faster.
- Turning a 5-line support doc into a 10-heading outline.