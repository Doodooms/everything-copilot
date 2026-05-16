# Mandatory package template

Use this workspace shape unless the user explicitly asks for a user-profile skill instead of a workspace skill.

```text
.github/skills/<skill-name>/ (<skill-name> must be lowercase, no spaces)
├── SKILL.md           # Required skill definition file with YAML frontmatter and Markdown content
├── scripts/           # Required executable validation or automation
├── references/        # Required guidance loaded at point of need
└── assets/            # Required templates or machine-readable payloads
```

## Required pieces

```text
+-------------+--------------------------------------+---------------------------------------------+
| Piece       | Purpose                              | Missing means                               |
+-------------+--------------------------------------+---------------------------------------------+
| SKILL.md    | Discovery surface plus live workflow | No skill can load or execute                |
| assets/     | Templates and structured payloads    | Reusable inputs leak into prose or vanish   |
| references/ | Human guidance and matrices          | Explanations get duplicated in SKILL.md     |
| scripts/    | Validators or small automation       | No executable quality gate exists           |
+-------------+--------------------------------------+---------------------------------------------+
```

If a directory would otherwise be empty, add the smallest real artifact that closes the gap, such as a validator stub, a question payload, or a short reference guide.
