# Conditional package template

Start with `SKILL.md`. Add only the support directories that contain real files
consumed by the workflow. A user-profile skill follows the same rule.

Expected package shape:

- `.github/skills/<skill-name>/SKILL.md` is required. The folder name must be lowercase and hyphenated.
- `assets/` is optional and contains copyable templates or structured payloads.
- `references/` is optional and contains human guidance loaded at the point of need.
- `scripts/` is optional and contains executable checks or domain automation. Scripts must be self-contained and must not import workspace modules; they may call another skill only through an explicit skill handoff.

## Required pieces

- `SKILL.md` is the discovery surface and owns the live workflow. Without it, the skill cannot load.
- `assets/` is for reusable inputs. Do not create the directory when the workflow consumes no assets.
- `references/` is for reusable guidance or matrices. Do not duplicate that guidance in `SKILL.md`.
- `scripts/` is for skill-specific behavior. Do not add a validator stub just to populate the directory.

The repository validator checks package structure for every skill. Every support
file must be linked from `SKILL.md` and must be consumed by a workflow action.
The package must run from its own directory without relying on the repository
that created it.
