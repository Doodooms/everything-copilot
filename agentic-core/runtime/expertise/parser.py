from __future__ import annotations

import hashlib
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Any

from .errors import PackValidationError, TargetError
from .ir import (
    AgentContribution,
    AgentContributions,
    AgentExtension,
    AgentProjection,
    Capability,
    Compatibility,
    Dependency,
    MCPServer,
    PackIR,
    PackSource,
    SkillComponent,
    TrustMetadata,
)
from .ontology import (
    AGENT_PLUGIN_SCHEMA,
    RELATIVE_PATH_PATTERN,
    parse_agent_plugins_requirement,
)
from .validator import (
    load_json_no_duplicate_keys,
    load_pack_yaml_bytes,
    validate_pack_document,
)


def source_content_digest(files: Mapping[str, bytes]) -> str:
    digest = hashlib.sha256()
    for relative, data in sorted(files.items()):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def _capture_source_snapshot(
    root: Path,
    relative_files: tuple[str, ...],
    manifest_path: str,
    manifest_bytes: bytes,
    initial_files: Mapping[str, bytes] | None = None,
) -> Mapping[str, bytes]:
    snapshot = dict(initial_files or {})
    snapshot[manifest_path] = manifest_bytes
    for relative in sorted(set(relative_files) - set(snapshot)):
        relative_path = Path(relative)
        if relative_path.is_absolute() or any(
            part in {"", ".", ".."} for part in relative.split("/")
        ):
            raise PackValidationError(
                (f"source path is unsafe while capturing snapshot: {relative}",)
            )

        current = root
        for part in relative_path.parts:
            current = current / part
            if current.is_symlink():
                raise PackValidationError(
                    (f"{relative}: source path contains a symlink",)
                )
        try:
            resolved = current.resolve(strict=True)
            resolved.relative_to(root)
            if not resolved.is_file():
                raise PackValidationError(
                    (f"{relative}: source path is not a regular file",)
                )
            snapshot[relative] = resolved.read_bytes()
        except PackValidationError:
            raise
        except (OSError, RuntimeError, ValueError) as exc:
            raise PackValidationError(
                (f"{relative}: source file is unavailable or outside the pack",)
            ) from exc
    return MappingProxyType(snapshot)


def _load_pack_source_manifest(
    root: Path,
) -> tuple[str, bytes, dict[str, bytes], Any]:
    pack_manifest = root / "pack.yaml"
    if pack_manifest.exists() or pack_manifest.is_symlink():
        if pack_manifest.is_symlink() or not pack_manifest.is_file():
            raise PackValidationError(
                ("pack.yaml: manifest must be a regular file at the pack root",)
            )
        try:
            content = pack_manifest.read_bytes()
        except OSError as exc:
            raise PackValidationError(
                ("pack.yaml: manifest could not be read",)
            ) from exc
        document = load_pack_yaml_bytes(content, source_name="pack.yaml")
        return "pack.yaml", content, {}, document

    plugin_path = root / "plugin.json"
    if not plugin_path.is_file() or plugin_path.is_symlink():
        raise PackValidationError(
            (
                "source must contain pack.yaml or an Agent Plugin plugin.json with integration metadata",
            )
        )
    try:
        plugin_bytes = plugin_path.read_bytes()
        plugin = load_json_no_duplicate_keys(plugin_bytes)
    except (OSError, UnicodeError, ValueError) as exc:
        raise PackValidationError(
            (f"plugin.json: cannot parse plugin manifest: {exc}",)
        ) from exc

    from .targets.validation import validate_plugin_manifest

    try:
        validate_plugin_manifest(plugin)
    except TargetError as exc:
        raise PackValidationError((f"plugin.json: {exc}",)) from exc

    if not isinstance(plugin, dict) or plugin.get("$schema") != AGENT_PLUGIN_SCHEMA:
        raise PackValidationError(
            ("plugin.json: source must declare Agent Plugins 1.0",)
        )
    extension = plugin.get("extensions", {}).get("com.doodooms.agentic-workflow")
    if not isinstance(extension, dict):
        raise PackValidationError(
            (
                "plugin.json: missing extensions.com.doodooms.agentic-workflow integration metadata",
            )
        )
    integration_path = extension.get("integrationManifest")
    if (
        not isinstance(integration_path, str)
        or RELATIVE_PATH_PATTERN.fullmatch(integration_path) is None
        or PurePosixPath(integration_path).is_absolute()
        or any(part in {"", ".", ".."} for part in integration_path.split("/"))
    ):
        raise PackValidationError(
            (
                "plugin.json: integrationManifest must be a safe plugin-root-relative path",
            )
        )

    current = root
    for part in PurePosixPath(integration_path).parts:
        current = current / part
        if current.is_symlink():
            raise PackValidationError(
                ("plugin.json: integration manifest path must not contain symlinks",)
            )
    try:
        resolved = current.resolve(strict=True)
        resolved.relative_to(root)
        if not resolved.is_file():
            raise PackValidationError(
                ("plugin.json: integration manifest must be a regular file",)
            )
        integration_bytes = resolved.read_bytes()
    except PackValidationError:
        raise
    except (OSError, RuntimeError, ValueError) as exc:
        raise PackValidationError(
            (
                "plugin.json: integration manifest is unavailable or outside the plugin root",
            )
        ) from exc

    document = load_pack_yaml_bytes(integration_bytes, source_name=integration_path)
    if not isinstance(document, dict):
        raise PackValidationError(
            (f"{integration_path}: integration manifest must be an object",)
        )
    if plugin.get("name") != document.get("id"):
        raise PackValidationError(
            ("plugin.json: name must match integration manifest id",)
        )
    if plugin.get("version") != document.get("version"):
        raise PackValidationError(
            ("plugin.json: version must match integration manifest version",)
        )
    return (
        integration_path,
        integration_bytes,
        {"plugin.json": plugin_bytes},
        document,
    )


def parse_pack(
    source_root: Path,
    *,
    known_agents: set[str] | frozenset[str] = frozenset(),
) -> PackSource:
    """Parse and structurally validate one local pack source without mutating it."""
    try:
        root = Path(source_root).resolve(strict=True)
    except OSError as exc:
        raise PackValidationError(
            (f"pack source is unavailable: {source_root}",)
        ) from exc
    if not root.is_dir():
        raise PackValidationError((f"pack source is not a directory: {source_root}",))

    (
        manifest_relative_path,
        manifest_bytes,
        initial_files,
        document,
    ) = _load_pack_source_manifest(root)
    initial_source_files = tuple(initial_files)
    agent_catalog = frozenset(known_agents)
    discovery = validate_pack_document(
        document,
        root,
        known_agents=agent_catalog,
        discover_only=True,
        manifest_path=manifest_relative_path,
        initial_source_files=initial_source_files,
    )
    if discovery.diagnostics:
        raise PackValidationError(discovery.diagnostics)

    source_snapshot = _capture_source_snapshot(
        root,
        discovery.source_files,
        manifest_relative_path,
        manifest_bytes,
        initial_files,
    )
    report = validate_pack_document(
        document,
        root,
        known_agents=agent_catalog,
        source_snapshot=source_snapshot,
        manifest_path=manifest_relative_path,
        initial_source_files=initial_source_files,
    )
    if report.diagnostics:
        raise PackValidationError(report.diagnostics)
    if report.source_files != discovery.source_files:
        raise PackValidationError(
            ("pack source paths changed during snapshot capture",)
        )

    compatibility = document["compatibility"]
    trust = document["trust"]
    agents = document["agents"]
    ir = PackIR(
        schema_version=document["schema_version"],
        id=document["id"],
        type=document["type"],
        name=document["name"],
        version=document["version"],
        description=document["description"],
        compatibility=Compatibility(
            targets=tuple(sorted(compatibility["targets"])),
            agent_plugins=parse_agent_plugins_requirement(
                compatibility["agent_plugins"]
            )[0],
        ),
        trust=TrustMetadata(
            publisher=trust["publisher"],
            source=trust["source"],
            approval_required=trust["approval_required"],
            digest=trust.get("digest"),
        ),
        capabilities=tuple(
            Capability(id=item["id"], description=item["description"])
            for item in sorted(document["capabilities"], key=lambda row: row["id"])
        ),
        dependencies=tuple(
            Dependency(
                capability=item["capability"],
                pack_id=item.get("pack_id"),
                minimum_version=item.get("minimum_version"),
            )
            for item in sorted(
                document["dependencies"],
                key=lambda row: (
                    row["capability"],
                    row.get("pack_id") or "",
                    row.get("minimum_version") or "",
                ),
            )
        ),
        agents=AgentContributions(
            contributions=tuple(
                AgentContribution(
                    id=item["id"],
                    source=item["source"],
                    capabilities=tuple(sorted(item["capabilities"])),
                )
                for item in sorted(agents["contributions"], key=lambda row: row["id"])
            ),
            extensions=tuple(
                AgentExtension(
                    agent_id=item["agent_id"],
                    capabilities=tuple(sorted(item["capabilities"])),
                )
                for item in sorted(
                    agents["extensions"], key=lambda row: row["agent_id"]
                )
            ),
        ),
        skills=tuple(
            SkillComponent(
                id=item["id"],
                path=item["path"],
                capabilities=tuple(sorted(item["capabilities"])),
            )
            for item in sorted(document["skills"], key=lambda row: row["id"])
        ),
        mcp_config=document["mcp_config"],
        mcp_servers=tuple(
            MCPServer(
                id=item["id"],
                capabilities=tuple(sorted(item["capabilities"])),
                permissions=tuple(sorted(item["permissions"])),
                tools=tuple(sorted(item.get("tools", []))),
            )
            for item in sorted(document["mcp_servers"], key=lambda row: row["id"])
        ),
        projections=tuple(
            AgentProjection(
                agent_id=item["agent_id"],
                capabilities=tuple(sorted(item["capabilities"])),
                skills=tuple(sorted(item["skills"])),
                mcp_servers=tuple(sorted(item["mcp_servers"])),
            )
            for item in sorted(document["projections"], key=lambda row: row["agent_id"])
        ),
        content_digest=source_content_digest(source_snapshot),
    )
    return PackSource(
        root=root,
        ir=ir,
        source_files=report.source_files,
        manifest_path=manifest_relative_path,
        source_snapshot=source_snapshot,
        known_agents=agent_catalog,
    )
