from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import typer
import yaml


FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.DOTALL)
STEP_HEADING_PATTERN = re.compile(r"^##\s+Step\s+(\d+)\b", re.IGNORECASE)
REQUIRED_SKILL_BLOCKS = ("rules", "workflow")
REQUIRED_POLICY_BLOCKS = ("critical_rules", "general_rules", "risk_assessment")
CONTEXT_ONLY_TOOL_NAMES = {
    "read",
    "search",
    "search/codebase",
    "search/usages",
}
SUPPORT_FILE_PREFIXES = (
    "./references/",
    "./assets/",
    "./scripts/",
    "./workflows/",
    "../references/",
    "../assets/",
    "../scripts/",
    "../workflows/",
)
WORKFLOW_ID_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
WORKFLOW_METADATA_KEYS = {
    "id",
    "description",
    "invoke_for",
    "avoid_for",
    "references",
}
TEMPLATE_LEFTOVER_MARKERS = {
    "[skill-name]": "Unresolved template placeholder `[skill-name]` found; replace it with the actual skill name.",
    "[what this skill does]": "Unresolved template placeholder `[what this skill does]` found; replace it with the actual skill purpose.",
    "[trigger phrases or scenarios that should cause the agent to load this skill]": "Unresolved template placeholder for discovery text found; replace it with real trigger phrases.",
    "[inspect or prepare]": "Unresolved workflow step placeholder `[inspect or prepare]` found; replace template step titles with concrete steps.",
    "[describe what this step must inspect or prepare before later work can be correct]": "Unresolved workflow placeholder found; replace it with the actual inspection or preparation requirement.",
    "[ask or decide]": "Unresolved workflow step placeholder `[ask or decide]` found; replace template step titles with concrete steps.",
    "[describe the missing decision, ambiguity, or structured input this step resolves]": "Unresolved workflow placeholder found; replace it with the actual decision or missing input this step resolves.",
    "[validate or execute]": "Unresolved workflow step placeholder `[validate or execute]` found; replace template step titles with concrete steps.",
    "[describe the concrete outcome this validation or execution step must produce before the workflow can finish]": "Unresolved workflow placeholder found; replace it with the actual validation or execution outcome.",
    "./references/[guide].md": "Template file reference `./references/[guide].md` found; replace it with a real support-file path or remove it.",
    "./assets/[questions].json": "Template file reference `./assets/[questions].json` found; replace it with a real support-file path or remove it.",
    "./scripts/[validator].py": "Template file reference `./scripts/[validator].py` found; replace it with a real validator path or remove it.",
    "./workflows/[workflow-id].md": "Template workflow reference found; replace it with a real workflow path or remove it.",
}
EXPECTED_AGENT_TEMPLATE_POST_HEADINGS = [
    "Authoring Notes",
    "Discovery and routing example",
    "Workflow specificity example",
    "Delegation boundary example",
    "Output contract example",
]
EXPECTED_SKILL_TEMPLATE_POST_HEADINGS = [
    "Authoring Notes",
    "Discovery and routing example",
    "Duplicate logic example",
    "List versus table example",
    "Point-of-need reference example",
    "Choosing `#file:` versus markdown links",
    "Early-context front-loading example",
    "Support-doc marker example",
]
CANONICAL_CREATE_SURFACE_SKILL_NAMES = {
    "plugin-engineering",
}
MAX_POST_WORKFLOW_CONTENT_LINES = 20
GENERIC_DUPLICATE_CONCEPTS = {
    "when to use",
    "when not to use",
    "official resources",
    "validation",
    "purpose",
    "notes",
}
CONCEPT_TOKEN_STOPWORDS = {
    "and",
    "below",
    "code",
    "docs",
    "example",
    "examples",
    "file",
    "files",
    "for",
    "from",
    "guide",
    "guides",
    "how",
    "into",
    "not",
    "only",
    "or",
    "resource",
    "resources",
    "section",
    "sections",
    "the",
    "this",
    "those",
    "through",
    "use",
    "when",
    "with",
}


@dataclass
class LintResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)

    def extend(self, other: "LintResult") -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)


def _print_result(result: LintResult) -> None:
    if result.errors:
        typer.echo("ERRORS:")
        for error in result.errors:
            typer.echo(f"  - {error}")
    if result.warnings:
        typer.echo("WARNINGS:")
        for warning in result.warnings:
            typer.echo(f"  - {warning}")


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    normalized = text.replace("\r\n", "\n").lstrip("\ufeff")
    match = FRONTMATTER_PATTERN.match(normalized)
    if not match:
        raise ValueError("Missing YAML frontmatter delimited by --- markers.")

    raw_frontmatter, body = match.groups()
    try:
        data = yaml.safe_load(raw_frontmatter) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Frontmatter is not valid YAML: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("Frontmatter must parse to a YAML mapping.")

    return data, body.strip()


def _normalize_agent_heading(text: str) -> str:
    return re.sub(r"[*_`]+", "", text).strip().upper()


def iter_markdown_headings(text: str):
    in_code_block = False
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if re.match(r"^#{1,6}\s+", line):
            yield re.sub(r"^#{1,6}\s+", "", line).strip()


def normalize_heading(heading: str) -> str:
    heading = heading.strip().lower()
    heading = re.sub(r"^step\s+\d+\s*[-: ]\s*", "", heading)
    heading = re.sub(r"\s+", " ", heading)
    return heading


def contains_runtime_inputs_heading(text: str) -> bool:
    for heading in iter_markdown_headings(text):
        if normalize_heading(heading) == "runtime inputs":
            return True
    return False


def has_block_tag(text: str, tag_name: str) -> bool:
    return f"<{tag_name}>" in text and f"</{tag_name}>" in text


def extract_workflow_text(text: str) -> str | None:
    match = re.search(r"<workflow>(.*?)</workflow>", text, re.DOTALL | re.IGNORECASE)
    if not match:
        return None
    return match.group(1)


def iter_workflow_steps(text: str):
    workflow_text = extract_workflow_text(text)
    if not workflow_text:
        return

    current_heading = None
    current_step_number = None
    current_lines: list[str] = []

    for raw_line in workflow_text.splitlines():
        line = raw_line.rstrip()
        heading_match = STEP_HEADING_PATTERN.match(line.strip())
        if heading_match:
            if current_heading is not None and current_step_number is not None:
                yield current_step_number, current_heading, "\n".join(current_lines)
            current_heading = line.strip()
            current_step_number = int(heading_match.group(1))
            current_lines = []
            continue
        if current_heading is not None:
            current_lines.append(line)

    if current_heading is not None and current_step_number is not None:
        yield current_step_number, current_heading, "\n".join(current_lines)


def iter_code_fence_filtered_lines(text: str, *, strip_inline_code: bool = True):
    in_code_block = False
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        yield re.sub(r"`[^`]*`", "", line) if strip_inline_code else line


def extract_tool_refs(text: str) -> list[str]:
    refs = []
    for line in iter_code_fence_filtered_lines(text):
        for match in re.finditer(r"#tool:([^\s`]+)", line):
            refs.append(match.group(1).rstrip(".,;:"))
    return refs


def extract_capability_refs(text: str) -> list[str]:
    return [
        match.group(1).rstrip(".,;:")
        for match in re.finditer(r"capability:([^\s`]+)", text)
    ]


def extract_support_doc_reads(text: str) -> list[str]:
    paths = []
    for line in iter_code_fence_filtered_lines(text):
        if "#tool:read" not in line:
            continue
        for match in re.finditer(r"#file:\s*([^\s`]+)", line):
            file_ref = match.group(1).rstrip(".,;:")
            if file_ref.startswith(SUPPORT_FILE_PREFIXES):
                paths.append(file_ref)
    return paths


def detect_front_loaded_support_reads(text: str) -> list[str]:
    warnings = []
    for step_number, heading, step_text in iter_workflow_steps(text) or []:
        if step_number == 0:
            continue

        tool_refs = extract_tool_refs(step_text)
        if not tool_refs:
            continue

        if any(tool_ref not in CONTEXT_ONLY_TOOL_NAMES for tool_ref in tool_refs):
            break

        support_doc_reads = sorted(set(extract_support_doc_reads(step_text)))
        if len(support_doc_reads) >= 3:
            warnings.append(
                f"Potential front-loading in {heading}: early context-gathering step reads {len(support_doc_reads)} support files ({', '.join(support_doc_reads)}). Replace most of these with markdown links and defer #tool:read to the step where each file is actually consumed."
            )

    return warnings


def extract_post_workflow_text(text: str) -> str | None:
    match = re.search(
        r"</workflow>(?P<remainder>.*)\Z", text, re.DOTALL | re.IGNORECASE
    )
    if not match:
        return None
    return match.group("remainder")


def count_content_lines(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip())


def validate_post_workflow_reference_sections(text: str) -> list[str]:
    post_workflow_text = extract_post_workflow_text(text)
    if post_workflow_text is None:
        return []

    content_line_count = count_content_lines(post_workflow_text)
    if content_line_count <= MAX_POST_WORKFLOW_CONTENT_LINES:
        return []

    return [
        (
            f"SKILL.md contient {content_line_count} lignes après </workflow>. "
            "Déplacez les matrices, checklists, guides de setup dans references/ ou assets/."
        )
    ]


def normalize_concept_label(label: str) -> str:
    normalized = label.strip().lower()
    normalized = normalized.replace("mcp.json", "mcp json")
    normalized = re.sub(r"[`*_#:/().,\-]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def extract_significant_concept_tokens(label: str) -> set[str]:
    normalized = normalize_concept_label(label)
    return {
        token
        for token in normalized.split()
        if len(token) >= 3 and token not in CONCEPT_TOKEN_STOPWORDS
    }


def read_frontmatter(path: Path) -> tuple[dict[str, Any] | None, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    try:
        frontmatter = yaml.safe_load(parts[1])
    except Exception:
        return None, text
    if not isinstance(frontmatter, dict):
        return None, text
    return frontmatter, text


def iter_non_frontmatter_markdown_files(skill_dir: Path):
    for candidate in sorted(skill_dir.rglob("*.md")):
        if candidate == skill_dir / "SKILL.md":
            continue
        frontmatter, _ = read_frontmatter(candidate)
        if isinstance(frontmatter, dict):
            continue
        yield candidate


def iter_relative_markdown_links(text: str):
    in_code_block = False
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        for match in re.finditer(r"\[[^\]]+\]\(((?:\./|\.\./)[^)]+)\)", line):
            yield match.group(1)


def _resolve_workflow_reference(
    skill_dir: Path, workflow_path: Path, raw_reference: str
) -> tuple[Path | None, str | None, str | None]:
    if (
        not isinstance(raw_reference, str)
        or not raw_reference
        or raw_reference != raw_reference.strip()
        or "\\" in raw_reference
    ):
        return None, None, "must be a non-empty package-relative path using `/`"

    reference = Path(raw_reference)
    if reference.is_absolute():
        return None, None, "must be a relative path"
    try:
        skill_root = skill_dir.resolve(strict=True)
        resolved = (workflow_path.parent / reference).resolve(strict=False)
        relative = resolved.relative_to(skill_root).as_posix()
    except (OSError, RuntimeError, ValueError):
        return None, None, "must resolve inside the skill package"
    return resolved, relative, None


def validate_skill_workflows(skill_dir: Path) -> LintResult:
    result = LintResult()
    workflows_dir = skill_dir / "workflows"
    if not workflows_dir.exists():
        return result
    if workflows_dir.is_symlink() or not workflows_dir.is_dir():
        result.errors.append(
            "`workflows/` must be a regular directory inside the skill package."
        )
        return result
    references_dir = skill_dir / "references"
    if references_dir.exists():
        for candidate in references_dir.rglob("workflows"):
            if candidate.is_dir():
                relative = candidate.relative_to(skill_dir).as_posix()
                result.errors.append(
                    f"Procedures must be immediate children of `workflows/`; nested workflow directory found: ./{relative}"
                )

    workflow_files: list[Path] = []
    for candidate in sorted(workflows_dir.rglob("*")):
        relative = candidate.relative_to(workflows_dir)
        if candidate.is_symlink():
            result.errors.append(
                f"Workflow support path must not be a symlink: ./workflows/{relative.as_posix()}"
            )
        elif candidate.is_dir():
            result.errors.append(
                f"Workflow files must be immediate children of `workflows/`; nested directory found: ./workflows/{relative.as_posix()}"
            )
        elif candidate.is_file():
            if relative.parent != Path(".") or candidate.suffix.lower() != ".md":
                result.errors.append(
                    f"Workflow files must be immediate Markdown files under `workflows/`: ./workflows/{relative.as_posix()}"
                )
            else:
                workflow_files.append(candidate)

    seen_ids: set[str] = set()
    workflows: list[dict[str, Any]] = []
    for workflow_path in workflow_files:
        relative_workflow = workflow_path.relative_to(skill_dir).as_posix()
        try:
            text = workflow_path.read_text(encoding="utf-8")
            metadata, body = split_frontmatter(text)
        except (OSError, UnicodeError, ValueError) as exc:
            result.errors.append(f"./{relative_workflow}: {exc}")
            continue

        unknown_keys = sorted(set(metadata) - WORKFLOW_METADATA_KEYS)
        if unknown_keys:
            result.errors.append(
                f"./{relative_workflow}: unknown workflow metadata field(s): {', '.join(unknown_keys)}"
            )

        workflow_id = metadata.get("id")
        if not isinstance(workflow_id, str) or not WORKFLOW_ID_PATTERN.fullmatch(
            workflow_id
        ):
            result.errors.append(
                f"./{relative_workflow}: `id` must be a lowercase hyphenated workflow identifier."
            )
        else:
            if workflow_id != workflow_path.stem:
                result.errors.append(
                    f"./{relative_workflow}: `id` must match the workflow filename stem `{workflow_path.stem}`."
                )
            if workflow_id in seen_ids:
                result.errors.append(
                    f"./{relative_workflow}: duplicate workflow id `{workflow_id}`."
                )
            seen_ids.add(workflow_id)

        description = metadata.get("description")
        if not isinstance(description, str) or not description.strip():
            result.errors.append(
                f"./{relative_workflow}: `description` must be a non-empty string."
            )

        for field_name, required in (("invoke_for", True), ("avoid_for", False)):
            values = metadata.get(field_name, [] if not required else None)
            if (
                not isinstance(values, list)
                or (required and not values)
                or any(
                    not isinstance(value, str) or not value.strip() for value in values
                )
            ):
                expectation = "a non-empty" if required else "an"
                result.errors.append(
                    f"./{relative_workflow}: `{field_name}` must be {expectation} array of non-empty strings."
                )

        raw_references = metadata.get("references", [])
        if not isinstance(raw_references, list) or any(
            not isinstance(reference, str) for reference in raw_references
        ):
            result.errors.append(
                f"./{relative_workflow}: `references` must be an array of relative file paths."
            )
            raw_references = []

        references: set[str] = set()
        for raw_reference in raw_references:
            resolved, relative, error = _resolve_workflow_reference(
                skill_dir, workflow_path, raw_reference
            )
            if error:
                result.errors.append(
                    f"./{relative_workflow}: reference `{raw_reference}` {error}."
                )
                continue
            if relative is None or not relative.startswith("references/"):
                result.errors.append(
                    f"./{relative_workflow}: reference `{raw_reference}` must target the package's `references/` directory."
                )
                continue
            if resolved is None or not resolved.is_file():
                result.errors.append(
                    f"./{relative_workflow}: reference `{raw_reference}` is not a file."
                )
                continue
            if relative in references:
                result.errors.append(
                    f"./{relative_workflow}: duplicate reference `{raw_reference}`."
                )
            references.add(relative)

        if not body.strip():
            result.errors.append(
                f"./{relative_workflow}: workflow body must not be empty."
            )
        structural_text = "\n".join(
            iter_code_fence_filtered_lines(text, strip_inline_code=False)
        )
        for error in validate_subskill_body_structure(body):
            result.errors.append(f"./{relative_workflow}: {error}")
        for error in validate_skill_step_structure(structural_text):
            result.errors.append(f"./{relative_workflow}: {error}")

        linked_paths: set[str] = set()
        markdown_linked_paths: set[str] = set()
        file_references: set[str] = set()
        for raw_link in iter_relative_markdown_links(body):
            resolved, relative, error = _resolve_workflow_reference(
                skill_dir, workflow_path, raw_link
            )
            if error:
                result.errors.append(
                    f"./{relative_workflow}: link `{raw_link}` {error}."
                )
                continue
            if relative is not None and relative.startswith("workflows/"):
                result.errors.append(
                    f"./{relative_workflow}: workflow-to-workflow links are not allowed."
                )
            elif relative is not None:
                linked_paths.add(relative)
                markdown_linked_paths.add(relative)

        for match in re.finditer(r"#file:\s*([^\s`]+)", body):
            raw_reference = match.group(1).rstrip(".,;:")
            resolved, relative, error = _resolve_workflow_reference(
                skill_dir, workflow_path, raw_reference
            )
            if error:
                result.errors.append(
                    f"./{relative_workflow}: file reference `{raw_reference}` {error}."
                )
            elif relative is not None and relative.startswith("workflows/"):
                result.errors.append(
                    f"./{relative_workflow}: workflow-to-workflow file references are not allowed."
                )
            elif relative is not None:
                linked_paths.add(relative)
                file_references.add(relative)

        if re.search(r"#tool:[^\s`]+[.,;:](?:\s|$)", body):
            result.warnings.append(
                f"./{relative_workflow}: a `#tool:` marker is followed by punctuation."
            )

        workflows.append(
            {
                "path": relative_workflow,
                "references": sorted(references),
                "linked_paths": sorted(linked_paths),
                "markdown_linked_paths": sorted(markdown_linked_paths),
                "file_references": sorted(file_references),
            }
        )

    result.data["workflows"] = workflows
    return result


def validate_subskill_body_structure(body: str) -> list[str]:
    """Validate a nested subskill's skill-shaped body without package identity."""
    sections = (
        "critical_rules",
        "general_rules",
        "risk_assessment",
        "rules",
        "workflow",
    )
    lines = [
        line.strip()
        for line in iter_code_fence_filtered_lines(body, strip_inline_code=False)
    ]
    positions: list[int] = []
    content_by_section: dict[str, str] = {}
    errors: list[str] = []

    for section in sections:
        opening = f"<{section}>"
        closing = f"</{section}>"
        opening_positions = [
            index for index, line in enumerate(lines) if line == opening
        ]
        closing_positions = [
            index for index, line in enumerate(lines) if line == closing
        ]
        if len(opening_positions) != 1 or len(closing_positions) != 1:
            errors.append(
                "must contain each canonical subskill body section exactly once: "
                "<critical_rules>, <general_rules>, <risk_assessment>, <rules>, and <workflow>."
            )
            return errors
        start = opening_positions[0]
        end = closing_positions[0]
        if end <= start:
            errors.append(f"<{section}> must close after its opening tag.")
            return errors
        positions.extend((start, end))
        content_by_section[section] = "\n".join(lines[start + 1 : end])

    if positions != sorted(positions):
        errors.append(
            "canonical subskill body sections must appear in this order: "
            "<critical_rules>, <general_rules>, <risk_assessment>, <rules>, <workflow>."
        )

    if "<admission>" in lines or "</admission>" in lines:
        errors.append(
            "nested subskills must leave domain admission and global routing to the parent skill."
        )

    critical = content_by_section["critical_rules"]
    if not re.search(r"(?m)^-\s+.*\bMUST(?:\s+NOT)?\b", critical):
        errors.append(
            "<critical_rules> must contain a bulleted MUST/MUST NOT invariant."
        )

    general = content_by_section["general_rules"]
    if not re.search(r"(?m)^-\s+.*\b(?:SHOULD(?:\s+NOT)?|MAY)\b", general):
        errors.append(
            "<general_rules> must contain a bulleted SHOULD/SHOULD NOT/MAY rule."
        )

    risk = content_by_section["risk_assessment"].lower()
    if "risk_level" not in risk or "downgrade" not in risk or "escalat" not in risk:
        errors.append(
            "<risk_assessment> must inherit risk_level, forbid downgrading, and allow evidence-based escalation."
        )

    if not re.search(r"(?m)^-\s+\S", content_by_section["rules"]):
        errors.append("<rules> must contain at least one bulleted subskill contract.")

    workflow = content_by_section["workflow"]
    steps = list(iter_workflow_steps(f"<workflow>\n{workflow}\n</workflow>"))
    if not steps:
        errors.append("<workflow> must contain the complete stepwise procedure.")
    else:
        numbers = [number for number, _, _ in steps]
        if numbers[0] not in {0, 1} or numbers != list(
            range(numbers[0], numbers[0] + len(numbers))
        ):
            errors.append(
                "<workflow> steps must be continuous, starting at Step 0 or Step 1."
            )
        first_step_text = steps[0][2]
        if not re.search(
            r"\brisk(?:[_ -](?:assessment|level))?\b", first_step_text, re.IGNORECASE
        ):
            errors.append(
                "the first <workflow> step must consume the inherited risk level."
            )

    return errors


def normalize_relative_path(path_str: str) -> str:
    path = Path(path_str.strip())
    normalized = Path(*[part for part in path.parts if part not in (".", "")])
    return normalized.as_posix()


def resolve_skill_relative_path(skill_dir: Path, file_ref: str) -> Path:
    candidate = Path(file_ref.strip())
    if candidate.is_absolute():
        return candidate
    return (skill_dir / candidate).resolve(strict=False)


def split_leading_code_fences(text: str, expected_count: int = 2):
    normalized = text.replace("\r\n", "\n").lstrip("\ufeff")
    lines = normalized.splitlines()
    index = 0

    while index < len(lines) and not lines[index].strip():
        index += 1

    fences = []
    while len(fences) < expected_count:
        if index >= len(lines) or not lines[index].startswith("```"):
            return fences, "\n".join(lines[index:]).strip(), False

        language = lines[index][3:].strip()
        index += 1
        content_lines = []
        while index < len(lines) and lines[index].strip() != "```":
            content_lines.append(lines[index])
            index += 1

        if index >= len(lines):
            return fences, "", None

        index += 1
        fences.append((language, "\n".join(content_lines).strip()))

        while index < len(lines) and not lines[index].strip():
            index += 1

    return fences, "\n".join(lines[index:]).strip(), True


def validate_template_yaml_block(content: str) -> str | None:
    stripped = content.strip()
    match = re.fullmatch(r"---\n(?P<body>.*)\n---", stripped, re.DOTALL)
    if not match:
        return "must keep YAML frontmatter delimiters inside the opening ```yaml block"

    try:
        parsed = yaml.safe_load(match.group("body"))
    except Exception:
        return "must keep valid YAML inside the opening ```yaml block"

    if parsed is not None and not isinstance(parsed, dict):
        return "must keep a YAML mapping inside the opening ```yaml block"

    return None


def validate_agent_template_yaml_block(content: str) -> list[str]:
    errors = []
    yaml_error = validate_template_yaml_block(content)
    if yaml_error:
        return [yaml_error]

    required_fragments = {
        'name: "[agent-slug]"': 'must keep the canonical `name: "[agent-slug]"` placeholder in the opening ```yaml block',
        "WHAT:": "must keep `WHAT:` guidance in the canonical agent YAML description example",
        "INVOKE FOR:": "must keep `INVOKE FOR:` guidance in the canonical agent YAML description example",
        "DO NOT INVOKE FOR:": "must keep `DO NOT INVOKE FOR:` guidance in the canonical agent YAML description example",
        "target: vscode": "must keep `target: vscode` in the canonical agent YAML example",
        "tools: [read, search]": "must keep the minimal `tools: [read, search]` example in the canonical agent YAML block",
        "# agents:": "must keep the optional `# agents:` guidance in the canonical agent YAML block",
        "# argument-hint:": "must keep the optional `# argument-hint:` guidance in the canonical agent YAML block",
        "# model:": "must keep the optional `# model:` guidance in the canonical agent YAML block",
        "# user-invocable:": "must keep the optional `# user-invocable:` guidance in the canonical agent YAML block",
        "# disable-model-invocation:": "must keep the optional `# disable-model-invocation:` guidance in the canonical agent YAML block",
    }
    for fragment, message in required_fragments.items():
        if fragment not in content:
            errors.append(message)

    return errors


def validate_agent_template_markdown_block(content: str) -> list[str]:
    errors = []
    stripped_lines = [line.strip() for line in content.splitlines() if line.strip()]

    if re.search(
        r"^\s{0,3}#{1,6}\s+.*\badmission matrix\b",
        content,
        re.IGNORECASE | re.MULTILINE,
    ):
        errors.append(
            "must not include a body-level admission matrix in the canonical agent markdown example"
        )
    table_lines = content.splitlines()
    for index, line in enumerate(table_lines):
        if "|" not in line:
            continue
        header_cells = [
            cell.strip().strip("`*_ ").upper()
            for cell in line.strip().strip("|").split("|")
        ]
        if not any("REQUEST SHAPE" in cell for cell in header_cells):
            continue
        if not any(re.fullmatch(r"INVOKE\??", cell) for cell in header_cells):
            continue
        has_yes = False
        has_no = False
        for row in table_lines[index + 1 :]:
            if "|" not in row:
                break
            cells = {
                cell.strip().strip("`*_ ").upper()
                for cell in row.strip().strip("|").split("|")
            }
            has_yes = has_yes or "YES" in cells
            has_no = has_no or "NO" in cells
            if has_yes and has_no:
                errors.append(
                    "must not include a body-level admission matrix in the canonical agent markdown example"
                )
                break

    if re.search(
        r"\{[^{}]*[\"']status[\"']\s*:\s*[\"']refused[\"'][^{}]*\}",
        content,
        re.DOTALL | re.IGNORECASE,
    ):
        errors.append(
            "must not include a refusal JSON admission contract in the canonical agent markdown example"
        )

    if "<role>" in stripped_lines or "</role>" in stripped_lines:
        errors.append(
            "must not introduce a `<role>` wrapper in the canonical agent markdown example"
        )
        return errors

    tag_positions = {}
    for tag in (
        "<routing>",
        "</routing>",
        "<critical_rules>",
        "</critical_rules>",
        "<general_rules>",
        "</general_rules>",
        "<risk_assessment>",
        "</risk_assessment>",
        "<rules>",
        "</rules>",
        "<agent-skills>",
        "</agent-skills>",
        "<workflow>",
        "</workflow>",
    ):
        positions = [index for index, line in enumerate(stripped_lines) if line == tag]
        if len(positions) != 1:
            errors.append(
                "must keep exactly one <routing>, <critical_rules>, <general_rules>, <risk_assessment>, <rules>, <agent-skills>, and <workflow> block in the canonical agent markdown example"
            )
            return errors
        tag_positions[tag] = positions[0]

    definitions_open = [
        index for index, line in enumerate(stripped_lines) if line == "<definitions>"
    ]
    definitions_close = [
        index for index, line in enumerate(stripped_lines) if line == "</definitions>"
    ]
    if bool(definitions_open) != bool(definitions_close):
        errors.append(
            "must either omit <definitions> or include matching <definitions> and </definitions> tags"
        )
        return errors
    if len(definitions_open) > 1 or len(definitions_close) > 1:
        errors.append("must keep at most one optional <definitions> block")
        return errors
    if definitions_open:
        definitions_start = definitions_open[0]
        definitions_end = definitions_close[0]
        definitions_text = "\n".join(
            stripped_lines[definitions_start + 1 : definitions_end]
        )
        if (
            definitions_start >= definitions_end
            or definitions_end >= tag_positions["<routing>"]
            or not re.search(
                r"^\s*-\s+\*\*[^*]+\*\*\s*:\s+\S+",
                definitions_text,
                re.MULTILINE,
            )
        ):
            errors.append(
                "when present, <definitions> must precede <rules> and contain a non-empty `- **term** : definition` bullet"
            )
            return errors

    rules_start = tag_positions["<rules>"]
    rules_end = tag_positions["</rules>"]
    routing_start = tag_positions["<routing>"]
    routing_end = tag_positions["</routing>"]
    critical_start = tag_positions["<critical_rules>"]
    critical_end = tag_positions["</critical_rules>"]
    general_start = tag_positions["<general_rules>"]
    general_end = tag_positions["</general_rules>"]
    risk_start = tag_positions["<risk_assessment>"]
    risk_end = tag_positions["</risk_assessment>"]
    skills_start = tag_positions["<agent-skills>"]
    skills_end = tag_positions["</agent-skills>"]
    workflow_start = tag_positions["<workflow>"]
    workflow_end = tag_positions["</workflow>"]
    if not (
        routing_start
        < routing_end
        < critical_start
        < critical_end
        < general_start
        < general_end
        < risk_start
        < risk_end
        < rules_start
        < rules_end
        < skills_start
        < skills_end
        < workflow_start
        < workflow_end
    ):
        errors.append(
            "must order <routing>, <critical_rules>, <general_rules>, <risk_assessment>, <rules>, <agent-skills>, and <workflow> in the canonical agent markdown example"
        )
        return errors
    critical_lines = stripped_lines[critical_start + 1 : critical_end]
    general_lines = stripped_lines[general_start + 1 : general_end]
    risk_text = "\n".join(stripped_lines[risk_start + 1 : risk_end])
    if not any(re.match(r"^-\s+\S", line) for line in critical_lines) or not re.search(
        r"\bMUST(?:\s+NOT)?\b", "\n".join(critical_lines)
    ):
        errors.append(
            "<critical_rules> must contain a bulleted non-negotiable MUST rule in the canonical agent markdown example"
        )
        return errors
    if not any(re.match(r"^-\s+\S", line) for line in general_lines) or not re.search(
        r"\b(?:SHOULD(?:\s+NOT)?|MAY)\b", "\n".join(general_lines)
    ):
        errors.append(
            "<general_rules> must contain a bulleted SHOULD/SHOULD NOT/MAY preference in the canonical agent markdown example"
        )
        return errors
    if (
        "risk_level" not in risk_text
        or "downgrade" not in risk_text.lower()
        or "escalat" not in risk_text.lower()
    ):
        errors.append(
            "<risk_assessment> must consume the assigned risk_level, forbid downgrading it, and allow evidence-based escalation in the canonical agent markdown example"
        )
        return errors
    workflow_lines = stripped_lines[workflow_start + 1 : workflow_end]
    step_positions = [
        index
        for index, line in enumerate(workflow_lines)
        if STEP_HEADING_PATTERN.match(line)
    ]
    if len(step_positions) >= 2 and not re.search(
        r"\b(?:risk(?:[_ -](?:assessment|level))?|assurance)\b",
        "\n".join(workflow_lines[step_positions[0] + 1 : step_positions[1]]),
        re.IGNORECASE,
    ):
        errors.append(
            "<workflow> Step 1 must apply the local risk assessment in the canonical agent markdown example"
        )
        return errors
    routing_lines = stripped_lines[routing_start + 1 : routing_end]
    accept_positions = [
        index for index, line in enumerate(routing_lines) if line == "## ACCEPT"
    ]
    reject_positions = [
        index for index, line in enumerate(routing_lines) if line == "## REJECT"
    ]
    if len(accept_positions) != 1 or len(reject_positions) != 1:
        errors.append(
            "canonical <routing> must contain exactly one ## ACCEPT and one ## REJECT section"
        )
        return errors
    accept_start = accept_positions[0]
    reject_start = reject_positions[0]
    if accept_start >= reject_start:
        errors.append("canonical <routing> must place ## ACCEPT before ## REJECT")
        return errors
    if not any(
        re.match(r"^-\s+\S", line)
        for line in routing_lines[accept_start + 1 : reject_start]
    ):
        errors.append("canonical <routing> ## ACCEPT must contain a non-empty list")
        return errors
    reject_items = [
        line for line in routing_lines[reject_start + 1 :] if re.match(r"^-\s+\S", line)
    ]
    if not reject_items:
        errors.append("canonical <routing> ## REJECT must contain a non-empty list")
        return errors
    if any(
        not re.search(
            r"→\s*(?:`[a-z0-9]+(?:-[a-z0-9]+)*`|`\[exact-agent-id\]`)",
            line,
        )
        for line in reject_items
    ):
        errors.append(
            "every canonical <routing> ## REJECT item must route to an exact agent identifier"
        )
        return errors
    skills_lines = stripped_lines[skills_start + 1 : skills_end]
    if not any(re.match(r"^-\s+\S", line) for line in skills_lines):
        errors.append(
            "<agent-skills> must contain at least one skill/context entry or a statement that no skill is prescribed"
        )
        return errors

    rules_lines = stripped_lines[rules_start + 1 : rules_end]
    required_sections = (
        "## Role",
        "## Responsibilities",
        "## Constraints",
        "## Output Contract",
    )
    section_positions = []
    for section in required_sections:
        positions = [index for index, line in enumerate(rules_lines) if line == section]
        if len(positions) != 1:
            errors.append(
                "must keep ## Role, ## Responsibilities, ## Constraints, and ## Output Contract inside <rules>"
            )
            return errors
        section_positions.append(positions[0])
    if section_positions != sorted(section_positions):
        errors.append(
            "must keep Role, Responsibilities, Constraints, and Output Contract in order inside <rules>"
        )
        return errors

    workflow_lines = stripped_lines[workflow_start + 1 : workflow_end]
    workflow_steps = [
        line for line in workflow_lines if STEP_HEADING_PATTERN.match(line)
    ]
    all_steps = [line for line in stripped_lines if STEP_HEADING_PATTERN.match(line)]
    step_patterns = (
        r"^##\s+Step\s+1\s+-\s+.+$",
        r"^##\s+Step\s+2\s+-\s+.+$",
        r"^##\s+Step\s+3\s+-\s+.+$",
    )
    if (
        len(all_steps) != 3
        or all_steps != workflow_steps
        or any(
            not re.fullmatch(pattern, line)
            for pattern, line in zip(step_patterns, workflow_steps)
        )
    ):
        errors.append(
            "must keep exactly ## Step 1 - ..., ## Step 2 - ..., and ## Step 3 - ... inside <workflow>"
        )
        return errors

    if (
        "# Role" in rules_lines
        or "<role>" in stripped_lines
        or "</role>" in stripped_lines
    ):
        errors.append(
            "must use ## Role inside <rules> instead of a # Role heading or <role> wrapper"
        )

    if (
        "#file:./references/USEFOR.md" in content
        or "#file:./references/DONOTUSEFOR.md" in content
    ):
        errors.append(
            "must keep routing inside the `.agent.md` file instead of reading sibling routing files in the canonical agent markdown example"
        )

    return errors


def validate_skill_template_markdown_block(content: str) -> list[str]:
    errors = []
    stripped_lines = [line.strip() for line in content.splitlines() if line.strip()]

    required_tokens = [
        "<definitions>",
        "</definitions>",
        "<critical_rules>",
        "</critical_rules>",
        "<general_rules>",
        "</general_rules>",
        "<risk_assessment>",
        "</risk_assessment>",
        "<rules>",
        "</rules>",
        "<workflow>",
        "</workflow>",
    ]
    token_positions = {}
    for token in required_tokens:
        try:
            token_positions[token] = stripped_lines.index(token)
        except ValueError:
            errors.append(
                "must keep <definitions>, <critical_rules>, <general_rules>, <risk_assessment>, <rules>, and <workflow> tags in the canonical markdown example"
            )
            return errors

    step_lines = [line for line in stripped_lines if STEP_HEADING_PATTERN.match(line)]
    step_patterns = [
        r"^##\s+Step\s+1\s+-\s+.+$",
        r"^##\s+Step\s+2\s+-\s+.+$",
        r"^##\s+Step\s+3\s+-\s+.+$",
    ]
    if len(step_lines) != len(step_patterns) or any(
        not re.fullmatch(pattern, line)
        for pattern, line in zip(step_patterns, step_lines)
    ):
        errors.append(
            "must keep markdown headings in this order: ## Step 1 - ..., ## Step 2 - ..., ## Step 3 - ..."
        )
        return errors

    step_positions = {line: stripped_lines.index(line) for line in step_lines}
    if not (
        token_positions["<definitions>"]
        < token_positions["</definitions>"]
        < token_positions["<critical_rules>"]
        < token_positions["</critical_rules>"]
        < token_positions["<general_rules>"]
        < token_positions["</general_rules>"]
        < token_positions["<risk_assessment>"]
        < token_positions["</risk_assessment>"]
        < token_positions["<rules>"]
        < token_positions["</rules>"]
        < token_positions["<workflow>"]
        < step_positions[step_lines[0]]
        < step_positions[step_lines[1]]
        < step_positions[step_lines[2]]
        < token_positions["</workflow>"]
    ):
        errors.append(
            "must keep <definitions>, <critical_rules>, <general_rules>, <risk_assessment>, <rules>, <workflow>, Step 1, Step 2, Step 3, and </workflow> in canonical order"
        )
        return errors

    critical_start = token_positions["<critical_rules>"]
    critical_end = token_positions["</critical_rules>"]
    general_start = token_positions["<general_rules>"]
    general_end = token_positions["</general_rules>"]
    risk_start = token_positions["<risk_assessment>"]
    risk_end = token_positions["</risk_assessment>"]
    critical_lines = stripped_lines[critical_start + 1 : critical_end]
    general_lines = stripped_lines[general_start + 1 : general_end]
    risk_text = "\n".join(stripped_lines[risk_start + 1 : risk_end])
    if not any(re.match(r"^-\s+\S", line) for line in critical_lines) or not re.search(
        r"\bMUST(?:\s+NOT)?\b", "\n".join(critical_lines)
    ):
        errors.append(
            "<critical_rules> must contain a bulleted non-negotiable MUST rule in the canonical skill markdown example"
        )
        return errors
    if not any(re.match(r"^-\s+\S", line) for line in general_lines) or not re.search(
        r"\b(?:SHOULD(?:\s+NOT)?|MAY)\b", "\n".join(general_lines)
    ):
        errors.append(
            "<general_rules> must contain a bulleted SHOULD/SHOULD NOT/MAY preference in the canonical skill markdown example"
        )
        return errors
    if (
        "risk_level" not in risk_text
        or "downgrade" not in risk_text.lower()
        or "escalat" not in risk_text.lower()
    ):
        errors.append(
            "<risk_assessment> must consume the assigned risk_level, forbid downgrading it, and allow evidence-based escalation in the canonical skill markdown example"
        )
        return errors
    workflow_start = token_positions["<workflow>"]
    workflow_end = token_positions["</workflow>"]
    workflow_lines = stripped_lines[workflow_start + 1 : workflow_end]
    first_step_position = workflow_lines.index(step_lines[0])
    second_step_position = workflow_lines.index(step_lines[1])
    if not re.search(
        r"\b(?:risk(?:[_ -](?:assessment|level))?|assurance)\b",
        "\n".join(workflow_lines[first_step_position + 1 : second_step_position]),
        re.IGNORECASE,
    ):
        errors.append(
            "<workflow> Step 1 must apply the local risk assessment in the canonical skill markdown example"
        )

    return errors


def validate_template_asset(relative_path: str, text: str) -> list[str]:
    errors = []
    asset_name = Path(relative_path).name

    fences, remainder, status = split_leading_code_fences(text)
    if status is False:
        return [
            f"Template asset ./{relative_path} must start with consecutive ```yaml and ```markdown code fences"
        ]
    if status is None:
        return [f"Template asset ./{relative_path} has an unclosed leading code fence"]

    languages = [language for language, _ in fences]
    if languages != ["yaml", "markdown"]:
        errors.append(
            f"Template asset ./{relative_path} must start with consecutive ```yaml and ```markdown code fences"
        )
        return errors

    if asset_name == "agent-template.md":
        for yaml_error in validate_agent_template_yaml_block(fences[0][1]):
            errors.append(f"Template asset ./{relative_path} {yaml_error}")
        for markdown_error in validate_agent_template_markdown_block(fences[1][1]):
            errors.append(f"Template asset ./{relative_path} {markdown_error}")

        post_headings = list(iter_markdown_headings(remainder))
        if post_headings != EXPECTED_AGENT_TEMPLATE_POST_HEADINGS:
            errors.append(
                f"Template asset ./{relative_path} must keep post-template headings in this order: "
                + ", ".join(EXPECTED_AGENT_TEMPLATE_POST_HEADINGS)
            )

    if asset_name == "skill-template.md":
        yaml_error = validate_template_yaml_block(fences[0][1])
        if yaml_error:
            errors.append(f"Template asset ./{relative_path} {yaml_error}")
        for markdown_error in validate_skill_template_markdown_block(fences[1][1]):
            errors.append(f"Template asset ./{relative_path} {markdown_error}")

        post_headings = list(iter_markdown_headings(remainder))
        if post_headings != EXPECTED_SKILL_TEMPLATE_POST_HEADINGS:
            errors.append(
                f"Template asset ./{relative_path} must keep post-template headings in this order: "
                + ", ".join(EXPECTED_SKILL_TEMPLATE_POST_HEADINGS)
            )

    return errors


def iter_support_doc_concepts(skill_dir: Path):
    for support_doc in iter_non_frontmatter_markdown_files(skill_dir):
        if support_doc.name in {"USEFOR.md", "DONOTUSEFOR.md"}:
            continue

        _, support_text = read_frontmatter(support_doc)
        relative_path = support_doc.relative_to(skill_dir).as_posix()
        concepts = [support_doc.stem.replace("-", " ")]
        concepts.extend(iter_markdown_headings(support_text))

        seen = set()
        for concept in concepts:
            normalized = normalize_concept_label(concept)
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            yield relative_path, concept


def detect_duplicate_skill_support_concepts(
    skill_dir: Path, full_text: str
) -> list[str]:
    post_workflow_text = extract_post_workflow_text(full_text)
    if not post_workflow_text:
        return []

    support_concepts = []
    for relative_path, concept in iter_support_doc_concepts(skill_dir):
        support_concepts.append(
            (
                relative_path,
                concept,
                normalize_concept_label(concept),
                extract_significant_concept_tokens(concept),
            )
        )

    warnings: list[str] = []
    seen_messages: set[str] = set()
    for heading in iter_markdown_headings(post_workflow_text):
        normalized_heading = normalize_concept_label(heading)
        if not normalized_heading or normalized_heading in GENERIC_DUPLICATE_CONCEPTS:
            continue

        heading_tokens = extract_significant_concept_tokens(heading)
        if not heading_tokens:
            continue

        for (
            relative_path,
            support_concept,
            normalized_support,
            support_tokens,
        ) in support_concepts:
            if not support_tokens:
                continue

            overlap = heading_tokens & support_tokens
            if not (
                normalized_heading in normalized_support
                or normalized_support in normalized_heading
                or len(overlap) >= 2
            ):
                continue

            message = (
                f"Concept `{heading}` apparaît dans SKILL.md ET dans ./{relative_path} "
                f"(`{support_concept}`). Gardez une seule source."
            )
            if message in seen_messages:
                continue
            seen_messages.add(message)
            warnings.append(message)
            break

    return warnings


def validate_skill_step_structure(text: str) -> list[str]:
    errors: list[str] = []
    structural_lines = {"<rules>", "</rules>"}

    for _, heading, step_text in iter_workflow_steps(text) or []:
        non_empty_lines = [
            line.rstrip()
            for line in iter_code_fence_filtered_lines(
                step_text, strip_inline_code=False
            )
            if line.strip()
        ]
        content_lines = []
        inside_rules = False
        for line in non_empty_lines:
            stripped_line = line.strip()
            if stripped_line == "<rules>":
                inside_rules = True
                continue
            if stripped_line == "</rules>":
                inside_rules = False
                continue
            if inside_rules or stripped_line in structural_lines:
                continue
            content_lines.append(line)

        if not content_lines:
            errors.append(f"{heading} must contain at least one ordered `1.` action.")
            continue

        if not re.match(r"^\d+\.\s+\S", content_lines[0].lstrip()):
            errors.append(
                f"{heading} must start with an ordered `1.` action instead of bare prose."
            )
            continue

        next_number_by_indent: dict[int, int] = {}
        for line in content_lines:
            stripped = line.lstrip()
            ordered_match = re.match(r"^(\s*)(\d+)\.\s+\S", line)
            if ordered_match:
                indent = len(ordered_match.group(1))
                number = int(ordered_match.group(2))
                expected = next_number_by_indent.get(indent, 1)
                if number != expected:
                    errors.append(
                        f"{heading} has non-consecutive ordered actions at indentation {indent}: expected `{expected}.`, found `{number}.`."
                    )
                    break
                next_number_by_indent[indent] = number + 1
                continue
            if re.match(r"^-\s+\S", stripped):
                continue
            if re.match(r"^\s+\S", line):
                continue
            errors.append(
                f"{heading} must keep step instructions inside ordered `1.` items; move plain text `{line.strip()}` into a numbered action."
            )
            break

    return errors


def validate_skill_contract_sections(text: str) -> list[str]:
    errors: list[str] = []
    lines = [
        line.strip()
        for line in iter_code_fence_filtered_lines(text, strip_inline_code=False)
        if line.strip()
    ]
    required_tags = (*REQUIRED_POLICY_BLOCKS, "rules", "workflow")
    positions: dict[str, tuple[int, int]] = {}
    for tag_name in required_tags:
        open_tag = f"<{tag_name}>"
        close_tag = f"</{tag_name}>"
        open_positions = [index for index, line in enumerate(lines) if line == open_tag]
        close_positions = [
            index for index, line in enumerate(lines) if line == close_tag
        ]
        if len(open_positions) != 1 or len(close_positions) != 1:
            errors.append(
                f"Canonical skills must contain exactly one `{open_tag}` and `{close_tag}` block."
            )
            return errors
        positions[tag_name] = (open_positions[0], close_positions[0])

    ordered_tags = [positions[tag_name] for tag_name in required_tags]
    if any(
        open_position >= close_position
        for open_position, close_position in ordered_tags
    ) or any(
        ordered_tags[index][1] >= ordered_tags[index + 1][0]
        for index in range(len(ordered_tags) - 1)
    ):
        errors.append(
            "Canonical skills must order `<critical_rules>`, `<general_rules>`, `<risk_assessment>`, `<rules>`, and `<workflow>`."
        )
        return errors

    critical_start, critical_end = positions["critical_rules"]
    critical_lines = lines[critical_start + 1 : critical_end]
    if not any(re.match(r"^-\s+\S", line) for line in critical_lines) or not re.search(
        r"\bMUST(?:\s+NOT)?\b", "\n".join(critical_lines)
    ):
        errors.append(
            "`<critical_rules>` must contain a bulleted non-negotiable MUST rule."
        )
        return errors

    general_start, general_end = positions["general_rules"]
    general_lines = lines[general_start + 1 : general_end]
    if not any(re.match(r"^-\s+\S", line) for line in general_lines) or not re.search(
        r"\b(?:SHOULD(?:\s+NOT)?|MAY)\b", "\n".join(general_lines)
    ):
        errors.append(
            "`<general_rules>` must contain a bulleted SHOULD/SHOULD NOT/MAY preference."
        )
        return errors

    risk_start, risk_end = positions["risk_assessment"]
    risk_text = "\n".join(lines[risk_start + 1 : risk_end])
    if (
        "risk_level" not in risk_text
        or "downgrade" not in risk_text.lower()
        or "escalat" not in risk_text.lower()
    ):
        errors.append(
            "`<risk_assessment>` must consume the assigned `risk_level`, forbid downgrading it, and allow evidence-based escalation."
        )
        return errors

    workflow_start, workflow_end = positions["workflow"]
    workflow_lines = lines[workflow_start + 1 : workflow_end]
    step_positions = [
        index
        for index, line in enumerate(workflow_lines)
        if STEP_HEADING_PATTERN.match(line)
    ]
    if len(step_positions) >= 2 and not re.search(
        r"\b(?:risk(?:[_ -](?:assessment|level))?|assurance)\b",
        "\n".join(workflow_lines[step_positions[0] + 1 : step_positions[1]]),
        re.IGNORECASE,
    ):
        errors.append(
            "`<workflow>` Step 1 must consume or assign risk before substantive work."
        )

    return errors


def collect_transitive_workflow_support(
    skill_dir: Path, workflows: list[dict[str, Any]]
) -> tuple[set[str], set[str], set[str], set[str], list[str]]:
    referenced_paths: set[str] = set()
    markdown_paths: set[str] = set()
    file_reference_paths: set[str] = set()
    metadata_reference_paths: set[str] = set()
    errors: list[str] = []
    pending = [
        support_path
        for workflow in workflows
        for field_name in (
            "references",
            "linked_paths",
            "file_references",
        )
        for support_path in workflow.get(field_name, [])
    ]
    visited: set[str] = set()

    while pending:
        relative_source = pending.pop()
        if relative_source in visited:
            continue
        visited.add(relative_source)
        source_path = skill_dir / relative_source
        if source_path.is_symlink():
            errors.append(
                f"Workflow support path must not be a symlink: ./{relative_source}"
            )
            continue
        try:
            resolved_source = source_path.resolve(strict=True)
            relative_source = resolved_source.relative_to(
                skill_dir.resolve(strict=True)
            ).as_posix()
            source_text = resolved_source.read_text(encoding="utf-8")
        except (OSError, UnicodeError, RuntimeError, ValueError) as exc:
            errors.append(
                f"Could not read workflow support file ./{relative_source}: {exc}"
            )
            continue

        frontmatter, body = read_frontmatter(resolved_source)
        if isinstance(frontmatter, dict):
            try:
                _, body = split_frontmatter(source_text)
            except ValueError:
                body = source_text

        if resolved_source.suffix.lower() != ".md":
            continue

        if isinstance(frontmatter, dict):
            metadata_paths = frontmatter.get("references", [])
            if not isinstance(metadata_paths, list) or any(
                not isinstance(path, str) for path in metadata_paths
            ):
                errors.append(
                    f"./{relative_source}: `references` must be an array of relative file paths."
                )
            else:
                for raw_path in metadata_paths:
                    resolved, relative, error = _resolve_workflow_reference(
                        skill_dir, resolved_source, raw_path
                    )
                    if error:
                        errors.append(
                            f"./{relative_source}: reference `{raw_path}` {error}."
                        )
                        continue
                    if relative is None:
                        continue
                    if resolved is None or not resolved.is_file():
                        errors.append(
                            f"./{relative_source}: reference `{raw_path}` is not a file."
                        )
                        continue
                    referenced_paths.add(relative)
                    metadata_reference_paths.add(relative)
                    if relative.lower().endswith(".md"):
                        markdown_paths.add(relative)
                        pending.append(relative)

        active_body = "\n".join(iter_code_fence_filtered_lines(body))
        for raw_link in iter_relative_markdown_links(active_body):
            resolved, relative, error = _resolve_workflow_reference(
                skill_dir, resolved_source, raw_link
            )
            if error:
                errors.append(
                    f"./{relative_source}: transitive link `{raw_link}` {error}."
                )
                continue
            if relative is None:
                continue
            referenced_paths.add(relative)
            markdown_paths.add(relative)
            if relative.lower().endswith(".md"):
                pending.append(relative)

        for match in re.finditer(r"#file:\s*([^\s`]+)", active_body):
            raw_reference = match.group(1).rstrip(".,;:")
            resolved, relative, error = _resolve_workflow_reference(
                skill_dir, resolved_source, raw_reference
            )
            if error:
                errors.append(
                    f"./{relative_source}: transitive file reference `{raw_reference}` {error}."
                )
                continue
            if relative is None:
                continue
            referenced_paths.add(relative)
            file_reference_paths.add(relative)
            if relative.lower().endswith(".md"):
                markdown_paths.add(relative)
                pending.append(relative)

    return (
        referenced_paths,
        markdown_paths,
        file_reference_paths,
        metadata_reference_paths,
        errors,
    )


def lint_skill_markdown(skill_dir: Path, full_text: str) -> LintResult:
    result = LintResult()
    workflow_result = validate_skill_workflows(skill_dir)
    result.extend(workflow_result)
    workflows = workflow_result.data.get("workflows", [])

    lines = full_text.splitlines()
    if len(lines) > 500:
        result.warnings.append(f"SKILL.md is {len(lines)} lines (recommended <500)")

    if skill_dir.name in CANONICAL_CREATE_SURFACE_SKILL_NAMES:
        script_files = [
            candidate
            for candidate in (skill_dir / "references").rglob("*")
            if candidate.is_file()
            and candidate.parent.name == "scripts"
            and candidate.suffix.lower() in {".py", ".sh", ".js", ".ts"}
            and "__pycache__" not in candidate.parts
        ]
        if not script_files:
            result.errors.append(
                "The `plugin-engineering` domain must preserve executable authoring or validation scripts under its internal create-surface methods."
            )

    filtered_lines = list(iter_code_fence_filtered_lines(full_text))
    filtered_text = "\n".join(filtered_lines)
    result.data["filtered_text"] = filtered_text

    for tag_name in REQUIRED_SKILL_BLOCKS:
        if not has_block_tag(filtered_text, tag_name):
            result.warnings.append(
                f"Missing <{tag_name}> block; use the canonical structure from assets/skill-template.md"
            )
    result.errors.extend(validate_skill_contract_sections(full_text))

    for marker, message in TEMPLATE_LEFTOVER_MARKERS.items():
        if marker in filtered_text:
            result.errors.append(message)

    file_refs = []
    file_ref_has_trailing_punctuation = False
    for match in re.finditer(r"#file:\s*([^\s`]+)", filtered_text):
        raw_ref = match.group(1)
        clean_ref = raw_ref.rstrip(".,;:")
        if clean_ref != raw_ref:
            file_ref_has_trailing_punctuation = True
        file_refs.append(clean_ref)
    result.data["file_refs"] = file_refs

    markdown_links = list(iter_relative_markdown_links(full_text))
    markdown_referenced_paths = {
        normalize_relative_path(path)
        for path in markdown_links
        if path.startswith("./") or path.startswith("../")
    }
    known_workflow_paths = {workflow["path"] for workflow in workflows}
    for route_path in markdown_referenced_paths:
        route_parts = Path(route_path).parts
        if "workflows" not in route_parts:
            continue
        if route_parts[0] != "workflows" or route_path not in known_workflow_paths:
            result.errors.append(
                f"Workflow routing link must target an existing immediate child of `workflows/`: {route_path}"
            )
    referenced_paths = {
        normalize_relative_path(path)
        for path in [*file_refs, *markdown_links]
        if path.startswith("./") or path.startswith("../")
    }
    all_referenced_paths = set(referenced_paths)
    all_markdown_referenced_paths = set(markdown_referenced_paths)
    workflow_metadata_references: set[str] = set()
    workflow_support: list[dict[str, Any]] = []
    file_marker_references = set(file_refs)
    for workflow in workflows:
        all_referenced_paths.update(workflow["references"])
        all_referenced_paths.update(workflow["linked_paths"])
        all_markdown_referenced_paths.update(workflow["markdown_linked_paths"])
        workflow_metadata_references.update(workflow["references"])
        file_marker_references.update(workflow["file_references"])
        workflow_support.append(workflow)

    (
        transitive_paths,
        transitive_markdown_paths,
        transitive_file_refs,
        transitive_metadata_refs,
        closure_errors,
    ) = collect_transitive_workflow_support(skill_dir, workflow_support)
    result.errors.extend(closure_errors)
    all_referenced_paths.update(transitive_paths)
    all_markdown_referenced_paths.update(transitive_markdown_paths)
    file_marker_references.update(transitive_file_refs)
    workflow_metadata_references.update(transitive_metadata_refs)

    for file_ref in file_refs:
        parts = Path(file_ref).parts
        if len(parts) > 2 and not file_ref.startswith(("./", "../")):
            result.warnings.append(f"#file reference appears deep: {file_ref}")

        candidate = resolve_skill_relative_path(skill_dir, file_ref)
        if not candidate.exists():
            result.warnings.append(
                f"#file reference not found (best-effort): {file_ref}"
            )

    support_dirs = [
        skill_dir / "assets",
        skill_dir / "references",
        skill_dir / "scripts",
        skill_dir / "workflows",
    ]
    for support_dir in support_dirs:
        if not support_dir.exists():
            continue
        for candidate in sorted(
            path
            for path in support_dir.rglob("*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix != ".pyc"
        ):
            relative_candidate = candidate.relative_to(skill_dir).as_posix()
            if relative_candidate not in all_referenced_paths:
                result.warnings.append(
                    f"Support file is not referenced from SKILL.md or a selected workflow: ./{relative_candidate}"
                )
            elif relative_candidate.startswith("workflows/"):
                if relative_candidate not in markdown_referenced_paths:
                    result.errors.append(
                        f"Workflow must be linked from SKILL.md routing: ./{relative_candidate}"
                    )
            elif (
                relative_candidate not in all_markdown_referenced_paths
                and relative_candidate not in workflow_metadata_references
                and relative_candidate not in file_marker_references
            ):
                result.errors.append(
                    f"Support file must be referenced by a Markdown link, active `#file:` marker, or workflow metadata: ./{relative_candidate}"
                )

    for support_doc in iter_non_frontmatter_markdown_files(skill_dir):
        _, support_text = read_frontmatter(support_doc)
        filtered_support_text = "\n".join(iter_code_fence_filtered_lines(support_text))
        relative_support_doc = support_doc.relative_to(skill_dir).as_posix()

        if re.search(r"#file:\s*([^\s`]+)", filtered_support_text):
            result.errors.append(
                f"Active #file marker found in non-frontmatter markdown file: ./{relative_support_doc}. Use markdown links such as [file](./path) or [file](../path) in support docs."
            )

        if re.search(r"#tool:([^\s`]+)", filtered_support_text):
            result.errors.append(
                f"Active #tool marker found in non-frontmatter markdown file: ./{relative_support_doc}. Reserve #tool for frontmatter-bearing skill, agent, or prompt definitions and use inline tool names in support docs."
            )

        if extract_capability_refs(support_text):
            result.errors.append(
                f"Active capability marker found in non-frontmatter markdown file: ./{relative_support_doc}. Reserve capability markers for frontmatter-bearing skill definitions and keep support docs passive."
            )

        if Path(relative_support_doc).parts[:1] == ("assets",) and Path(
            relative_support_doc
        ).name in {
            "agent-template.md",
            "skill-template.md",
        }:
            result.errors.extend(
                validate_template_asset(relative_support_doc, support_text)
            )

    tool_refs = []
    tool_ref_has_trailing_punctuation = False
    for match in re.finditer(r"#tool:([^\s`]+)", filtered_text):
        raw_ref = match.group(1)
        clean_ref = raw_ref.rstrip(".,;:")
        if clean_ref != raw_ref:
            tool_ref_has_trailing_punctuation = True
        tool_refs.append(clean_ref)
    result.data["tool_refs"] = tool_refs

    capability_refs = extract_capability_refs(full_text)
    result.data["capability_refs"] = capability_refs
    if capability_refs:
        result.warnings.append(
            "Capability references are recorded but not resolved by package-local lint; resolve them in the consuming workspace."
        )

    if not tool_refs and not capability_refs:
        result.warnings.append(
            "No execution references found; ensure you reference required `#tool:` or `capability:` markers"
        )

    raw_tool_markers = len(re.findall(r"#tool:", filtered_text))
    if raw_tool_markers > len(tool_refs):
        result.warnings.append("One or more `#tool:` markers appear malformed or empty")

    if tool_ref_has_trailing_punctuation:
        result.warnings.append(
            "One or more `#tool:` references are followed by punctuation; keep tool references free of trailing commas or periods"
        )

    if file_ref_has_trailing_punctuation:
        result.warnings.append(
            "One or more `#file:` references are followed by punctuation; keep file references free of trailing commas or periods"
        )

    normalized_heading_counts = {}
    for heading in iter_markdown_headings(full_text):
        normalized = normalize_heading(heading)
        if not normalized:
            continue
        normalized_heading_counts[normalized] = (
            normalized_heading_counts.get(normalized, 0) + 1
        )

    duplicate_headings = sorted(
        heading for heading, count in normalized_heading_counts.items() if count > 1
    )
    for heading in duplicate_headings:
        result.warnings.append(
            f"Potential duplicate section heading after normalization: '{heading}' appears multiple times; keep one canonical section and reference it elsewhere"
        )

    if contains_runtime_inputs_heading(full_text):
        result.warnings.append(
            "`## Runtime Inputs` encourages eager loading; cite support files on the workflow step that actually consumes them"
        )

    result.errors.extend(validate_skill_step_structure(full_text))
    result.errors.extend(validate_post_workflow_reference_sections(full_text))
    result.warnings.extend(detect_front_loaded_support_reads(full_text))
    result.warnings.extend(
        detect_duplicate_skill_support_concepts(skill_dir, full_text)
    )
    return result
