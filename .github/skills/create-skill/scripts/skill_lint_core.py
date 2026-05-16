from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import typer
import yaml


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.capability_registry import (  # noqa: E402
    extract_capability_refs,
    find_workspace_root,
    validate_skill_capability_refs,
)


FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.DOTALL)
STEP_HEADING_PATTERN = re.compile(r"^##\s+Step\s+(\d+)\b", re.IGNORECASE)
AGENT_REFUSAL_JSON_TOKENS = (
    '"status": "refused"',
    '"agent":',
    '"reason":',
    '"suggested_alternative":',
)
REQUIRED_SKILL_BLOCKS = ("rules", "workflow")
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
    "../references/",
    "../assets/",
    "../scripts/",
)
TEMPLATE_LEFTOVER_MARKERS = {
    "<what this skill does>": "Unresolved template placeholder `<what this skill does>` found; replace it with the actual skill purpose.",
    "<trigger phrases or scenarios that should cause the agent to load this skill>": "Unresolved template placeholder for discovery text found; replace it with real trigger phrases.",
    "<inspect or prepare>": "Unresolved workflow step placeholder `<inspect or prepare>` found; replace template step titles with concrete steps.",
    "<describe what this step must inspect or prepare before later work can be correct>": "Unresolved workflow placeholder found; replace it with the actual inspection or preparation requirement.",
    "<ask or decide>": "Unresolved workflow step placeholder `<ask or decide>` found; replace template step titles with concrete steps.",
    "<describe the missing decision, ambiguity, or structured input this step resolves>": "Unresolved workflow placeholder found; replace it with the actual decision or missing input this step resolves.",
    "<validate or execute>": "Unresolved workflow step placeholder `<validate or execute>` found; replace template step titles with concrete steps.",
    "<describe the concrete outcome this validation or execution step must produce before the workflow can finish>": "Unresolved workflow placeholder found; replace it with the actual validation or execution outcome.",
    "./references/<guide>.md": "Template file reference `./references/<guide>.md` found; replace it with a real support-file path or remove it.",
    "./assets/<questions>.json": "Template file reference `./assets/<questions>.json` found; replace it with a real support-file path or remove it.",
    "./scripts/<validator>.py": "Template file reference `./scripts/<validator>.py` found; replace it with a real validator path or remove it.",
}
EXPECTED_AGENT_TEMPLATE_POST_HEADINGS = [
    "Authoring Notes",
    "Discovery and routing example",
    "Step 0 refusal example",
    "Workflow specificity example",
    "Delegation boundary example",
    "Output contract example",
]
EXPECTED_SKILL_TEMPLATE_POST_HEADINGS = [
    "Authoring Notes",
    "Discovery and routing example",
    "Duplicate logic example",
    "Point-of-need reference example",
    "Choosing `#file:` versus markdown links",
    "Early-context front-loading example",
    "Support-doc marker example",
]
CANONICAL_CREATE_SURFACE_SKILL_NAMES = {
    "create-skill",
    "create-agent",
    "create-prompt",
    "create-mcp",
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


def iter_code_fence_filtered_lines(text: str):
    in_code_block = False
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        yield re.sub(r"`[^`]*`", "", line)


def extract_tool_refs(text: str) -> list[str]:
    refs = []
    for line in iter_code_fence_filtered_lines(text):
        for match in re.finditer(r"#tool:([^\s`]+)", line):
            refs.append(match.group(1).rstrip(".,;:"))
    return refs


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
    match = re.search(r"</workflow>(?P<remainder>.*)\Z", text, re.DOTALL | re.IGNORECASE)
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
        "name: agent-slug": "must keep the canonical `name: agent-slug` example in the opening ```yaml block",
        "WHAT:": "must keep `WHAT:` guidance in the canonical agent YAML description example",
        "USE FOR:": "must keep `USE FOR:` guidance in the canonical agent YAML description example",
        "DO NOT USE FOR:": "must keep `DO NOT USE FOR:` guidance in the canonical agent YAML description example",
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

    if "<role>" in stripped_lines or "</role>" in stripped_lines:
        errors.append("must not introduce a `<role>` wrapper in the canonical agent markdown example")
        return errors

    required_tokens = [
        "<definitions>",
        "</definitions>",
        "<workflow>",
        "## Step 0 - **CONFIRMATION**",
        "## Role",
        "<rules>",
        "## Responsibilities",
        "## Constraints",
        "## Output Contract",
        "</rules>",
        "</workflow>",
    ]
    token_positions = {}
    for token in required_tokens:
        try:
            token_positions[token] = stripped_lines.index(token)
        except ValueError:
            if token in {"<definitions>", "<workflow>", "</workflow>", "<rules>", "</rules>"}:
                errors.append(
                    "must keep <definitions>, a <workflow> wrapper, and a <rules> wrapper in the canonical agent markdown example"
                )
            else:
                errors.append(
                    "must keep Step 0, Role, Responsibilities, Constraints, Output Contract, and Step 1/2/3 headings in the canonical agent markdown example"
                )
            return errors

    definitions_match = re.search(r"<definitions>(.*?)</definitions>", content, re.DOTALL | re.IGNORECASE)
    if not definitions_match or not re.search(
        r"^\s*-\s+\*\*[^*]+\*\*\s*:\s+\S+",
        definitions_match.group(1),
        re.MULTILINE,
    ):
        errors.append(
            "must keep at least one definition bullet in <definitions> using `- **term** : definition`"
        )

    step_lines = [line for line in stripped_lines if STEP_HEADING_PATTERN.match(line)]
    step_patterns = [
        r"^##\s+Step\s+0\s+-\s+\*\*CONFIRMATION\*\*$",
        r"^##\s+Step\s+1\s+-\s+.+$",
        r"^##\s+Step\s+2\s+-\s+.+$",
        r"^##\s+Step\s+3\s+-\s+.+$",
    ]
    if len(step_lines) != len(step_patterns) or any(
        not re.fullmatch(pattern, line)
        for pattern, line in zip(step_patterns, step_lines)
    ):
        errors.append(
            "must keep canonical agent markdown sections in this order: ## Step 0 - **CONFIRMATION**, ## Role, ## Responsibilities, ## Constraints, ## Output Contract, ## Step 1 - ..., ## Step 2 - ..., ## Step 3 - ..."
        )
        return errors

    normalized_lines = {_normalize_agent_heading(line) for line in stripped_lines}
    if "### USE FOR" not in normalized_lines or "### DO NOT USE FOR" not in normalized_lines:
        errors.append(
            "must keep embedded `### USE FOR` and `### DO **NOT** USE FOR` routing sections in the canonical agent markdown example"
        )

    if "#file:./references/USEFOR.md" in content or "#file:./references/DONOTUSEFOR.md" in content:
        errors.append(
            "must keep routing inside the `.agent.md` file instead of reading sibling routing files in the canonical agent markdown example"
        )

    if any(token not in content for token in AGENT_REFUSAL_JSON_TOKENS):
        errors.append(
            "must keep the Step 0 JSON refusal example with `\"status\": \"refused\"`, `\"agent\"`, `\"reason\"`, and `\"suggested_alternative\"` fields in the canonical agent markdown example"
        )

    step_positions = {line: stripped_lines.index(line) for line in step_lines}
    if not (
        token_positions["<definitions>"]
        < token_positions["</definitions>"]
        < token_positions["<workflow>"]
        < step_positions[step_lines[0]]
        < token_positions["## Role"]
        < token_positions["<rules>"]
        < token_positions["## Responsibilities"]
        < token_positions["## Constraints"]
        < token_positions["## Output Contract"]
        < token_positions["</rules>"]
        < step_positions[step_lines[1]]
        < step_positions[step_lines[2]]
        < step_positions[step_lines[3]]
        < token_positions["</workflow>"]
    ):
        errors.append(
            "must keep <definitions>, <workflow>, Step 0, ## Role, <rules>, ## Responsibilities, ## Constraints, ## Output Contract, </rules>, Step 1, Step 2, Step 3, and </workflow> in canonical order"
        )

    return errors


def validate_skill_template_markdown_block(content: str) -> list[str]:
    errors = []
    stripped_lines = [line.strip() for line in content.splitlines() if line.strip()]

    required_tokens = [
        "<definitions>",
        "</definitions>",
        "<workflow>",
        "<rules>",
        "</rules>",
        "</workflow>",
    ]
    token_positions = {}
    for token in required_tokens:
        try:
            token_positions[token] = stripped_lines.index(token)
        except ValueError:
            errors.append(
                "must keep <definitions>, <workflow>, and <rules> tags in the canonical markdown example"
            )
            return errors

    step_lines = [line for line in stripped_lines if STEP_HEADING_PATTERN.match(line)]
    step_patterns = [
        r"^##\s+Step\s+0\s+-\s+\*\*CONFIRMATION\*\*$",
        r"^##\s+Step\s+1\s+-\s+.+$",
        r"^##\s+Step\s+2\s+-\s+.+$",
        r"^##\s+Step\s+3\s+-\s+.+$",
    ]
    if len(step_lines) != len(step_patterns) or any(
        not re.fullmatch(pattern, line)
        for pattern, line in zip(step_patterns, step_lines)
    ):
        errors.append(
            "must keep markdown headings in this order: ## Step 0 - **CONFIRMATION**, ## Step 1 - ..., ## Step 2 - ..., ## Step 3 - ..."
        )
        return errors

    step_positions = {line: stripped_lines.index(line) for line in step_lines}
    if not (
        token_positions["<definitions>"]
        < token_positions["</definitions>"]
        < token_positions["<workflow>"]
        < step_positions[step_lines[0]]
        < token_positions["<rules>"]
        < token_positions["</rules>"]
        < step_positions[step_lines[1]]
        < step_positions[step_lines[2]]
        < step_positions[step_lines[3]]
        < token_positions["</workflow>"]
    ):
        errors.append(
            "must keep <definitions>, <workflow>, Step 0, <rules>, Step 1, Step 2, Step 3, and </workflow> in canonical order"
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


def detect_duplicate_skill_support_concepts(skill_dir: Path, full_text: str) -> list[str]:
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

        for relative_path, support_concept, normalized_support, support_tokens in support_concepts:
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
        non_empty_lines = [line.rstrip() for line in step_text.splitlines() if line.strip()]
        content_lines = [line for line in non_empty_lines if line.strip() not in structural_lines]

        if not content_lines:
            errors.append(f"{heading} must contain at least one ordered `1.` action.")
            continue

        if not re.match(r"^\d+\.\s+\S", content_lines[0].lstrip()):
            errors.append(
                f"{heading} must start with an ordered `1.` action instead of bare prose."
            )
            continue

        for line in content_lines:
            stripped = line.lstrip()
            if re.match(r"^\d+\.\s+\S", stripped):
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


def lint_skill_markdown(skill_dir: Path, full_text: str) -> LintResult:
    result = LintResult()

    lines = full_text.splitlines()
    if len(lines) > 500:
        result.warnings.append(f"SKILL.md is {len(lines)} lines (recommended <500)")

    assets = skill_dir / "assets"
    if not assets.exists() or not any(assets.iterdir()):
        result.warnings.append("No files in `assets/` — include at least one template")

    references = skill_dir / "references"
    if not references.exists() or not any(references.iterdir()):
        result.warnings.append("No files in `references/` — include docs or examples")

    scripts_dir = skill_dir / "scripts"
    if skill_dir.name in CANONICAL_CREATE_SURFACE_SKILL_NAMES and (
        not scripts_dir.exists() or not any(scripts_dir.iterdir())
    ):
        result.errors.append(
            "Canonical create-surface skills must include a non-empty `scripts/` directory with executable validation or automation."
        )

    filtered_lines = list(iter_code_fence_filtered_lines(full_text))
    filtered_text = "\n".join(filtered_lines)
    result.data["filtered_text"] = filtered_text

    for tag_name in REQUIRED_SKILL_BLOCKS:
        if not has_block_tag(filtered_text, tag_name):
            result.warnings.append(
                f"Missing <{tag_name}> block; use the canonical structure from assets/skill-template.md"
            )

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
    referenced_paths = {
        normalize_relative_path(path)
        for path in [*file_refs, *markdown_links]
        if path.startswith("./") or path.startswith("../")
    }

    for file_ref in file_refs:
        parts = Path(file_ref).parts
        if len(parts) > 2 and not file_ref.startswith(("./", "../")):
            result.warnings.append(f"#file reference appears deep: {file_ref}")

        candidate = resolve_skill_relative_path(skill_dir, file_ref)
        if not candidate.exists():
            result.warnings.append(f"#file reference not found (best-effort): {file_ref}")

    support_dirs = [skill_dir / "assets", skill_dir / "references", skill_dir / "scripts"]
    for support_dir in support_dirs:
        if not support_dir.exists():
            continue
        for candidate in sorted(
            path
            for path in support_dir.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
        ):
            relative_candidate = candidate.relative_to(skill_dir).as_posix()
            if relative_candidate not in referenced_paths:
                result.warnings.append(f"Support file is not referenced from SKILL.md: ./{relative_candidate}")

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

        if Path(relative_support_doc).parts[:1] == ("assets",) and Path(relative_support_doc).name in {
            "agent-template.md",
            "skill-template.md",
        }:
            result.errors.extend(validate_template_asset(relative_support_doc, support_text))

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
        workspace_root = find_workspace_root(skill_dir)
        if workspace_root is None:
            result.errors.append(
                f"Capability references require a workspace root containing `.github/runtime` and `.vscode/mcp.json`: {skill_dir}"
            )
        else:
            source_name = (skill_dir / "SKILL.md").relative_to(workspace_root).as_posix()
            capability_result = validate_skill_capability_refs(
                workspace_root,
                full_text,
                source_name=source_name,
            )
            result.extend(capability_result)

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
        normalized_heading_counts[normalized] = normalized_heading_counts.get(normalized, 0) + 1

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
    result.warnings.extend(detect_duplicate_skill_support_concepts(skill_dir, full_text))
    return result