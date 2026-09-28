from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .ontology import canonical_digest


@dataclass(frozen=True, order=True)
class PackReference:
    id: str
    version: str


@dataclass(frozen=True)
class Compatibility:
    targets: tuple[str, ...]
    agent_plugins: str


@dataclass(frozen=True)
class TrustMetadata:
    publisher: str
    source: str
    approval_required: bool
    digest: str | None = None


@dataclass(frozen=True)
class Capability:
    id: str
    description: str


@dataclass(frozen=True)
class Dependency:
    capability: str
    pack_id: str | None = None
    minimum_version: str | None = None


@dataclass(frozen=True)
class AgentContribution:
    id: str
    source: str
    capabilities: tuple[str, ...]


@dataclass(frozen=True)
class AgentExtension:
    agent_id: str
    capabilities: tuple[str, ...]


@dataclass(frozen=True)
class AgentContributions:
    contributions: tuple[AgentContribution, ...]
    extensions: tuple[AgentExtension, ...]


@dataclass(frozen=True)
class SkillComponent:
    id: str
    path: str
    capabilities: tuple[str, ...]


@dataclass(frozen=True)
class MCPServer:
    id: str
    capabilities: tuple[str, ...]
    permissions: tuple[str, ...]
    tools: tuple[str, ...] = ()


@dataclass(frozen=True)
class AgentProjection:
    agent_id: str
    capabilities: tuple[str, ...]
    skills: tuple[str, ...]
    mcp_servers: tuple[str, ...]


@dataclass(frozen=True)
class PackIR:
    schema_version: int
    id: str
    type: str
    name: str
    version: str
    description: str
    compatibility: Compatibility
    trust: TrustMetadata
    capabilities: tuple[Capability, ...]
    dependencies: tuple[Dependency, ...]
    agents: AgentContributions
    skills: tuple[SkillComponent, ...]
    mcp_config: str | None
    mcp_servers: tuple[MCPServer, ...]
    projections: tuple[AgentProjection, ...]
    content_digest: str

    @property
    def reference(self) -> PackReference:
        return PackReference(self.id, self.version)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "compatibility": {
                "targets": list(self.compatibility.targets),
                "agent_plugins": self.compatibility.agent_plugins,
            },
            "trust": {
                "publisher": self.trust.publisher,
                "source": self.trust.source,
                "approval_required": self.trust.approval_required,
                "digest": self.trust.digest,
            },
            "capabilities": [
                {"id": item.id, "description": item.description}
                for item in self.capabilities
            ],
            "dependencies": [
                {
                    "capability": item.capability,
                    "pack_id": item.pack_id,
                    "minimum_version": item.minimum_version,
                }
                for item in self.dependencies
            ],
            "agents": {
                "contributions": [
                    {
                        "id": item.id,
                        "source": item.source,
                        "capabilities": list(item.capabilities),
                    }
                    for item in self.agents.contributions
                ],
                "extensions": [
                    {
                        "agent_id": item.agent_id,
                        "capabilities": list(item.capabilities),
                    }
                    for item in self.agents.extensions
                ],
            },
            "skills": [
                {
                    "id": item.id,
                    "path": item.path,
                    "capabilities": list(item.capabilities),
                }
                for item in self.skills
            ],
            "mcp_config": self.mcp_config,
            "mcp_servers": [
                {
                    "id": item.id,
                    "capabilities": list(item.capabilities),
                    "permissions": list(item.permissions),
                    "tools": list(item.tools),
                }
                for item in self.mcp_servers
            ],
            "projections": [
                {
                    "agent_id": item.agent_id,
                    "capabilities": list(item.capabilities),
                    "skills": list(item.skills),
                    "mcp_servers": list(item.mcp_servers),
                }
                for item in self.projections
            ],
            "content_digest": self.content_digest,
        }

    @property
    def fingerprint(self) -> str:
        return canonical_digest(self.as_dict())


@dataclass(frozen=True)
class PackSource:
    root: Path = field(compare=False)
    ir: PackIR
    source_files: tuple[str, ...] = ()
    manifest_path: str = "pack.yaml"
    source_snapshot: Mapping[str, bytes] = field(
        default_factory=lambda: MappingProxyType({}),
        compare=False,
        repr=False,
    )
    known_agents: frozenset[str] = field(default_factory=frozenset, compare=False)

    @property
    def reference(self) -> PackReference:
        return self.ir.reference


@dataclass(frozen=True)
class CapabilityProvider:
    capability: str
    pack: PackReference
    kind: str
    component_id: str


@dataclass(frozen=True)
class ResolvedAgentProjection:
    agent_id: str
    capabilities: tuple[str, ...]
    skills: tuple[str, ...]
    mcp_servers: tuple[str, ...]
    packs: tuple[PackReference, ...]


@dataclass(frozen=True)
class EffectiveIR:
    """Pure, in-memory resolution result; it is not persisted lifecycle state."""

    packs: tuple[PackReference, ...]
    capabilities: tuple[str, ...]
    providers: tuple[CapabilityProvider, ...]
    agent_projections: tuple[ResolvedAgentProjection, ...]
    provenance: tuple[tuple[str, PackReference, str], ...]
    host_capabilities: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "packs": [{"id": item.id, "version": item.version} for item in self.packs],
            "capabilities": list(self.capabilities),
            "providers": [
                {
                    "capability": item.capability,
                    "pack": {"id": item.pack.id, "version": item.pack.version},
                    "kind": item.kind,
                    "component_id": item.component_id,
                }
                for item in self.providers
            ],
            "agent_projections": [
                {
                    "agent_id": item.agent_id,
                    "capabilities": list(item.capabilities),
                    "skills": list(item.skills),
                    "mcp_servers": list(item.mcp_servers),
                    "packs": [
                        {"id": ref.id, "version": ref.version} for ref in item.packs
                    ],
                }
                for item in self.agent_projections
            ],
            "provenance": [
                {
                    "capability": capability,
                    "pack": {"id": pack.id, "version": pack.version},
                    "content_digest": digest,
                }
                for capability, pack, digest in self.provenance
            ],
            "host_capabilities": list(self.host_capabilities),
        }

    @property
    def fingerprint(self) -> str:
        return canonical_digest(self.as_dict())
