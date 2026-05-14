# Prompt validation guide

## Purpose

- Explains what `scripts/validate_prompt.py` checks and how to fix its output.
- Use [prompt-template.md](../assets/prompt-template.md) as the canonical starting point when validation points to structural problems.

## When to use this file

- Read it after generated `.prompt.md` validation fails.
- In this repository, run the validator with `./.venv/bin/python .github/skills/create-prompt/scripts/validate_prompt.py --prompt-file <prompt_file>`.
- If `.venv` does not exist yet, or if dependencies changed, run `uv sync` from the repository root before validating.

## Automatic checks

- The file ends with `.prompt.md`.
- YAML frontmatter parses and the body is not empty.
- `description` exists and is a non-empty string.
- `description` is checked for both `What:` and `Use when:` guidance because prompt routing weakens when either part is missing.
- `name`, `argument-hint`, `agent`, `tools`, and `model` use the expected shapes when present.
- The body includes at least one top-level `#` heading.
- Longer prompt bodies without any `##` sections are reported as warnings because they become visually flat.
- Files outside `.github/prompts/` are reported as warnings because this repository defaults to workspace prompts there.

## Fix patterns

- Missing frontmatter -> add the YAML header before the body.
- Empty `description` -> write a concise sentence that states what the prompt does and when it should be chosen.
- Missing `What:` or `Use when:` -> rewrite `description` so it clearly states the job and the routing triggers.
- Missing top-level heading -> add `# Task` or another single `#` heading that frames the prompt cleanly.
- Flat long prompt body -> add short `##` sections such as `## Inputs`, `## Constraints`, or `## Output Contract`.
- Invalid `tools`, `model`, or `argument-hint` shapes -> restore the field to the supported YAML shape.
- Warning about file location -> move the file to `.github/prompts/` unless a different scope was explicitly requested.

## Status codes

- **ERROR**: must fix before the prompt is ready.
- **WARNING**: readability or routing issue that should usually be corrected.