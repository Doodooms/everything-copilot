from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

import yaml

from ..errors import TargetError
from ..ir import PackSource
from ..ontology import AGENT_PLUGIN_SCHEMA
from ..parser import source_content_digest
from ..validator import (
    DuplicateJSONKeyError,
    load_json_no_duplicate_keys,
    load_pack_yaml_bytes,
    validate_mcp_config,
)
from .common import CompiledTarget, ensure_supported_agent_plugins
from .validation import validate_plugin_manifest


def _read_source_file(source: PackSource, relative: str) -> bytes:
    path = source.root / Path(relative)
    if path.is_symlink():
        raise TargetError(f"source file became a symlink after validation: {relative}")
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(source.root)
        if not resolved.is_file():
            raise TargetError(f"source path is not a regular file: {relative}")
        return resolved.read_bytes()
    except (OSError, ValueError) as exc:
        raise TargetError(f"source file is unavailable or outside the pack: {relative}") from exc


def _read_source_snapshot(source: PackSource) -> Mapping[str, bytes]:
    validated_snapshot = source.source_snapshot
    if tuple(sorted(validated_snapshot)) != source.source_files:
        raise TargetError("pack source snapshot does not match the parsed file list")
    validated_digest = source_content_digest(validated_snapshot)
    if validated_digest != source.ir.content_digest:
        raise TargetError("parsed pack source snapshot does not match its content digest")

    live_snapshot = {
        relative: _read_source_file(source, relative)
        for relative in source.source_files
    }
    actual_digest = source_content_digest(live_snapshot)
    if actual_digest != source.ir.content_digest:
        raise TargetError(
            "pack source changed since parsing; "
            f"expected digest {source.ir.content_digest}, found {actual_digest}"
        )
    return validated_snapshot


def _plugin_manifest(source: PackSource) -> dict[str, object]:
    if "plugin.json" in source.source_snapshot:
        try:
            manifest = load_json_no_duplicate_keys(source.source_snapshot["plugin.json"])
        except (UnicodeError, json.JSONDecodeError, ValueError) as exc:
            raise TargetError("source plugin.json is not valid JSON") from exc
        if not isinstance(manifest, dict):
            raise TargetError("source plugin.json must contain an object")
        validate_plugin_manifest(manifest)
        return manifest
    return {
        "$schema": AGENT_PLUGIN_SCHEMA,
        "name": source.ir.id,
        "description": source.ir.description,
        "version": source.ir.version,
        "author": {"name": source.ir.trust.publisher},
        "extensions": {
            "com.doodooms.agentic-workflow": {
                "integrationManifest": (
                    "com.doodooms.agentic-workflow/integration.yaml"
                )
            }
        },
    }


def _compile_portable_core(
    source: PackSource,
    source_snapshot: Mapping[str, bytes],
) -> CompiledTarget:
    pack = source.ir
    manifest = _plugin_manifest(source)
    validate_plugin_manifest(manifest)
    files: dict[str, bytes] = {
        "plugin.json": (
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
    }

    if source.manifest_path == "pack.yaml":
        try:
            integration = load_pack_yaml_bytes(source_snapshot["pack.yaml"])
        except (KeyError, TargetError) as exc:
            raise TargetError("source pack.yaml is missing from the validated snapshot") from exc
        if not isinstance(integration, dict):
            raise TargetError("source integration metadata must be an object")
        agent_section = integration.get("agents")
        contributions = agent_section.get("contributions") if isinstance(agent_section, dict) else None
        if not isinstance(contributions, list):
            raise TargetError("source integration metadata has invalid agent contributions")
        for contribution in contributions:
            if not isinstance(contribution, dict) or not isinstance(contribution.get("id"), str):
                raise TargetError("source integration metadata has an invalid agent contribution")
            contribution["source"] = (
                "com.doodooms.agentic-workflow/agents/"
                f"{contribution['id']}.agent.md"
            )
        integration_path = "com.doodooms.agentic-workflow/integration.yaml"
        integration_bytes = yaml.safe_dump(
            integration, sort_keys=False, allow_unicode=True
        ).encode("utf-8")
    else:
        integration_path = source.manifest_path
        try:
            integration_bytes = source_snapshot[integration_path]
        except KeyError as exc:
            raise TargetError(
                f"integration manifest is missing from the validated snapshot: {integration_path}"
            ) from exc
    if integration_path != "plugin.json":
        files[integration_path] = integration_bytes

    for contribution in pack.agents.contributions:
        if source.manifest_path == "pack.yaml":
            source_path = contribution.source
            output_path = (
                "com.doodooms.agentic-workflow/agents/"
                f"{contribution.id}.agent.md"
            )
        else:
            source_path = contribution.source
            output_path = source_path
        try:
            content = source_snapshot[source_path]
        except KeyError as exc:
            raise TargetError(
                f"agent source is missing from the validated snapshot: {source_path}"
            ) from exc
        if output_path in files:
            raise TargetError(f"duplicate integration source path: {output_path}")
        files[output_path] = content

    for skill in pack.skills:
        prefix = f"{skill.path.rstrip('/')}/"
        package_files = [
            relative
            for relative in source.source_files
            if relative.startswith(prefix)
        ]
        if not package_files:
            raise TargetError(f"skill package has no source files: {skill.id}")
        for relative in package_files:
            suffix = relative[len(prefix) :]
            output_path = f"skills/{skill.id}/{suffix}"
            if output_path in files:
                raise TargetError(f"duplicate portable output path: {output_path}")
            try:
                files[output_path] = source_snapshot[relative]
            except KeyError as exc:
                raise TargetError(
                    f"source file is absent from the validated snapshot: {relative}"
                ) from exc

    if pack.mcp_config is not None:
        try:
            raw_mcp = source_snapshot[pack.mcp_config]
        except KeyError as exc:
            raise TargetError(
                f"MCP configuration is absent from the validated snapshot: {pack.mcp_config}"
            ) from exc
        try:
            mcp_manifest = load_json_no_duplicate_keys(raw_mcp)
        except DuplicateJSONKeyError as exc:
            raise TargetError(f"source mcp.json contains duplicate JSON key {exc.key!r}") from exc
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise TargetError("source mcp.json is not valid UTF-8 JSON") from exc
        errors: list[str] = []
        server_ids = validate_mcp_config(mcp_manifest, "mcp.json", errors)
        if errors:
            raise TargetError("; ".join(sorted(errors)))
        if server_ids != {server.id for server in pack.mcp_servers}:
            raise TargetError("source mcp.json server IDs changed after pack validation")
        files["mcp.json"] = raw_mcp

    return CompiledTarget.create(
        "portable",
        pack.reference,
        files,
        source_digest=pack.content_digest,
    )


def compile_portable(source: PackSource) -> CompiledTarget:
    if "portable" not in source.ir.compatibility.targets:
        raise TargetError(f"pack {source.ir.id!r} does not support the portable target")
    ensure_supported_agent_plugins(source)
    return _compile_portable_core(source, _read_source_snapshot(source))
