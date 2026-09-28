from __future__ import annotations

import base64
import json
import os
import shutil
import sys
import uuid
from collections.abc import Iterable, Mapping
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Any

from expertise.errors import ExpertiseError
from expertise.ir import EffectiveIR, PackReference, PackSource
from expertise.ontology import (
    CAPABILITY_ID_PATTERN,
    MCP_SCHEMA,
    PACK_ID_PATTERN,
    VERSION_PATTERN,
    canonical_digest,
    parse_version,
)
from expertise.parser import parse_pack, source_content_digest
from expertise.registry import LocalPackRegistry
from expertise.resolver import _version_key, resolve_effective_ir
from expertise.targets import (
    compile_target,
    validate_mcp_manifest,
    validate_plugin_manifest,
)
from expertise.targets.common import (
    CompiledTarget,
    ensure_supported_agent_plugins,
    validate_target_files,
)
from expertise.targets.copilot import _validate_agent
from expertise.validator import load_json_no_duplicate_keys, load_pack_yaml_bytes

from .models import (
    ActiveSet,
    EffectiveProfile,
    ManagedEffectiveIR,
    PluginControlError,
    TrustedRegistry,
    TrustedSource,
)

_CORE_PACKAGE_ROOT = Path(__file__).resolve().parents[2]
if str(_CORE_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(_CORE_PACKAGE_ROOT))
from core_agents import load_core_agents

_HEX_DIGEST = frozenset("0123456789abcdef")
_INSTALL_RECORD_FIELDS = {
    "schema_version",
    "id",
    "version",
    "digest",
    "publisher",
    "source",
    "trusted_source_path",
    "approved",
}
_PROFILE_FIELDS = {"schema_version", "active_packs", "capabilities"}


def _digest_is_valid(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in _HEX_DIGEST for character in value)
    )


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def _safe_relative_path(relative: str) -> Path:
    path = PurePosixPath(relative)
    if (
        not isinstance(relative, str)
        or not relative
        or path.is_absolute()
        or "\\" in relative
        or any(part in {"", ".", ".."} for part in relative.split("/"))
        or ":" in relative
        or ".github" in path.parts
    ):
        raise PluginControlError(f"unsafe plugin-store path: {relative!r}")
    return Path(*path.parts)


def _ensure_no_symlink(path: Path, description: str) -> None:
    if path.is_symlink():
        raise PluginControlError(f"{description} must not be a symlink: {path}")


def _read_regular_file(path: Path, root: Path, description: str) -> bytes:
    _ensure_no_symlink(path, description)
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(root.resolve(strict=True))
        if not resolved.is_file():
            raise PluginControlError(f"{description} is not a regular file: {path}")
        return resolved.read_bytes()
    except PluginControlError:
        raise
    except (OSError, RuntimeError, ValueError) as exc:
        raise PluginControlError(f"{description} is unavailable or outside its root: {path}") from exc


def _write_bytes_exclusive(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ensure_no_symlink(path.parent, "output directory")
    try:
        with path.open("xb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise PluginControlError(f"refusing to overwrite existing file: {path}") from exc


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ensure_no_symlink(path.parent, "state directory")
    staged = path.with_name(f".{path.name}.stage-{uuid.uuid4().hex}")
    try:
        _write_bytes_exclusive(staged, content)
        os.replace(staged, path)
    except Exception:
        try:
            staged.unlink(missing_ok=True)
        except OSError:
            pass
        raise


class PluginController:
    """Bounded local lifecycle controller; it never registers or downloads plugins."""

    def __init__(
        self,
        store_root: Path,
        *,
        workspace_root: Path | None = None,
        trusted_registry: TrustedRegistry | Path | None = None,
        host_capabilities: Iterable[str] = (),
    ):
        raw_store_root = Path(store_root)
        if not raw_store_root.is_absolute():
            raise PluginControlError("store_root must be an explicit absolute path")
        _ensure_no_symlink(raw_store_root, "store_root")
        self.store_root = raw_store_root.resolve(strict=False)
        if self.store_root == Path("/") or ".github" in self.store_root.parts:
            raise PluginControlError("store_root is not an allowed private store location")

        raw_workspace = Path(workspace_root or Path.cwd())
        try:
            self.workspace_root = raw_workspace.resolve(strict=True)
        except OSError as exc:
            raise PluginControlError(f"workspace root is unavailable: {raw_workspace}") from exc
        if not self.workspace_root.is_dir():
            raise PluginControlError(f"workspace root is not a directory: {self.workspace_root}")
        if self.store_root == self.workspace_root:
            raise PluginControlError("store_root and workspace_root must be distinct")

        if isinstance(trusted_registry, TrustedRegistry):
            self.trusted_registry = trusted_registry
        elif trusted_registry is not None:
            self.trusted_registry = TrustedRegistry.from_file(Path(trusted_registry))
        else:
            registry_path = self.store_root / "trusted-registry.json"
            self.trusted_registry = (
                TrustedRegistry.from_file(registry_path)
                if registry_path.is_file()
                else TrustedRegistry()
            )

        supplied_host_capabilities = tuple(host_capabilities)
        if any(
            not isinstance(capability, str) or not capability
            for capability in supplied_host_capabilities
        ):
            raise PluginControlError("host_capabilities must be non-empty strings")
        self.host_capabilities = tuple(sorted(set(supplied_host_capabilities)))

        self.repository_root = Path(__file__).resolve().parents[3]
        self.core_root = self.repository_root / "agentic-core"
        self.core_agent_ids = frozenset(load_core_agents(_CORE_PACKAGE_ROOT / "agents"))

    @property
    def workspace_state_dir(self) -> Path:
        state_dir = self.workspace_root / ".agentic"
        _ensure_no_symlink(state_dir, "workspace state directory")
        try:
            state_dir.resolve(strict=False).relative_to(self.workspace_root)
        except ValueError as exc:
            raise PluginControlError("workspace state path escapes the workspace") from exc
        return state_dir

    def _ensure_store_root(self) -> None:
        _ensure_no_symlink(self.store_root, "store_root")
        try:
            self.store_root.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise PluginControlError(f"could not create private store root: {exc}") from exc
        if not self.store_root.is_dir():
            raise PluginControlError("store_root is not a directory")

    def _store_path(self, *parts: str) -> Path:
        path = self.store_root
        for part in parts:
            safe = _safe_relative_path(part)
            if len(safe.parts) != 1:
                raise PluginControlError(f"store path component is not a single name: {part!r}")
            path = path / safe
            if path.is_symlink():
                raise PluginControlError(f"private store path contains a symlink: {path}")
        try:
            path.resolve(strict=False).relative_to(self.store_root)
        except ValueError as exc:
            raise PluginControlError("private store path escapes store_root") from exc
        return path

    def _trusted_source_for(self, source: PackSource) -> TrustedSource:
        entry = self.trusted_registry.get(source.ir.reference)
        if entry is None:
            raise PluginControlError(
                f"pack is not in the trusted local registry: "
                f"{source.ir.id}@{source.ir.version}"
            )
        try:
            expected_root = entry.source_root.resolve(strict=True)
        except OSError as exc:
            raise PluginControlError(
                f"trusted source is unavailable: {entry.source_root}"
            ) from exc
        if expected_root != source.root:
            raise PluginControlError("pack source path does not match the trusted registry entry")
        if entry.digest != source.ir.content_digest:
            raise PluginControlError("pack content digest does not match the trusted registry")
        if entry.publisher != source.ir.trust.publisher:
            raise PluginControlError("pack publisher does not match the trusted registry")
        if entry.source != source.ir.trust.source:
            raise PluginControlError("pack source identity does not match the trusted registry")
        return entry

    def check(self, source_root: Path) -> dict[str, Any]:
        raw_root = Path(source_root)
        if raw_root.is_symlink():
            raise PluginControlError("trusted source root must not be a symlink")
        source = parse_pack(raw_root, known_agents=self.core_agent_ids)
        ensure_supported_agent_plugins(source)
        compile_target(source, "copilot")
        entry = self.trusted_registry.get(source.ir.reference)
        trusted = False
        if entry is not None:
            self._trusted_source_for(source)
            trusted = True
            installed = self._load_installed_sources()
            self._validate_dependency_closure(source, installed)
        return {
            "status": "valid",
            "state": "AVAILABLE" if trusted else "UNTRUSTED",
            "pack": source.ir.id,
            "version": source.ir.version,
            "digest": source.ir.content_digest,
            "trusted": trusted,
            "targets": list(source.ir.compatibility.targets),
        }

    def install(
        self,
        pack_id: str,
        version: str,
        *,
        approved: bool,
        expected_digest: str | None = None,
    ) -> dict[str, Any]:
        if approved is not True:
            raise PluginControlError("install requires explicit user approval")
        reference = PackReference(pack_id, version)
        entry = self.trusted_registry.get(reference)
        if entry is None:
            raise PluginControlError(
                f"pack is not in the trusted local registry: {pack_id}@{version}"
            )
        if expected_digest is not None:
            requested_digest = expected_digest.removeprefix("sha256:")
            if not _digest_is_valid(requested_digest) or requested_digest != entry.digest:
                raise PluginControlError("requested digest does not match trusted registry pin")

        raw_source = entry.source_root
        if raw_source.is_symlink():
            raise PluginControlError("trusted source root must not be a symlink")
        source = parse_pack(raw_source, known_agents=self.core_agent_ids)
        self._trusted_source_for(source)
        ensure_supported_agent_plugins(source)
        if "copilot" not in source.ir.compatibility.targets:
            raise PluginControlError("pack is not compatible with the Copilot managed target")
        compile_target(source, "copilot")

        installed = self._load_installed_sources()
        existing = installed.get(reference)
        if existing is not None:
            if existing.ir.content_digest != source.ir.content_digest:
                raise PluginControlError("installed version has a different content digest")
            return {
                "status": "installed",
                "state": "INSTALLED",
                "pack": reference.id,
                "version": reference.version,
                "digest": existing.ir.content_digest,
                "already_installed": True,
            }
        self._validate_dependency_closure(source, installed)

        self._ensure_store_root()
        parent = self._store_path("packs", reference.id)
        parent.mkdir(parents=True, exist_ok=True)
        _ensure_no_symlink(parent, "pack store directory")
        final = parent / reference.version
        if final.exists() or final.is_symlink():
            raise PluginControlError(
                f"installed version path already exists: {reference.id}@{reference.version}"
            )

        stage_root = self._store_path(".staging", f"install-{uuid.uuid4().hex}")
        stage_source = stage_root / "source"
        try:
            stage_root.mkdir(parents=True, exist_ok=False)
            self._write_source_snapshot(stage_source, source)
            staged_source = parse_pack(stage_source, known_agents=self.core_agent_ids)
            if staged_source.ir.content_digest != source.ir.content_digest:
                raise PluginControlError("staged pack digest differs from trusted source")
            self._validate_dependency_closure(staged_source, installed)
            record = {
                "schema_version": 1,
                "id": reference.id,
                "version": reference.version,
                "digest": source.ir.content_digest,
                "publisher": source.ir.trust.publisher,
                "source": source.ir.trust.source,
                "trusted_source_path": str(entry.source_root.resolve(strict=False)),
                "approved": True,
            }
            _write_bytes_exclusive(stage_root / "install.json", _json_bytes(record))
            self._make_read_only(
                [
                    *(stage_source / _safe_relative_path(relative) for relative in source.source_snapshot),
                    stage_root / "install.json",
                ]
            )
            try:
                stage_root.rename(final)
            except FileExistsError as exc:
                raise PluginControlError(
                    f"installed version path already exists: {reference.id}@{reference.version}"
                ) from exc
        except Exception:
            shutil.rmtree(stage_root, ignore_errors=True)
            raise
        return {
            "status": "installed",
            "state": "INSTALLED",
            "pack": reference.id,
            "version": reference.version,
            "digest": source.ir.content_digest,
            "already_installed": False,
        }

    def resolve(self) -> ManagedEffectiveIR:
        active_set = self._read_active_set()
        managed, _, _ = self._compose(active_set)
        return managed

    def activate(
        self,
        pack_id: str,
        version: str,
        *,
        capabilities: Iterable[str],
    ) -> dict[str, Any]:
        reference = PackReference(pack_id, version)
        installed = self._load_installed_sources()
        source = installed.get(reference)
        if source is None:
            raise PluginControlError(f"pack is not installed: {pack_id}@{version}")
        record = self._load_install_record(reference)
        if record.get("approved") is not True:
            raise PluginControlError("pack has no explicit install approval")

        previous = self._read_active_set()
        packs = dict(previous.packs)
        packs[reference] = source.ir.content_digest
        requested = set(previous.capabilities)
        grants = self._validate_capabilities(capabilities)
        if not grants:
            raise PluginControlError("activate requires explicit capability grants")
        requested.update(grants)
        candidate = ActiveSet(
            packs=tuple(sorted(packs.items())),
            capabilities=tuple(sorted(requested)),
        )
        return self._activate_candidate(candidate, action="activate")

    def deactivate(self, pack_id: str, version: str) -> dict[str, Any]:
        reference = PackReference(pack_id, version)
        installed = self._load_installed_sources()
        if reference not in installed:
            raise PluginControlError(f"pack is not installed: {pack_id}@{version}")
        previous = self._read_active_set()
        packs = dict(previous.packs)
        if reference not in packs:
            return self._status_result("deactivate", previous)
        missing = sorted(set(packs) - set(installed))
        if missing:
            rendered = ", ".join(
                f"{item.id}@{item.version}" for item in missing
            )
            raise PluginControlError(
                f"Active Set contains packs that are not installed: {rendered}"
            )
        del packs[reference]

        remaining_sources = [installed[item] for item in packs]
        available_capabilities = {
            capability.id
            for source in remaining_sources
            for capability in source.ir.capabilities
        } | set(self.host_capabilities)
        capabilities = tuple(
            sorted(set(previous.capabilities) & available_capabilities)
        )
        candidate = ActiveSet(
            packs=tuple(sorted(packs.items())),
            capabilities=capabilities,
        )
        return self._activate_candidate(candidate, action="deactivate")

    def materialize(self) -> dict[str, Any]:
        active_set = self._read_active_set()
        managed, artifact, profile_hash = self._compose(active_set)
        if artifact is None:
            lock = self._make_profile_lock(active_set, managed, None, None, "CORE_ONLY")
            self._commit_workspace_state(active_set, lock, save_history=False)
            return {
                "status": "materialized",
                "state": "CORE_ONLY",
                "runtime_visible": False,
                "effective_ir": managed.as_dict(),
            }
        profile_path = self._store_path("profiles", profile_hash)
        self._materialize_artifact(artifact, profile_path)
        lock = self._make_profile_lock(
            active_set,
            managed,
            artifact,
            profile_path,
            "MATERIALIZED_PENDING_ACTIVATION",
        )
        self._commit_workspace_state(active_set, lock, save_history=True)
        profile = EffectiveProfile(
            profile_hash=profile_hash,
            artifact_digest=artifact.digest,
            target="copilot",
            store_path=profile_path,
            effective_ir=managed,
            runtime_state="MATERIALIZED_PENDING_ACTIVATION",
        )
        return {
            "status": "materialized",
            "state": "MATERIALIZED_PENDING_ACTIVATION",
            "runtime_visible": False,
            **profile.as_dict(),
            "profile_path": str(profile_path),
        }

    def inspect(self) -> dict[str, Any]:
        installed = self._load_installed_sources()
        active_set = self._read_active_set()
        lock = self._read_profile_lock()
        active_refs = {reference for reference, _ in active_set.packs}
        return {
            "store_root": str(self.store_root),
            "workspace_root": str(self.workspace_root),
            "available": [
                {
                    "id": reference.id,
                    "version": reference.version,
                    "digest": entry.digest,
                    "state": "AVAILABLE",
                }
                for reference, entry in sorted(self.trusted_registry.entries.items())
            ],
            "installed": [
                {
                    "id": reference.id,
                    "version": reference.version,
                    "digest": source.ir.content_digest,
                    "state": "INSTALLED",
                    "desired_active": reference in active_refs,
                }
                for reference, source in sorted(installed.items())
            ],
            "active_set": active_set.as_dict(),
            "active_set_state": "ACTIVE" if active_refs else "CORE_ONLY",
            "runtime_state": (
                lock.get("runtime_state")
                if lock is not None
                else ("ACTIVE_PENDING_MATERIALIZATION" if active_refs else "CORE_ONLY")
            ),
            "materialized": bool(lock and lock.get("profile_hash")),
            "profile_hash": lock.get("profile_hash") if lock else None,
            "profile_path": lock.get("profile_path") if lock else None,
            "runtime_visible": False,
        }

    def rollback(self) -> dict[str, Any]:
        history_dir = self._workspace_store_path("history")
        index_path = history_dir / "index.json"
        if not index_path.is_file() or index_path.is_symlink():
            raise PluginControlError("no pluginctl rollback state is available")
        index = self._read_json_file(index_path, history_dir)
        if not isinstance(index, dict) or set(index) != {"entries"}:
            raise PluginControlError("rollback history index is invalid")
        entries = index.get("entries")
        if not isinstance(entries, list) or not entries:
            raise PluginControlError("no pluginctl rollback state is available")
        snapshot_id = entries[-1]
        if not isinstance(snapshot_id, str) or not _digest_is_valid(snapshot_id):
            raise PluginControlError("rollback history entry is invalid")
        snapshot_path = history_dir / f"{snapshot_id}.json"
        snapshot = self._read_json_file(snapshot_path, history_dir)
        if not isinstance(snapshot, dict) or set(snapshot) != {
            "profile_yaml",
            "profile_lock",
        }:
            raise PluginControlError("rollback snapshot is invalid")
        previous_yaml = self._decode_optional_snapshot(snapshot["profile_yaml"])
        previous_set = self._parse_active_set_bytes(previous_yaml) if previous_yaml else ActiveSet()
        managed, artifact, profile_hash = self._compose(previous_set)
        if artifact is None:
            lock = self._make_profile_lock(previous_set, managed, None, None, "CORE_ONLY")
        else:
            profile_path = self._store_path("profiles", profile_hash)
            self._materialize_artifact(artifact, profile_path)
            lock = self._make_profile_lock(
                previous_set,
                managed,
                artifact,
                profile_path,
                "MATERIALIZED_PENDING_ACTIVATION",
            )
        self._commit_workspace_state(previous_set, lock, save_history=False)
        _atomic_write(index_path, _json_bytes({"entries": entries[:-1]}))
        return {
            "status": "rolled_back",
            "state": lock["runtime_state"],
            "runtime_visible": False,
            "profile_hash": lock["profile_hash"],
            "effective_ir": managed.as_dict(),
        }

    def _activate_candidate(self, candidate: ActiveSet, *, action: str) -> dict[str, Any]:
        managed, artifact, profile_hash = self._compose(candidate)
        if artifact is None:
            lock = self._make_profile_lock(candidate, managed, None, None, "CORE_ONLY")
        else:
            profile_path = self._store_path("profiles", profile_hash)
            self._materialize_artifact(artifact, profile_path)
            lock = self._make_profile_lock(
                candidate,
                managed,
                artifact,
                profile_path,
                "MATERIALIZED_PENDING_ACTIVATION",
            )
        self._commit_workspace_state(candidate, lock, save_history=True)
        profile = (
            EffectiveProfile(
                profile_hash=profile_hash,
                artifact_digest=artifact.digest,
                target="copilot",
                store_path=profile_path,
                effective_ir=managed,
                runtime_state="MATERIALIZED_PENDING_ACTIVATION",
            )
            if artifact is not None and profile_hash is not None and profile_path is not None
            else None
        )
        return {
            "status": action,
            "desired_state": "ACTIVE" if candidate.packs else "CORE_ONLY",
            "state": lock["runtime_state"],
            "runtime_visible": False,
            **(profile.as_dict() if profile is not None else {
                "profile_hash": None,
                "effective_ir": managed.as_dict(),
            }),
            "profile_path": (
                str(profile.store_path) if profile is not None else None
            ),
        }

    def _compose(
        self,
        active_set: ActiveSet,
    ) -> tuple[ManagedEffectiveIR, CompiledTarget | None, str | None]:
        installed = self._load_installed_sources()
        installed_refs = tuple(sorted(installed))
        active_refs = tuple(reference for reference, _ in active_set.packs)
        record_digests = {
            reference: self._load_install_record(reference)["digest"]
            for reference in installed_refs
        }
        for reference, digest in active_set.packs:
            if reference not in installed:
                raise PluginControlError(f"active pack is not installed: {reference.id}@{reference.version}")
            if installed[reference].ir.content_digest != digest:
                raise PluginControlError(
                    f"active pack digest changed: {reference.id}@{reference.version}"
                )

        registry = LocalPackRegistry(
            installed.values(),
            known_agents=self.core_agent_ids,
        )
        try:
            effective_packs = resolve_effective_ir(
                registry,
                active_set.capabilities,
                installed_pack_refs=installed_refs,
                active_pack_refs=active_refs,
                approved_pack_refs=tuple(
                    reference
                    for reference, record_digest in record_digests.items()
                    if record_digest == installed[reference].ir.content_digest
                ),
                host_capabilities=self.host_capabilities,
            )
        except ExpertiseError as exc:
            raise PluginControlError(f"could not resolve Active Set: {exc}") from exc

        core_reference, core_digest, core_files, core_skill_ids = self._load_core()
        permission_projections = tuple(
            sorted(
                (
                    projection.agent_id,
                    reference,
                    server.id,
                    server.permissions,
                )
                for projection in effective_packs.agent_projections
                for reference in projection.packs
                for server in installed[reference].ir.mcp_servers
                if server.id in projection.mcp_servers
            )
        )
        managed = ManagedEffectiveIR(
            core=core_reference,
            core_digest=core_digest,
            packs=effective_packs,
            requested_capabilities=active_set.capabilities,
            target="copilot",
            permission_projections=permission_projections,
        )
        if not active_refs:
            return managed, None, None
        files = self._compose_files(
            installed,
            effective_packs,
            active_refs,
            core_files,
            core_skill_ids,
        )
        composition_digest = canonical_digest(
            {
                "core_digest": core_digest,
                "packs": [
                    {
                        "id": reference.id,
                        "version": reference.version,
                        "digest": installed[reference].ir.content_digest,
                    }
                    for reference in active_refs
                ],
                "host_capabilities": list(self.host_capabilities),
                "effective_ir": managed.as_dict(),
            }
        )
        artifact = CompiledTarget.create(
            "copilot",
            core_reference,
            files,
            source_digest=composition_digest,
        )
        profile_hash = canonical_digest(
            {
                "effective_ir": managed.as_dict(),
                "artifact_digest": artifact.digest,
            }
        )
        return managed, artifact, profile_hash

    def _compose_files(
        self,
        installed: Mapping[PackReference, PackSource],
        effective: EffectiveIR,
        active_refs: tuple[PackReference, ...],
        core_files: Mapping[str, bytes],
        core_skill_ids: frozenset[str],
    ) -> dict[str, bytes]:
        files = dict(core_files)
        allowed_skills: dict[PackReference, set[str]] = {
            reference: set() for reference in active_refs
        }
        allowed_servers: dict[PackReference, set[str]] = {
            reference: set() for reference in active_refs
        }
        for reference in active_refs:
            for projection in installed[reference].ir.projections:
                allowed_skills[reference].update(projection.skills)
                allowed_servers[reference].update(projection.mcp_servers)

        all_skill_ids = set(core_skill_ids)
        mcp_servers: dict[str, dict[str, Any]] = {}
        raw_core_mcp = files.pop("mcp.json", None)
        if raw_core_mcp is not None:
            core_mcp = load_json_no_duplicate_keys(raw_core_mcp)
            mcp_servers.update(core_mcp.get("mcpServers", {}))

        for reference in active_refs:
            source = installed[reference]
            pack_skill_ids = {item.id for item in source.ir.skills}
            collisions = all_skill_ids & pack_skill_ids
            if collisions:
                raise PluginControlError(
                    "duplicate visible skill IDs: " + ", ".join(sorted(collisions))
                )
            all_skill_ids.update(pack_skill_ids)

            artifact = compile_target(source, "copilot")
            integration_manifest_path = (
                "com.doodooms.agentic-workflow/integration.yaml"
                if source.manifest_path == "pack.yaml"
                else source.manifest_path
            )
            for relative, content in artifact.files.items():
                if relative in {
                    "plugin.json",
                    "mcp.json",
                    integration_manifest_path,
                }:
                    continue
                if relative.startswith("skills/"):
                    parts = relative.split("/", 2)
                    if len(parts) < 3 or parts[1] not in allowed_skills[reference]:
                        continue
                _add_profile_file(files, relative, content)

            raw_pack_mcp = artifact.files.get("mcp.json")
            if raw_pack_mcp is not None:
                pack_mcp = load_json_no_duplicate_keys(raw_pack_mcp)
                declared_ids = {server.id for server in source.ir.mcp_servers}
                allowed_ids = allowed_servers[reference]
                if not allowed_ids <= declared_ids:
                    raise PluginControlError("MCP projection references an undeclared server")
                for server_id in sorted(allowed_ids):
                    if server_id not in pack_mcp.get("mcpServers", {}):
                        raise PluginControlError(
                            f"projected MCP server is missing from package: {server_id}"
                        )
                    if server_id in mcp_servers:
                        raise PluginControlError(f"duplicate MCP server ID: {server_id}")
                    mcp_servers[server_id] = pack_mcp["mcpServers"][server_id]

        if mcp_servers:
            merged_mcp = {
                "$schema": MCP_SCHEMA,
                "mcpServers": dict(sorted(mcp_servers.items())),
            }
            validate_mcp_manifest(merged_mcp)
            files["mcp.json"] = _json_bytes(merged_mcp)
        validate_plugin_manifest(load_json_no_duplicate_keys(files["plugin.json"]))
        return files

    def _validate_dependency_closure(
        self,
        candidate: PackSource,
        installed: Mapping[PackReference, PackSource],
    ) -> None:
        available = dict(installed)
        available[candidate.reference] = candidate
        selected: dict[PackReference, PackSource] = {candidate.reference: candidate}
        pending = [candidate]
        while pending:
            current = pending.pop()
            for dependency in current.ir.dependencies:
                possible = [
                    (reference, source)
                    for reference, source in available.items()
                    if any(item.id == dependency.capability for item in source.ir.capabilities)
                    and (dependency.pack_id is None or reference.id == dependency.pack_id)
                    and (
                        dependency.minimum_version is None
                        or _version_key(reference.version)
                        >= _version_key(dependency.minimum_version)
                    )
                ]
                host_satisfies = (
                    dependency.capability in self.host_capabilities
                    and dependency.pack_id is None
                    and dependency.minimum_version is None
                )
                if host_satisfies and not possible:
                    continue
                if not possible:
                    raise PluginControlError(
                        f"dependency {dependency.capability!r} is not installed or host-provided"
                    )
                if len(possible) > 1:
                    raise PluginControlError(
                        f"dependency {dependency.capability!r} has ambiguous providers"
                    )
                reference, provider = possible[0]
                if reference not in selected:
                    selected[reference] = provider
                    pending.append(provider)

        refs = tuple(sorted(selected))
        registry = LocalPackRegistry(
            selected.values(),
            known_agents=self.core_agent_ids,
        )
        try:
            resolve_effective_ir(
                registry,
                [item.id for item in candidate.ir.capabilities],
                installed_pack_refs=refs,
                active_pack_refs=refs,
                approved_pack_refs=refs,
                host_capabilities=self.host_capabilities,
            )
        except ExpertiseError as exc:
            raise PluginControlError(f"pack dependency resolution failed: {exc}") from exc

    def _load_installed_sources(self) -> dict[PackReference, PackSource]:
        packs_root = self.store_root / "packs"
        if packs_root.is_symlink():
            raise PluginControlError("installed pack directory must not be a symlink")
        if not packs_root.exists():
            return {}
        _ensure_no_symlink(packs_root, "installed pack directory")
        if not packs_root.is_dir():
            raise PluginControlError("installed pack path is not a directory")
        installed: dict[PackReference, PackSource] = {}
        for id_dir in sorted(packs_root.iterdir(), key=lambda path: path.name):
            _ensure_no_symlink(id_dir, "installed pack entry")
            if not id_dir.is_dir():
                raise PluginControlError(f"unexpected file in installed pack store: {id_dir.name}")
            if not PACK_ID_PATTERN.fullmatch(id_dir.name) or len(id_dir.name) > 64:
                raise PluginControlError(f"invalid installed pack ID directory: {id_dir.name}")
            for version_dir in sorted(id_dir.iterdir(), key=lambda path: path.name):
                _ensure_no_symlink(version_dir, "installed version entry")
                if not version_dir.is_dir() or VERSION_PATTERN.fullmatch(version_dir.name) is None:
                    raise PluginControlError(f"invalid installed pack version path: {version_dir}")
                record_path = version_dir / "install.json"
                record = self._read_json_file(record_path, version_dir)
                if not isinstance(record, dict) or set(record) != _INSTALL_RECORD_FIELDS:
                    raise PluginControlError(f"install record is invalid: {record_path}")
                string_fields = (
                    "id",
                    "version",
                    "digest",
                    "publisher",
                    "source",
                    "trusted_source_path",
                )
                if any(not isinstance(record.get(field), str) for field in string_fields):
                    raise PluginControlError(f"install record fields are invalid: {record_path}")
                reference = PackReference(record.get("id"), record.get("version"))
                if (
                    reference.id != id_dir.name
                    or reference.version != version_dir.name
                    or type(record.get("schema_version")) is not int
                    or record.get("schema_version") != 1
                    or type(record.get("approved")) is not bool
                    or record.get("approved") is not True
                    or not _digest_is_valid(record.get("digest"))
                ):
                    raise PluginControlError(f"install record is inconsistent: {record_path}")
                source_root = version_dir / "source"
                if source_root.is_symlink() or not source_root.is_dir():
                    raise PluginControlError(f"installed source is unavailable: {source_root}")
                source = parse_pack(source_root, known_agents=self.core_agent_ids)
                if source.ir.reference != reference or source.ir.content_digest != record["digest"]:
                    raise PluginControlError(f"installed source digest mismatch: {reference.id}@{reference.version}")
                ensure_supported_agent_plugins(source)
                if "copilot" not in source.ir.compatibility.targets:
                    raise PluginControlError(
                        f"installed pack is not compatible with Copilot: {reference.id}@{reference.version}"
                    )
                entry = self.trusted_registry.get(reference)
                if entry is None:
                    raise PluginControlError(
                        f"installed pack is no longer in the trusted registry: {reference.id}@{reference.version}"
                    )
                if (
                    entry.digest != record["digest"]
                    or entry.publisher != record["publisher"]
                    or entry.source != record["source"]
                    or str(entry.source_root.resolve(strict=False)) != record["trusted_source_path"]
                    or source.ir.trust.publisher != record["publisher"]
                    or source.ir.trust.source != record["source"]
                ):
                    raise PluginControlError(
                        f"installed trust record does not match registry: {reference.id}@{reference.version}"
                    )
                installed[reference] = source
        return installed

    def _load_install_record(self, reference: PackReference) -> dict[str, Any]:
        path = self._store_path("packs", reference.id, reference.version, "install.json")
        record = self._read_json_file(path, self.store_root)
        if not isinstance(record, dict):
            raise PluginControlError(f"install record is invalid: {path}")
        return record

    def _read_active_set(self) -> ActiveSet:
        path = self.workspace_state_dir / "profile.yaml"
        if path.is_symlink():
            raise PluginControlError("workspace profile.yaml must not be a symlink")
        if not path.exists():
            return ActiveSet()
        if not path.is_file():
            raise PluginControlError("workspace profile.yaml must be a regular file")
        try:
            document = load_pack_yaml_bytes(path.read_bytes())
        except ExpertiseError as exc:
            raise PluginControlError(f"workspace Active Set is invalid: {exc}") from exc
        return self._parse_active_set(document)

    def _parse_active_set(self, document: Any) -> ActiveSet:
        if not isinstance(document, dict) or set(document) != _PROFILE_FIELDS:
            raise PluginControlError("profile.yaml must contain schema_version, active_packs, capabilities")
        if type(document.get("schema_version")) is not int or document["schema_version"] != 1:
            raise PluginControlError("profile.yaml schema_version must be integer 1")
        raw_packs = document.get("active_packs")
        if not isinstance(raw_packs, list):
            raise PluginControlError("profile.yaml active_packs must be an array")
        packs: list[tuple[PackReference, str]] = []
        seen: set[PackReference] = set()
        seen_ids: set[str] = set()
        for index, item in enumerate(raw_packs):
            if not isinstance(item, dict) or set(item) != {"id", "version", "digest"}:
                raise PluginControlError(f"profile.yaml active_packs[{index}] is invalid")
            if not all(isinstance(item[key], str) for key in ("id", "version", "digest")):
                raise PluginControlError(f"profile.yaml active_packs[{index}] fields must be strings")
            reference = PackReference(item["id"], item["version"])
            if (
                not PACK_ID_PATTERN.fullmatch(reference.id)
                or len(reference.id) > 64
                or VERSION_PATTERN.fullmatch(reference.version) is None
                or not _digest_is_valid(item["digest"])
            ):
                raise PluginControlError(f"profile.yaml active_packs[{index}] has invalid identity/digest")
            if reference in seen or reference.id in seen_ids:
                raise PluginControlError(f"profile.yaml has duplicate active pack {reference.id!r}")
            seen.add(reference)
            seen_ids.add(reference.id)
            packs.append((reference, item["digest"]))
        raw_capabilities = document.get("capabilities")
        if not isinstance(raw_capabilities, list) or any(
            not isinstance(item, str) or not CAPABILITY_ID_PATTERN.fullmatch(item)
            for item in raw_capabilities
        ):
            raise PluginControlError("profile.yaml capabilities must be valid capability IDs")
        if len(raw_capabilities) != len(set(raw_capabilities)):
            raise PluginControlError("profile.yaml capabilities must be unique")
        return ActiveSet(
            packs=tuple(sorted(packs)),
            capabilities=tuple(sorted(raw_capabilities)),
        )

    def _read_profile_lock(self) -> dict[str, Any] | None:
        path = self.workspace_state_dir / "profile.lock"
        if path.is_symlink():
            raise PluginControlError("workspace profile.lock must not be a symlink")
        if not path.exists():
            return None
        value = self._read_json_file(path, self.workspace_root)
        if not isinstance(value, dict):
            raise PluginControlError("workspace profile.lock must be a JSON object")
        return value

    def _read_json_file(self, path: Path, root: Path) -> Any:
        try:
            return load_json_no_duplicate_keys(_read_regular_file(path, root, "JSON state"))
        except ExpertiseError as exc:
            raise PluginControlError(f"invalid JSON state at {path}: {exc}") from exc
        except Exception as exc:
            raise PluginControlError(f"invalid JSON state at {path}: {exc}") from exc

    def _validate_capabilities(self, values: Iterable[str]) -> tuple[str, ...]:
        items = tuple(values)
        if any(
            not isinstance(value, str) or not CAPABILITY_ID_PATTERN.fullmatch(value)
            for value in items
        ):
            raise PluginControlError("capabilities must contain valid capability IDs")
        return tuple(sorted(set(items)))

    def _parse_local_source(self, source_root: Path) -> PackSource:
        raw = Path(source_root)
        if not raw.is_absolute():
            raw = Path.cwd() / raw
        if raw.is_symlink():
            raise PluginControlError("pack source root must not be a symlink")
        try:
            return parse_pack(raw, known_agents=self.core_agent_ids)
        except ExpertiseError as exc:
            raise PluginControlError(f"pack source check failed: {exc}") from exc

    def _verify_source_pin(
        self,
        source: PackSource,
        entry: TrustedSource,
    ) -> None:
        try:
            expected_root = entry.source_root.resolve(strict=True)
        except OSError as exc:
            raise PluginControlError(f"trusted source is unavailable: {entry.source_root}") from exc
        if source.root != expected_root:
            raise PluginControlError("source path does not match the trusted registry entry")
        if source.ir.content_digest != entry.digest:
            raise PluginControlError("source digest does not match the trusted registry entry")
        if source.ir.trust.publisher != entry.publisher or source.ir.trust.source != entry.source:
            raise PluginControlError("source trust metadata does not match the trusted registry entry")

    def _load_core(
        self,
    ) -> tuple[PackReference, str, Mapping[str, bytes], frozenset[str]]:
        plugin_path = self.core_root / "plugin.json"
        raw_plugin = _read_regular_file(plugin_path, self.core_root, "agentic-core plugin.json")
        try:
            plugin = load_json_no_duplicate_keys(raw_plugin)
            validate_plugin_manifest(plugin)
        except Exception as exc:
            raise PluginControlError("agentic-core plugin.json is invalid") from exc
        if not isinstance(plugin, dict) or not isinstance(plugin.get("name"), str) or not isinstance(plugin.get("version"), str):
            raise PluginControlError("agentic-core plugin identity is invalid")
        core_reference = PackReference(plugin["name"], plugin["version"])
        try:
            parse_version(core_reference.version)
        except ValueError as exc:
            raise PluginControlError("agentic-core version is invalid") from exc

        files: dict[str, bytes] = {"plugin.json": raw_plugin}
        skill_ids: set[str] = set()
        skills_root = self.core_root / "skills"
        _ensure_no_symlink(skills_root, "agentic-core skills directory")
        if not skills_root.is_dir():
            raise PluginControlError("agentic-core skills directory is unavailable")
        for skill_root in sorted(skills_root.iterdir(), key=lambda path: path.name):
            _ensure_no_symlink(skill_root, "agentic-core skill")
            if not skill_root.is_dir():
                continue
            if not (skill_root / "SKILL.md").is_file():
                continue
            skill_ids.add(skill_root.name)
            for path in sorted(skill_root.rglob("*"), key=lambda item: item.as_posix()):
                if path.is_symlink():
                    raise PluginControlError(f"agentic-core skill contains a symlink: {path}")
                if (
                    not path.is_file()
                    or _is_generated_cache(path)
                    or path.name == ".workflow-routes.tmp"
                ):
                    continue
                relative = f"skills/{skill_root.name}/{path.relative_to(skill_root).as_posix()}"
                files[relative] = _read_regular_file(
                    path, self.core_root, "agentic-core skill source"
                )

        agent_dir = self.core_root / "com.github.copilot" / "agents"
        _ensure_no_symlink(agent_dir, "agentic-core agent directory")
        if not agent_dir.is_dir():
            raise PluginControlError("agentic-core Copilot agent directory is unavailable")
        agent_ids: set[str] = set()
        for path in sorted(agent_dir.glob("*.agent.md"), key=lambda item: item.name):
            if path.is_symlink():
                raise PluginControlError(f"agentic-core agent is a symlink: {path}")
            content = _read_regular_file(path, self.core_root, "agentic-core agent")
            _validate_agent(content, path, self.core_agent_ids)
            agent_ids.add(path.name.removesuffix(".agent.md"))
            files[f"com.github.copilot/agents/{path.name}"] = content
        if agent_ids != set(self.core_agent_ids):
            raise PluginControlError("agentic-core agent catalog changed during composition")

        mcp_path = self.core_root / "mcp.json"
        if mcp_path.exists() or mcp_path.is_symlink():
            if mcp_path.is_symlink():
                raise PluginControlError("agentic-core mcp.json must not be a symlink")
            raw_mcp = _read_regular_file(mcp_path, self.core_root, "agentic-core mcp.json")
            try:
                validate_mcp_manifest(load_json_no_duplicate_keys(raw_mcp))
            except Exception as exc:
                raise PluginControlError("agentic-core mcp.json is invalid") from exc
            files["mcp.json"] = raw_mcp

        return (
            core_reference,
            source_content_digest(files),
            MappingProxyType(files),
            frozenset(skill_ids),
        )

    def _materialize_artifact(
        self,
        artifact: CompiledTarget,
        profile_path: Path,
    ) -> Path:
        self._ensure_store_root()
        files = validate_target_files(artifact.files)
        profiles_root = self._store_path("profiles")
        profiles_root.mkdir(parents=True, exist_ok=True)
        _ensure_no_symlink(profiles_root, "profile store directory")
        final = Path(profile_path)
        if (
            not final.is_absolute()
            or final.parent != profiles_root
            or not _digest_is_valid(final.name)
        ):
            raise PluginControlError("profile path must be a hash-addressed child of profiles")
        _ensure_no_symlink(final, "profile path")
        if final.exists() or final.is_symlink():
            if final.is_symlink() or not final.is_dir():
                raise PluginControlError("existing profile path is not a directory")
            self._verify_profile_files(final, files)
            return final

        stage = self._store_path(".staging", f"profile-{uuid.uuid4().hex}")
        try:
            stage.mkdir(parents=True, exist_ok=False)
            for relative, content in sorted(files.items()):
                rel = _safe_relative_path(relative)
                output = stage / rel
                output.parent.mkdir(parents=True, exist_ok=True)
                _ensure_no_symlink(output.parent, "staged profile directory")
                _write_bytes_exclusive(output, content)
            self._validate_profile_tree(stage)
            self._make_read_only(
                [stage / _safe_relative_path(relative) for relative in files]
            )
            try:
                stage.rename(final)
            except FileExistsError:
                self._verify_profile_files(final, files)
            return final
        except Exception:
            shutil.rmtree(stage, ignore_errors=True)
            raise

    def _validate_profile_tree(self, root: Path) -> None:
        manifest_path = root / "plugin.json"
        manifest = load_json_no_duplicate_keys(_read_regular_file(manifest_path, root, "profile plugin.json"))
        validate_plugin_manifest(manifest)
        mcp_path = root / "mcp.json"
        if mcp_path.exists():
            validate_mcp_manifest(load_json_no_duplicate_keys(_read_regular_file(mcp_path, root, "profile mcp.json")))
        for skill_root in sorted((root / "skills").glob("*")) if (root / "skills").exists() else ():
            _ensure_no_symlink(skill_root, "materialized skill")
            if skill_root.is_dir() and not (skill_root / "SKILL.md").is_file():
                raise PluginControlError(f"materialized skill is missing SKILL.md: {skill_root.name}")

    def _verify_profile_files(self, root: Path, expected: Mapping[str, bytes]) -> None:
        actual_paths: set[str] = set()
        for entry in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
            if entry.is_symlink():
                raise PluginControlError(f"stored profile contains a symlink: {entry}")
            if entry.is_file():
                relative = entry.relative_to(root).as_posix()
                if ".github" in Path(relative).parts:
                    raise PluginControlError("stored profile contains consumer .github content")
                actual_paths.add(relative)
            elif not entry.is_dir():
                raise PluginControlError(f"stored profile contains an unsupported entry: {entry}")
        if actual_paths != set(expected):
            raise PluginControlError("stored profile file set does not match the materialized profile")
        for relative, expected_bytes in expected.items():
            path = root / _safe_relative_path(relative)
            actual = _read_regular_file(path, root, "stored profile file")
            if actual != expected_bytes:
                raise PluginControlError(f"stored profile content mismatch: {relative}")

    def _make_profile_lock(
        self,
        active_set: ActiveSet,
        effective_ir: ManagedEffectiveIR,
        artifact: CompiledTarget | None,
        profile_path: Path | None,
        runtime_state: str,
    ) -> dict[str, Any]:
        effective_profile = (
            EffectiveProfile(
                profile_hash=canonical_digest(
                    {
                        "effective_ir": effective_ir.as_dict(),
                        "artifact_digest": artifact.digest,
                    }
                ),
                artifact_digest=artifact.digest,
                target="copilot",
                store_path=profile_path,
                effective_ir=effective_ir,
                runtime_state=runtime_state,
            ).as_dict()
            if artifact is not None and profile_path is not None
            else None
        )
        return {
            "schema_version": 1,
            "runtime_state": runtime_state,
            "runtime_visible": False,
            "target": "copilot",
            "profile_hash": effective_profile["profile_hash"] if effective_profile else None,
            "profile_path": str(profile_path) if profile_path is not None else None,
            "artifact_digest": artifact.digest if artifact is not None else None,
            "source_digest": artifact.source_digest if artifact is not None else None,
            "effective_profile": effective_profile,
            "active_set": active_set.as_dict(),
            "effective_ir": effective_ir.as_dict(),
        }

    def _commit_workspace_state(
        self,
        active_set: ActiveSet,
        lock: dict[str, Any],
        *,
        save_history: bool,
    ) -> None:
        state_dir = self.workspace_state_dir
        state_dir.mkdir(parents=True, exist_ok=True)
        _ensure_no_symlink(state_dir, "workspace state directory")
        profile_path = state_dir / "profile.yaml"
        lock_path = state_dir / "profile.lock"
        old_profile = self._read_optional_file(profile_path, self.workspace_root)
        old_lock = self._read_optional_file(lock_path, self.workspace_root)
        if save_history:
            self._push_history(old_profile, old_lock)
        new_profile = _json_bytes(active_set.as_dict())
        new_lock = _json_bytes(lock)
        try:
            _atomic_write(profile_path, new_profile)
            _atomic_write(lock_path, new_lock)
        except Exception:
            self._restore_file(profile_path, old_profile)
            self._restore_file(lock_path, old_lock)
            raise

    def _push_history(self, profile_yaml: bytes | None, profile_lock: bytes | None) -> None:
        history_dir = self._workspace_store_path("history")
        history_dir.mkdir(parents=True, exist_ok=True)
        index_path = history_dir / "index.json"
        index = self._read_json_file(index_path, history_dir) if index_path.exists() else {"entries": []}
        if not isinstance(index, dict) or set(index) != {"entries"} or not isinstance(index["entries"], list):
            raise PluginControlError("workspace history index is invalid")
        snapshot = {
            "profile_yaml": base64.b64encode(profile_yaml).decode("ascii") if profile_yaml is not None else None,
            "profile_lock": base64.b64encode(profile_lock).decode("ascii") if profile_lock is not None else None,
        }
        snapshot_id = canonical_digest(snapshot)
        snapshot_path = history_dir / f"{snapshot_id}.json"
        if not snapshot_path.exists():
            _atomic_write(snapshot_path, _json_bytes(snapshot))
        entries = list(index["entries"])
        if not entries or entries[-1] != snapshot_id:
            entries.append(snapshot_id)
            _atomic_write(index_path, _json_bytes({"entries": entries}))

    def _read_optional_file(self, path: Path, root: Path) -> bytes | None:
        if not path.exists():
            return None
        return _read_regular_file(path, root, "workspace state file")

    def _restore_file(self, path: Path, content: bytes | None) -> None:
        if content is None:
            path.unlink(missing_ok=True)
        else:
            _atomic_write(path, content)

    def _workspace_store_path(self, *parts: str) -> Path:
        workspace_id = canonical_digest({"workspace": str(self.workspace_root)})
        path = self._store_path("workspaces", workspace_id, *parts)
        return path

    def _write_source_snapshot(self, target_root: Path, source: PackSource) -> None:
        target_root.mkdir(parents=True, exist_ok=False)
        for relative, content in sorted(source.source_snapshot.items()):
            rel = _safe_relative_path(relative)
            target = target_root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            _write_bytes_exclusive(target, content)

    def _make_read_only(self, paths: Iterable[Path]) -> None:
        for path in paths:
            try:
                path.chmod(0o444)
            except OSError as exc:
                raise PluginControlError(f"could not make immutable copy read-only: {path}") from exc

    def _parse_active_set_bytes(self, content: bytes) -> ActiveSet:
        try:
            document = load_pack_yaml_bytes(content)
        except ExpertiseError as exc:
            raise PluginControlError(f"rollback Active Set is invalid: {exc}") from exc
        return self._parse_active_set(document)

    @staticmethod
    def _decode_optional_snapshot(value: Any) -> bytes | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise PluginControlError("rollback snapshot content must be base64 text")
        try:
            return base64.b64decode(value, validate=True)
        except ValueError as exc:
            raise PluginControlError("rollback snapshot contains invalid base64") from exc

    def _status_result(self, operation: str, active_set: ActiveSet) -> dict[str, Any]:
        lock = self._read_profile_lock()
        return {
            "status": operation,
            "desired_active_packs": [
                {"id": reference.id, "version": reference.version, "digest": digest}
                for reference, digest in active_set.packs
            ],
            "runtime_state": lock.get("runtime_state") if lock else "CORE_ONLY",
            "runtime_visible": False,
        }


def _add_profile_file(files: dict[str, bytes], path: str, content: bytes) -> None:
    if path in files:
        raise PluginControlError(f"duplicate effective profile path: {path}")
    files[path] = content


def _is_generated_cache(path: Path) -> bool:
    return "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}
