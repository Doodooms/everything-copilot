from __future__ import annotations

from collections.abc import Iterable

from .errors import ResolutionError
from .ir import (
    CapabilityProvider,
    EffectiveIR,
    PackReference,
    PackSource,
    ResolvedAgentProjection,
)
from .ontology import CAPABILITY_ID_PATTERN, VERSION_PATTERN
from .registry import LocalPackRegistry


def _version_key(value: str) -> tuple[object, ...]:
    match = VERSION_PATTERN.fullmatch(value)
    if match is None:
        raise ResolutionError(f"invalid pack version {value!r}")
    major, minor, patch = (int(match.group(index)) for index in (1, 2, 3))
    prerelease = match.group(4)
    if prerelease is None:
        return major, minor, patch, 1, ()
    identifiers: list[tuple[int, object]] = []
    for item in prerelease.split("."):
        if not item:
            raise ResolutionError(f"invalid semantic version {value!r}")
        if item.isdigit():
            if len(item) > 1 and item.startswith("0"):
                raise ResolutionError(f"invalid semantic version {value!r}")
            identifiers.append((0, int(item)))
        else:
            identifiers.append((1, item))
    return major, minor, patch, 0, tuple(identifiers)


def _reference_set(
    values: Iterable[PackReference], label: str
) -> frozenset[PackReference]:
    references = tuple(values)
    if any(not isinstance(item, PackReference) for item in references):
        raise ResolutionError(f"{label} must contain PackReference values")
    return frozenset(references)


def resolve_effective_ir(
    registry: LocalPackRegistry,
    requested_capabilities: Iterable[str],
    *,
    installed_pack_refs: Iterable[PackReference],
    active_pack_refs: Iterable[PackReference],
    approved_pack_refs: Iterable[PackReference],
    agent_ids: Iterable[str] | None = None,
    host_capabilities: Iterable[str] = (),
) -> EffectiveIR:
    """Compose an explicit Active Set without persisting or changing lifecycle state."""
    installed = _reference_set(installed_pack_refs, "installed_pack_refs")
    active = _reference_set(active_pack_refs, "active_pack_refs")
    approved = _reference_set(approved_pack_refs, "approved_pack_refs")
    registered = set(registry.references)

    unknown_installed = sorted(installed - registered)
    if unknown_installed:
        rendered = ", ".join(f"{item.id}@{item.version}" for item in unknown_installed)
        raise ResolutionError(f"installed packs are not locally registered: {rendered}")
    unknown_active = sorted(active - registered)
    if unknown_active:
        rendered = ", ".join(f"{item.id}@{item.version}" for item in unknown_active)
        raise ResolutionError(f"active packs are not locally registered: {rendered}")
    if not active <= installed:
        missing = sorted(active - installed)
        rendered = ", ".join(f"{item.id}@{item.version}" for item in missing)
        raise ResolutionError(f"active packs are not installed: {rendered}")
    if not active <= approved:
        missing = sorted(active - approved)
        rendered = ", ".join(f"{item.id}@{item.version}" for item in missing)
        raise ResolutionError(f"active packs are not approved: {rendered}")

    active_by_id: dict[str, PackReference] = {}
    for reference in sorted(active):
        prior = active_by_id.get(reference.id)
        if prior is not None and prior != reference:
            raise ResolutionError(
                f"multiple active versions for pack {reference.id!r}: "
                f"{prior.version}, {reference.version}"
            )
        active_by_id[reference.id] = reference

    requested_values = tuple(requested_capabilities)
    if any(
        not isinstance(capability, str) or not capability
        for capability in requested_values
    ):
        raise ResolutionError("requested capabilities must be non-empty strings")
    requested = set(requested_values)
    host_values = tuple(host_capabilities)
    if any(
        not isinstance(capability, str)
        or CAPABILITY_ID_PATTERN.fullmatch(capability) is None
        for capability in host_values
    ):
        raise ResolutionError("host_capabilities must contain valid capability IDs")
    available_host_capabilities = set(host_values)

    active_sources: dict[PackReference, PackSource] = {
        reference: registry.get(reference) for reference in sorted(active)
    }
    capability_providers: dict[str, PackReference] = {}
    for reference, source in active_sources.items():
        for capability in source.ir.capabilities:
            prior = capability_providers.get(capability.id)
            if prior is not None and prior != reference:
                raise ResolutionError(
                    f"ambiguous providers for capability {capability.id!r}: "
                    f"{prior.id}@{prior.version}, {reference.id}@{reference.version}"
                )
            capability_providers[capability.id] = reference

    overlapping_host_capabilities = sorted(
        set(capability_providers) & available_host_capabilities
    )
    if overlapping_host_capabilities:
        raise ResolutionError(
            "ambiguous pack and host providers for capabilities: "
            + ", ".join(overlapping_host_capabilities)
        )

    for capability in sorted(
        requested - set(capability_providers) - available_host_capabilities
    ):
        if not registry.providers_for(capability):
            raise ResolutionError(f"unknown capability {capability!r}")
        raise ResolutionError(
            f"capability {capability!r} is not provided by the explicit Active Set"
        )

    dependency_graph: dict[PackReference, set[PackReference]] = {
        reference: set() for reference in active
    }
    for reference, source in active_sources.items():
        for dependency in source.ir.dependencies:
            if (
                dependency.capability in available_host_capabilities
                and dependency.pack_id is None
                and dependency.minimum_version is None
            ):
                continue
            providers = [
                provider
                for provider in registry.providers_for(dependency.capability)
                if provider in active
                and provider in installed
                and provider in approved
                and (dependency.pack_id is None or provider.id == dependency.pack_id)
                and (
                    dependency.minimum_version is None
                    or _version_key(provider.version)
                    >= _version_key(dependency.minimum_version)
                )
            ]
            if not providers:
                raise ResolutionError(
                    f"dependency {dependency.capability!r} required by "
                    f"{reference.id}@{reference.version} is not provided by an "
                    "installed, active, approved pack"
                )
            if len(providers) > 1:
                rendered = ", ".join(
                    f"{item.id}@{item.version}" for item in sorted(providers)
                )
                raise ResolutionError(
                    f"ambiguous dependency providers for {dependency.capability!r}: {rendered}"
                )
            dependency_graph[reference].add(providers[0])

    visiting: list[PackReference] = []
    visited: set[PackReference] = set()

    def visit(reference: PackReference) -> None:
        if reference in visiting:
            cycle = visiting[visiting.index(reference) :] + [reference]
            rendered = " -> ".join(f"{item.id}@{item.version}" for item in cycle)
            raise ResolutionError(f"pack dependency cycle: {rendered}")
        if reference in visited:
            return
        visiting.append(reference)
        for dependency in sorted(dependency_graph[reference]):
            visit(dependency)
        visiting.pop()
        visited.add(reference)

    for reference in sorted(active):
        visit(reference)

    visible_agent_ids = set(registry.core_agent_ids)
    for reference, source in active_sources.items():
        contribution_ids = {item.id for item in source.ir.agents.contributions}
        duplicates = contribution_ids & visible_agent_ids
        if duplicates:
            raise ResolutionError(
                "duplicate visible agent IDs: " + ", ".join(sorted(duplicates))
            )
        visible_agent_ids.update(contribution_ids)

    if agent_ids is None:
        requested_agents = tuple(sorted(visible_agent_ids))
    else:
        supplied_agents = tuple(agent_ids)
        if any(
            not isinstance(agent_id, str) or not agent_id
            for agent_id in supplied_agents
        ):
            raise ResolutionError("agent_ids must contain non-empty strings")
        requested_agents = tuple(sorted(set(supplied_agents)))
    unknown_agents = sorted(set(requested_agents) - visible_agent_ids)
    if unknown_agents:
        raise ResolutionError(
            "unknown projected agent IDs: " + ", ".join(unknown_agents)
        )

    projections: list[ResolvedAgentProjection] = []
    for agent_id in requested_agents:
        granted_capabilities: set[str] = set()
        granted_skills: set[str] = set()
        granted_servers: set[str] = set()
        contributing_packs: set[PackReference] = set()
        for reference, source in active_sources.items():
            for projection in source.ir.projections:
                if projection.agent_id != agent_id:
                    continue
                granted_capabilities.update(projection.capabilities)
                granted_skills.update(projection.skills)
                granted_servers.update(projection.mcp_servers)
                contributing_packs.add(reference)
        projections.append(
            ResolvedAgentProjection(
                agent_id=agent_id,
                capabilities=tuple(sorted(granted_capabilities)),
                skills=tuple(sorted(granted_skills)),
                mcp_servers=tuple(sorted(granted_servers)),
                packs=tuple(sorted(contributing_packs)),
            )
        )

    providers: list[CapabilityProvider] = []
    provenance: list[tuple[str, PackReference, str]] = []
    for capability, reference in sorted(capability_providers.items()):
        source = active_sources[reference]
        provenance.append((capability, reference, source.ir.content_digest))
        for contribution in source.ir.agents.contributions:
            if capability in contribution.capabilities:
                providers.append(
                    CapabilityProvider(capability, reference, "agent", contribution.id)
                )
        for extension in source.ir.agents.extensions:
            if capability in extension.capabilities:
                providers.append(
                    CapabilityProvider(
                        capability, reference, "agent-extension", extension.agent_id
                    )
                )
        for skill in source.ir.skills:
            if capability in skill.capabilities:
                providers.append(
                    CapabilityProvider(capability, reference, "skill", skill.id)
                )
        for server in source.ir.mcp_servers:
            if capability in server.capabilities:
                providers.append(
                    CapabilityProvider(capability, reference, "mcp-server", server.id)
                )

    return EffectiveIR(
        packs=tuple(sorted(active)),
        capabilities=tuple(sorted(capability_providers)),
        providers=tuple(
            sorted(
                providers,
                key=lambda item: (
                    item.capability,
                    item.pack.id,
                    item.pack.version,
                    item.kind,
                    item.component_id,
                ),
            )
        ),
        agent_projections=tuple(projections),
        provenance=tuple(sorted(provenance)),
        host_capabilities=tuple(sorted(available_host_capabilities)),
    )
