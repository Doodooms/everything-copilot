# Built-in Skill Overlap Analysis

## Scope

This note compares the linked bundled Copilot skills under `./prompts/skills/` against the workspace canonical skills:

- Built-in `agent-customization`
- Built-in `create-agent`
- Built-in `create-skill`
- Workspace `create-agent`
- Workspace `create-skill`

The goal is to keep only the useful ideas and reject the parts that conflict with this repository's deterministic skill and agent model.

## Root conflict

The bundled GitHub Copilot skills centralize multiple customization primitives through one broad umbrella skill, `agent-customization`.

- Built-in `create-agent` delegates to `agent-customization` instead of owning a deterministic agent-authoring workflow.
- Built-in `create-skill` delegates to `agent-customization` instead of owning a deterministic skill-authoring workflow.
- The built-in umbrella skill mixes agents, skills, prompts, instructions, hooks, and MCP guidance into one discovery surface.

This directly conflicts with the workspace rule of one canonical home per concept.

## Structural comparison

| Surface | Bundled GitHub skills | Workspace skills |
|---------|------------------------|------------------|
| Discovery model | Broad heuristic descriptions | Narrow WHAT / USE FOR / DO NOT USE FOR routing |
| Ownership | `agent-customization` owns many primitives | `create-agent`, `create-skill`, `create-prompt`, `create-mcp` each own one primitive |
| Workflow style | Short prose checklist | Deterministic `<workflow>` with explicit steps |
| Support files | Reference-heavy but loosely governed | Point-of-need `assets/`, `references/`, `scripts/` with validation |
| Validation | Frontmatter and template advice only | Mechanical validators for skill, agent, prompt, and MCP surfaces |
| Tool references | Implicit or prose guidance | Explicit `#tool:` and `#file:` governance |
| Repo assumptions | Includes `AGENTS.md` and broad customization patterns | Health gate forbids provider artifacts like `AGENTS.md` |

## Keep / adapt / reject

| Idea | Verdict | Why |
|------|---------|-----|
| Primitive decision table | Keep and adapt | Good fast-routing aid; compact and deterministic when narrowed to workspace-supported primitives |
| Quick reference table | Keep and adapt | Useful if rewritten to match real workspace paths and forbidden-provider rules |
| `description` is the discovery surface | Keep | Matches the workspace validator and current authoring rules |
| YAML silent-failure warning | Keep | Useful operational guidance; fits template notes and validation docs |
| `applyTo: "**"` warning | Keep elsewhere | Good instruction-authoring advice, but belongs in instruction-specific guidance rather than `create-agent` or `create-skill` |
| Umbrella `agent-customization` skill | Reject | Too broad; competes with every canonical workspace create-surface skill |
| Built-in `create-agent` delegating to `agent-customization` | Reject | Creates naming collision and bypasses workspace validation workflow |
| Built-in `create-skill` delegating to `agent-customization` | Reject | Same collision pattern; weakens the canonical skill contract |
| Generic "edit directly, no skill needed" rule | Reject | Too heuristic for this repository's deterministic orchestration model |

## Best reusable pattern

The strongest import candidate is the compact decision-table pattern itself, not the bundled workflow that surrounds it.

Candidate adapted table for this workspace:

```text
| Primitive         | Use When                                      | Do Not Use When                          |
|------------------|-----------------------------------------------|------------------------------------------|
| Skill            | Reusable multi-step workflow with support files | You need a specialized persona boundary |
| Agent            | Specialized persona with explicit tools/routing | You only need a reusable procedure      |
| Prompt           | Single focused reusable task or input pattern   | You need deterministic orchestration    |
| MCP Server       | External tools, APIs, or remote capabilities    | Local repo guidance alone is enough     |
| Hook             | Deterministic lifecycle enforcement             | Non-deterministic guidance is enough    |
| File Instruction | File-scoped persistent guidance                 | The behavior is task-shaped, not file-shaped |
```

This is worth importing because it is:

- compact
- scannable
- deterministic
- compatible with the repository's one-concept-one-home rule once narrowed to local primitives

## Immediate local drift found during comparison

The comparison also exposed two local workspace issues that should be fixed before importing any new pattern.

1. `create-agent` still has a pasted Step 0 that talks about `code-reviewer` instead of its own confirmation contract.
   - See [create-agent Step 0 drift](./../skills/create-agent/SKILL.md#L30).
2. `create-agent` validation guidance still contains appended legacy content after the new self-contained guidance.
   - See [validation guide duplication](./../skills/create-agent/references/validation.md#L38).

Those are local correctness issues, not bundled-skill ideas to import.

## Recommended import targets

If we import ideas from the bundled skills, the clean targets are:

1. Add a short primitive decision table to the canonical skill-authoring guidance.
   - Best location: a new `create-skill` reference that is loaded only when the primitive is still ambiguous.
2. Add a short "discovery surface" pitfall reminder where frontmatter is authored.
   - Best location: template notes in `create-agent` and `create-skill` assets.
3. Add a short YAML-frontmatter warning where authors actually type descriptions.
   - Best location: template comments or validation guides.

## Do not import directly

Do not directly copy the bundled GitHub workflow bodies into this workspace.

Reasons:

- They route through `agent-customization`, which is the collision source.
- They assume broader provider surfaces than this repository allows.
- They do not encode the validator-backed point-of-need reference discipline used here.
- They reintroduce heuristic, multi-primitive guidance into skills that are intentionally narrow.

## Suggested next step

Fix the local `create-agent` drift first, then import only the compact primitive decision-table pattern into a narrow, non-conflicting support file.