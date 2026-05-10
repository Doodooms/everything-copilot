from pathlib import Path
import difflib
import json
import re

import typer
import yaml


app = typer.Typer()
TOOL_SNAPSHOT_PATH = Path(".vscode") / "copilot-tools.snapshot.json"
AGENT_FILE_PATTERNS = (
    ".github/agents/*.agent.md",
    ".github/agents/**/*.agent.md",
)
BUILTIN_SKILL_TOOL_NAMES = {
    "agent",
    "browser",
    "edit",
    "execute",
    "execute/getTerminalOutput",
    "read",
    "read/terminalLastCommand",
    "search",
    "search/codebase",
    "search/usages",
    "todo",
    "vscode/askQuestions",
    "vscode/memory",
    "vscode/vscodeAPI",
    "web",
    "web/fetch",
}
EXTENSION_MANIFEST_PATTERNS = (
    ".vscode/extensions/*/package.json",
    ".vscode-insiders/extensions/*/package.json",
    ".vscode-server/extensions/*/package.json",
    ".vscode-server/bin/*/extensions/*/package.json",
    ".vscode-insiders-server/extensions/*/package.json",
    ".vscode-insiders-server/bin/*/extensions/*/package.json",
)
WRONG_LAYER_TOOL_SUGGESTIONS = {
    "copilot_listDirectory": ["read"],
    "copilot_readFile": ["read"],
    "copilot_searchCodebase": ["search", "search/codebase"],
    "create_and_run_task": ["execute"],
    "explore_subagent": ["agent"],
    "run_in_terminal": ["execute"],
    "run_task": ["execute"],
    "runSubagent": ["agent"],
    "search_subagent": ["agent", "search/codebase"],
    "vscode_askQuestions": ["vscode/askQuestions"],
}
REQUIRED_SKILL_BLOCKS = ("rules", "workflow")
TEMPLATE_LEFTOVER_MARKERS = {
    "<what this skill does>": "Unresolved template placeholder `<what this skill does>` found; replace it with the actual skill purpose.",
    "<trigger phrases or scenarios that should cause the agent to load this skill>": "Unresolved template placeholder for discovery text found; replace it with real trigger phrases.",
    "<inspect or prepare>": "Unresolved workflow step placeholder `<inspect or prepare>` found; replace template step titles with concrete steps.",
    "<ask or decide>": "Unresolved workflow step placeholder `<ask or decide>` found; replace template step titles with concrete steps.",
    "<validate or execute>": "Unresolved workflow step placeholder `<validate or execute>` found; replace template step titles with concrete steps.",
    "./references/<guide>.md": "Template file reference `./references/<guide>.md` found; replace it with a real support-file path or remove it.",
    "./assets/<questions>.json": "Template file reference `./assets/<questions>.json` found; replace it with a real support-file path or remove it.",
    "./scripts/<validator>.py": "Template file reference `./scripts/<validator>.py` found; replace it with a real validator path or remove it.",
}


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
    heading = re.sub(r"^step\s+\d+\s*[-—:]\s*", "", heading)
    heading = re.sub(r"\s+", " ", heading)
    return heading


def contains_runtime_inputs_heading(text: str) -> bool:
    for heading in iter_markdown_headings(text):
        if normalize_heading(heading) == "runtime inputs":
            return True
    return False


def has_block_tag(text: str, tag_name: str) -> bool:
    return f"<{tag_name}>" in text and f"</{tag_name}>" in text


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
        for match in re.finditer(r"\[[^\]]+\]\((\./[^)]+)\)", line):
            yield match.group(1)


def normalize_relative_path(path_str: str) -> str:
    path = Path(path_str.strip())
    normalized = Path(*[part for part in path.parts if part not in (".", "")])
    return normalized.as_posix()


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


def find_workspace_root(start: Path):
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists() or (candidate / ".vscode").exists():
            return candidate
    return None


def add_toolset_member(groups, toolset_name: str, tool_name: str, source: str):
    if not toolset_name:
        return

    entry = groups.get(toolset_name)
    if not entry:
        entry = {"members": set(), "sources": set()}
        groups[toolset_name] = entry

    entry["members"].add(tool_name)
    entry["sources"].add(source)


def build_toolset_names(tools):
    groups = {}
    for tool in tools:
        tool_name = tool.get("name")
        if not isinstance(tool_name, str) or not tool_name:
            continue

        prefix = tool.get("prefix")
        if isinstance(prefix, str) and prefix:
            add_toolset_member(groups, prefix, tool_name, "name-prefix")

        for tag in tool.get("tags", []):
            if isinstance(tag, str) and tag:
                add_toolset_member(groups, tag, tool_name, "tag")

    return {
        toolset_name
        for toolset_name, group in groups.items()
        if len(group["members"]) > 1
    }


def load_tool_snapshot(skill_dir: Path):
    workspace_root = find_workspace_root(skill_dir)
    if not workspace_root:
        return None, None

    snapshot_path = workspace_root / TOOL_SNAPSHOT_PATH
    if not snapshot_path.exists():
        return None, None

    try:
        data = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, f"Tool snapshot could not be parsed: {snapshot_path} ({exc})"

    tool_names = {
        item.get("name")
        for item in data.get("tools", [])
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    toolset_names = {
        item.get("name")
        for item in data.get("toolSets", [])
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }

    return {
        "label": f"tool snapshot {snapshot_path}",
        "method": data.get("_method", "runtime-snapshot"),
        "tool_names": {name for name in tool_names if name},
        "toolset_names": {name for name in toolset_names if name},
    }, None


def iter_extension_manifest_paths():
    seen_paths = set()
    home = Path.home()
    for pattern in EXTENSION_MANIFEST_PATTERNS:
        for manifest_path in sorted(home.glob(pattern)):
            resolved = manifest_path.resolve()
            if resolved in seen_paths:
                continue
            seen_paths.add(resolved)
            yield resolved


def scan_extension_manifests():
    tools_by_name = {}
    manifest_paths = list(iter_extension_manifest_paths())
    if not manifest_paths:
        return None, "No VS Code extension manifests were found for static tool validation."

    for manifest_path in manifest_paths:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        tool_entries = manifest.get("contributes", {}).get("languageModelTools", [])
        if not isinstance(tool_entries, list):
            continue

        for tool_entry in tool_entries:
            if not isinstance(tool_entry, dict):
                continue

            tool_name = tool_entry.get("name")
            if not isinstance(tool_name, str) or not tool_name:
                continue

            tags = [
                tag
                for tag in tool_entry.get("tags", [])
                if isinstance(tag, str) and tag
            ]
            description = (
                tool_entry.get("modelDescription")
                or tool_entry.get("userDescription")
                or tool_entry.get("description")
                or ""
            )

            existing = tools_by_name.get(tool_name)
            if not existing:
                tools_by_name[tool_name] = {
                    "name": tool_name,
                    "description": description,
                    "tags": tags,
                    "prefix": tool_name.split("/", 1)[0] if "/" in tool_name else None,
                }
                continue

            existing_tags = set(existing.get("tags", []))
            existing_tags.update(tags)
            existing["tags"] = sorted(existing_tags)
            if len(description) > len(existing.get("description", "")):
                existing["description"] = description

    if not tools_by_name:
        return None, "No installed extension manifests contributed languageModelTools for static validation."

    tools = sorted(tools_by_name.values(), key=lambda item: item["name"])
    return {
        "label": "installed extension manifests",
        "method": "static-manifest-scan",
        "tool_names": {tool["name"] for tool in tools},
        "toolset_names": build_toolset_names(tools),
    }, None


def load_skill_tool_alias_catalog(skill_dir: Path):
    workspace_root = find_workspace_root(skill_dir)
    tool_names = set(BUILTIN_SKILL_TOOL_NAMES)

    if workspace_root:
        for pattern in AGENT_FILE_PATTERNS:
            for agent_file in sorted(workspace_root.glob(pattern)):
                frontmatter, _ = read_frontmatter(agent_file)
                if not isinstance(frontmatter, dict):
                    continue
                tools = frontmatter.get("tools", [])
                if not isinstance(tools, list):
                    continue
                for tool_name in tools:
                    if isinstance(tool_name, str) and tool_name:
                        tool_names.add(tool_name)

    return {
        "label": "workspace skill-tool aliases",
        "method": "skill-alias-catalog",
        "tool_names": tool_names,
    }, None


def load_runtime_tool_catalog(skill_dir: Path):
    warnings = []
    catalogs = []

    snapshot_catalog, snapshot_error = load_tool_snapshot(skill_dir)
    if snapshot_error:
        warnings.append(snapshot_error)
    if snapshot_catalog:
        catalogs.append(snapshot_catalog)

    manifest_catalog, manifest_error = scan_extension_manifests()
    if manifest_error and not snapshot_catalog:
        warnings.append(manifest_error)
    if manifest_catalog:
        catalogs.append(manifest_catalog)

    if not catalogs:
        return None, warnings

    return {
        "label": " + ".join(catalog["label"] for catalog in catalogs),
        "method": "+".join(catalog["method"] for catalog in catalogs),
        "tool_names": set().union(*(catalog["tool_names"] for catalog in catalogs)),
        "toolset_names": set().union(*(catalog["toolset_names"] for catalog in catalogs)),
    }, warnings


def build_tool_suggestions(tool_ref: str, valid_tool_names):
    suggestions = []

    for alias_suggestion in WRONG_LAYER_TOOL_SUGGESTIONS.get(tool_ref, []):
        if alias_suggestion in valid_tool_names and alias_suggestion not in suggestions:
            suggestions.append(alias_suggestion)

    close_matches = difflib.get_close_matches(tool_ref, sorted(valid_tool_names), n=5, cutoff=0.45)
    for suggestion in close_matches:
        if suggestion not in suggestions:
            suggestions.append(suggestion)

    return suggestions


def read_frontmatter(path: Path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    fm_text = parts[1]
    rest = parts[2]
    try:
        fm = yaml.safe_load(fm_text)
    except Exception:
        return None, text
    return fm, text


@app.command()
def validate(skill_dir: Path = Path(".")):
    skill_dir = skill_dir.resolve()
    md = skill_dir / "SKILL.md"
    if not md.exists():
        typer.echo(f"ERROR: SKILL.md not found in {skill_dir}")
        raise typer.Exit(code=2)

    fm, full_text = read_frontmatter(md)
    errors = []
    warnings = []

    if not fm:
        errors.append("Missing or invalid YAML frontmatter in SKILL.md")
    else:
        for key in ("name", "description", "user-invocable"):
            if key not in fm:
                errors.append(f"Missing frontmatter key: {key}")
        if "name" in fm and fm["name"] != skill_dir.name:
            warnings.append(f"Frontmatter name '{fm.get('name')}' != folder name '{skill_dir.name}'")
        if "context" in fm and "compatibility" not in fm:
            warnings.append(
                "Frontmatter uses `context` without `compatibility`; declare compatibility bounds for version-gated behavior"
            )

    lines = full_text.splitlines()
    if len(lines) > 500:
        warnings.append(f"SKILL.md is {len(lines)} lines (recommended <500)")

    assets = skill_dir / "assets"
    if not assets.exists() or not any(assets.iterdir()):
        warnings.append("No files in `assets/` — include at least one template")

    refs = skill_dir / "references"
    if not refs.exists() or not any(refs.iterdir()):
        warnings.append("No files in `references/` — include docs or examples")

    filtered_lines = list(iter_code_fence_filtered_lines(full_text))
    filtered_text = "\n".join(filtered_lines)

    for tag_name in REQUIRED_SKILL_BLOCKS:
        if not has_block_tag(filtered_text, tag_name):
            warnings.append(
                f"Missing <{tag_name}> block; use the canonical structure from assets/skill-template.md"
            )

    for marker, message in TEMPLATE_LEFTOVER_MARKERS.items():
        if marker in filtered_text:
            errors.append(message)

    file_refs = []
    file_ref_has_trailing_punctuation = False
    for match in re.finditer(r"#file:\s*([^\s`]+)", filtered_text):
        raw_ref = match.group(1)
        clean_ref = raw_ref.rstrip(".,;:")
        if clean_ref != raw_ref:
            file_ref_has_trailing_punctuation = True
        file_refs.append(clean_ref)

    markdown_links = list(iter_relative_markdown_links(full_text))
    referenced_paths = {
        normalize_relative_path(path)
        for path in [*file_refs, *markdown_links]
        if path.startswith("./") or path.startswith("../")
    }
    for file_ref in file_refs:
        parts = Path(file_ref).parts
        if len(parts) > 2 and not file_ref.startswith("./"):
            warnings.append(f"#file reference appears deep: {file_ref}")

        candidate = skill_dir.joinpath(file_ref.lstrip("./"))
        if not candidate.exists():
            warnings.append(f"#file reference not found (best-effort): {file_ref}")

    support_dirs = [skill_dir / "assets", skill_dir / "references", skill_dir / "scripts"]
    for support_dir in support_dirs:
        if not support_dir.exists():
            continue
        for candidate in sorted(path for path in support_dir.rglob("*") if path.is_file()):
            relative_candidate = candidate.relative_to(skill_dir).as_posix()
            if relative_candidate not in referenced_paths:
                warnings.append(f"Support file is not referenced from SKILL.md: ./{relative_candidate}")

    for support_doc in iter_non_frontmatter_markdown_files(skill_dir):
        _, support_text = read_frontmatter(support_doc)
        filtered_support_text = "\n".join(iter_code_fence_filtered_lines(support_text))
        relative_support_doc = support_doc.relative_to(skill_dir).as_posix()

        if re.search(r"#file:\s*([^\s`]+)", filtered_support_text):
            errors.append(
                f"Active #file marker found in non-frontmatter markdown file: ./{relative_support_doc}. Use markdown links such as [file](./path) or [file](../path) in support docs."
            )

        if re.search(r"#tool:([^\s`]+)", filtered_support_text):
            errors.append(
                f"Active #tool marker found in non-frontmatter markdown file: ./{relative_support_doc}. Reserve #tool for frontmatter-bearing skill, agent, or prompt definitions and use inline tool names in support docs."
            )

    tool_ref_has_trailing_punctuation = False
    tool_refs = []
    for match in re.finditer(r"#tool:([^\s`]+)", filtered_text):
        raw_ref = match.group(1)
        clean_ref = raw_ref.rstrip(".,;:")
        if clean_ref != raw_ref:
            tool_ref_has_trailing_punctuation = True
        tool_refs.append(clean_ref)

    if not tool_refs:
        warnings.append(
            "No `#tool:` references found; ensure you reference required tools (e.g., #tool:vscode/askQuestions)"
        )

    raw_tool_markers = len(re.findall(r"#tool:", filtered_text))
    if raw_tool_markers > len(tool_refs):
        warnings.append("One or more `#tool:` markers appear malformed or empty")

    if tool_ref_has_trailing_punctuation:
        warnings.append(
            "One or more `#tool:` references are followed by punctuation; keep tool references free of trailing commas or periods"
        )

    skill_tool_catalog, _ = load_skill_tool_alias_catalog(skill_dir)
    runtime_tool_catalog, runtime_tool_catalog_warnings = load_runtime_tool_catalog(skill_dir)
    warnings.extend(runtime_tool_catalog_warnings)
    if skill_tool_catalog:
        valid_tool_names = sorted(skill_tool_catalog["tool_names"])
        for tool_ref in sorted(set(tool_refs)):
            if tool_ref in valid_tool_names:
                continue
            suggestions = build_tool_suggestions(tool_ref, valid_tool_names)
            suggestion_text = f" Closest matches: {', '.join(suggestions)}" if suggestions else ""
            wrong_layer_text = " Wrong-layer raw tool name detected." if tool_ref in WRONG_LAYER_TOOL_SUGGESTIONS else ""
            runtime_text = ""
            if runtime_tool_catalog and tool_ref in (runtime_tool_catalog["tool_names"] | runtime_tool_catalog["toolset_names"]):
                runtime_text = " This name exists in the raw runtime registry but is not the skill-facing alias."
            errors.append(
                f"#tool reference not found in {skill_tool_catalog['label']}: {tool_ref}.{wrong_layer_text}{runtime_text}{suggestion_text}"
            )
    elif tool_refs:
        warnings.append(
            "No workspace skill-tool alias catalog was available; #tool references could not be checked deterministically."
        )

    if file_ref_has_trailing_punctuation:
        warnings.append(
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
        warnings.append(
            f"Potential duplicate section heading after normalization: '{heading}' appears multiple times; keep one canonical section and reference it elsewhere"
        )

    if contains_runtime_inputs_heading(full_text):
        warnings.append(
            "`## Runtime Inputs` encourages eager loading; cite support files on the workflow step that actually consumes them"
        )

    if errors:
        typer.echo("ERRORS:")
        for error in errors:
            typer.echo(f"  - {error}")
    if warnings:
        typer.echo("WARNINGS:")
        for warning in warnings:
            typer.echo(f"  - {warning}")
    if errors:
        raise typer.Exit(code=3)
    typer.echo("Validation passed (warnings may need attention).")
    raise typer.Exit(code=0)

if __name__ == '__main__':
    app()