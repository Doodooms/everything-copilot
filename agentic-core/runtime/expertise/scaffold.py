from __future__ import annotations

import tempfile
from collections.abc import Iterable
from pathlib import Path

import yaml

from .errors import PackValidationError
from .ontology import (
    CAPABILITY_ID_PATTERN,
    COMPONENT_ID_PATTERN,
    PACK_ID_PATTERN,
    PLUGIN_TYPES,
    SUPPORTED_TARGETS,
    VERSION_PATTERN,
    parse_agent_plugins_requirement,
)
from .parser import parse_pack
from .targets import compile_target


def scaffold_pack(
    repository_root: Path,
    *,
    pack_id: str,
    name: str,
    description: str,
    capability: str,
    skill_id: str,
    skill_description: str,
    project_to: Iterable[str],
    publisher: str,
    source: str,
    version: str = "0.1.0",
    pack_type: str = "horizontal",
    targets: Iterable[str] = SUPPORTED_TARGETS,
    known_agents: Iterable[str] = (),
) -> dict[str, object]:
    root = Path(repository_root).resolve(strict=True)
    if not root.is_dir():
        raise PackValidationError(("repository root must be a directory",))
    if (
        not isinstance(pack_id, str)
        or not PACK_ID_PATTERN.fullmatch(pack_id)
        or len(pack_id) > 64
    ):
        raise PackValidationError(
            ("pack_id must be a lowercase hyphenated ID of at most 64 characters",)
        )
    if not isinstance(pack_type, str) or pack_type not in PLUGIN_TYPES:
        raise PackValidationError(("pack_type must be horizontal or vertical",))
    if not isinstance(version, str) or VERSION_PATTERN.fullmatch(version) is None:
        raise PackValidationError(("version must be a semantic version",))
    try:
        compatibility = parse_agent_plugins_requirement(">=1.0")[0]
    except ValueError as exc:
        raise PackValidationError(
            (f"built-in compatibility default is invalid: {exc}",)
        ) from exc

    for label, value in (
        ("name", name),
        ("description", description),
        ("skill_description", skill_description),
        ("publisher", publisher),
        ("source", source),
    ):
        if not isinstance(value, str) or not value.strip():
            raise PackValidationError((f"{label} must be non-empty text",))
    if (
        not isinstance(capability, str)
        or CAPABILITY_ID_PATTERN.fullmatch(capability) is None
    ):
        raise PackValidationError(
            ("capability must be a valid dotted/hyphenated capability ID",)
        )
    if (
        not isinstance(skill_id, str)
        or COMPONENT_ID_PATTERN.fullmatch(skill_id) is None
        or len(skill_id) > 64
    ):
        raise PackValidationError(
            ("skill_id must be a lowercase hyphenated component ID",)
        )

    selected_targets = tuple(sorted(set(targets)))
    if not selected_targets or any(
        target not in SUPPORTED_TARGETS for target in selected_targets
    ):
        raise PackValidationError(
            "targets must contain one or more of: "
            + ", ".join(sorted(SUPPORTED_TARGETS))
        )

    selected_agents = tuple(sorted(set(project_to)))
    catalog = frozenset(known_agents)
    unknown_agents = sorted(set(selected_agents) - catalog)
    if unknown_agents:
        raise PackValidationError(
            "project_to contains unknown agents: " + ", ".join(unknown_agents)
        )

    packs_root = root / "expertise" / "packs"
    if packs_root.is_symlink():
        raise PackValidationError("expertise/packs must not be a symlink")
    packs_root.mkdir(parents=True, exist_ok=True)
    try:
        packs_root.resolve(strict=True).relative_to(root)
    except (OSError, ValueError) as exc:
        raise PackValidationError(
            "expertise/packs must remain inside the repository"
        ) from exc

    destination = packs_root / pack_id
    if destination.exists() or destination.is_symlink():
        raise PackValidationError(f"pack destination already exists: {destination}")

    manifest = {
        "schema_version": 1,
        "id": pack_id,
        "type": pack_type,
        "name": name.strip(),
        "version": version,
        "description": description.strip(),
        "compatibility": {
            "targets": list(selected_targets),
            "agent_plugins": compatibility,
        },
        "trust": {
            "publisher": publisher.strip(),
            "source": source.strip(),
            "approval_required": True,
        },
        "capabilities": [{"id": capability, "description": description.strip()}],
        "dependencies": [],
        "agents": {
            "contributions": [],
            "extensions": [
                {"agent_id": agent_id, "capabilities": [capability]}
                for agent_id in selected_agents
            ],
        },
        "skills": [
            {
                "id": skill_id,
                "path": f"skills/{skill_id}",
                "capabilities": [capability],
            }
        ],
        "mcp_config": None,
        "mcp_servers": [],
        "projections": [
            {
                "agent_id": agent_id,
                "capabilities": [capability],
                "skills": [skill_id],
                "mcp_servers": [],
            }
            for agent_id in selected_agents
        ],
    }

    try:
        with tempfile.TemporaryDirectory(
            prefix=".plugin-scaffold-", dir=packs_root
        ) as staging_directory:
            staging_root = Path(staging_directory) / pack_id
            skill_root = staging_root / "skills" / skill_id
            skill_root.mkdir(parents=True)
            (staging_root / "pack.yaml").write_text(
                yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            (skill_root / "SKILL.md").write_text(
                "---\n"
                f"name: {skill_id}\n"
                f"description: {skill_description.strip()}\n"
                "---\n\n"
                f"Use this skill when the task requires: {skill_description.strip()}\n\n"
                "<workflow>\n\n"
                "## Step 1 - Define the method\n\n"
                "1. Replace this scaffold with the approved workflow, evidence requirements, "
                "and bounded return contract.\n\n"
                "## Step 2 - Validate the method\n\n"
                "1. Add only references, assets, or scripts consumed by this workflow.\n\n"
                "</workflow>\n",
                encoding="utf-8",
            )

            parsed = parse_pack(staging_root, known_agents=catalog)
            artifacts = {
                target: compile_target(parsed, target) for target in selected_targets
            }
            expected_outputs = {
                target: sorted(artifact.files)
                for target, artifact in sorted(artifacts.items())
            }
            if destination.exists() or destination.is_symlink():
                raise PackValidationError(
                    f"pack destination appeared during scaffold: {destination}"
                )
            staging_root.rename(destination)
    except PackValidationError:
        raise
    except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
        raise PackValidationError(
            (f"could not scaffold pack {pack_id!r}: {exc}",)
        ) from exc

    return {
        "status": "scaffolded",
        "pack": pack_id,
        "source": destination.relative_to(root).as_posix(),
        "targets": list(selected_targets),
        "projected_agents": list(selected_agents),
        "build_outputs": expected_outputs,
    }
