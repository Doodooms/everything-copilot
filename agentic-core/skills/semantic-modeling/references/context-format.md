# Project context format

Use a single root `CONTEXT.md` when the repository has one shared domain. For distinct domains, use `CONTEXT-MAP.md` to locate each context and explain material relationships between them.

Create these files only when there is approved vocabulary to record.

```md
# {Context name}

{One concise sentence describing the domain context.}

## Language

**{Canonical term}**: {Meaning and domain boundary in one or two sentences.}
_Avoid_: {Competing term(s), only when they create ambiguity.}
```

Keep the document limited to domain meanings and relationships. Link specification or implementation details elsewhere instead of copying them into this glossary.
