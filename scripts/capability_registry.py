from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


CAPABILITY_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9-]*(?:\.[a-z][a-z0-9-]*)+$")
FIELD_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
PROVIDER_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")
TOOL_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_.-]*$")
POLICY_MODE_PATTERN = re.compile(r"^(explicit|priority|single)$")
CAPABILITY_REF_PATTERN = re.compile(r"(?<![\w/])capability:([a-z][a-z0-9-]*(?:\.[a-z][a-z0-9-]*)+)")


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)

    def extend(self, other: "ValidationResult") -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.data.update(other.data)


@dataclass(frozen=True)
class CapabilitySpec:
    name: str
    description: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    determinism: dict[str, str]
    constraints: tuple[str, ...]
    requires: tuple[str, ...]
    source_path: Path


@dataclass(frozen=True)
class ProviderCatalogEntry:
    name: str
    server: str
    tools: tuple[str, ...]
    description: str


@dataclass(frozen=True)
class RouteBinding:
    provider: str
    tool: str
    priority: int | None = None


@dataclass(frozen=True)
class BindingPolicy:
    mode: str = "single"


@dataclass(frozen=True)
class CapabilityBinding:
    capability_name: str
    routes: tuple[RouteBinding, ...]
    policy: BindingPolicy


@dataclass(frozen=True)
class CapabilityResolution:
    capability: CapabilitySpec
    binding: CapabilityBinding
    route: RouteBinding
    server_name: str


@dataclass(frozen=True)
class CapabilityRegistry:
    root: Path
    capabilities: dict[str, CapabilitySpec]
    bindings: dict[str, CapabilityBinding]
    providers: dict[str, ProviderCatalogEntry]
    mcp_servers: dict[str, dict[str, Any]]


def find_workspace_root(start: Path) -> Path | None:
    candidate = start.resolve(strict=False)
    if candidate.is_file():
        candidate = candidate.parent

    for path in [candidate, *candidate.parents]:
        if (path / ".github").exists() and (path / ".vscode" / "mcp.json").exists():
            return path
    return None


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


def extract_capability_refs(text: str) -> list[str]:
    refs: list[str] = []
    for line in iter_code_fence_filtered_lines(text):
        for match in CAPABILITY_REF_PATTERN.finditer(line):
            refs.append(match.group(1).strip())
    return refs


def _read_yaml_file(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _read_mcp_servers(root: Path, result: ValidationResult) -> dict[str, dict[str, Any]]:
    mcp_path = root / ".vscode" / "mcp.json"
    if not mcp_path.exists():
        result.errors.append(f"Missing MCP registry: {mcp_path}")
        return {}

    try:
        payload = json.loads(mcp_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        result.errors.append(f"MCP registry is not valid JSON: {exc}")
        return {}

    servers = payload.get("servers", {})
    if not isinstance(servers, dict):
        result.errors.append("`.vscode/mcp.json` must contain a top-level `servers` mapping.")
        return {}

    normalized: dict[str, dict[str, Any]] = {}
    for server_name, server_payload in servers.items():
        if isinstance(server_payload, dict):
            normalized[str(server_name)] = server_payload
    return normalized


def _load_provider_catalog(root: Path, result: ValidationResult) -> dict[str, ProviderCatalogEntry]:
    catalog_path = root / ".github" / "runtime" / "provider-catalog.yaml"
    if not catalog_path.exists():
        result.errors.append(f"Missing provider catalog: {catalog_path}")
        return {}

    try:
        payload = _read_yaml_file(catalog_path) or {}
    except yaml.YAMLError as exc:
        result.errors.append(f"Provider catalog is not valid YAML: {exc}")
        return {}

    providers_payload = payload.get("providers") if isinstance(payload, dict) else None
    if not isinstance(providers_payload, dict):
        result.errors.append("Provider catalog must contain a top-level `providers` mapping.")
        return {}

    providers: dict[str, ProviderCatalogEntry] = {}
    for provider_name, provider_payload in providers_payload.items():
        if not isinstance(provider_name, str) or not PROVIDER_NAME_PATTERN.fullmatch(provider_name):
            result.errors.append(f"Invalid provider name in catalog: {provider_name!r}")
            continue

        if provider_name in providers:
            result.errors.append(f"Duplicate provider catalog entry: {provider_name}")
            continue

        if not isinstance(provider_payload, dict):
            result.errors.append(f"Provider `{provider_name}` must map to a YAML object.")
            continue

        server = provider_payload.get("server")
        tools = provider_payload.get("tools")
        description = provider_payload.get("description", "")

        if not isinstance(server, str) or not server.strip():
            result.errors.append(f"Provider `{provider_name}` must declare a non-empty `server`.")
            continue

        if not isinstance(tools, list) or not tools:
            result.errors.append(f"Provider `{provider_name}` must declare a non-empty `tools` list.")
            continue

        normalized_tools: list[str] = []
        seen_tools: set[str] = set()
        for tool_name in tools:
            if not isinstance(tool_name, str) or not TOOL_NAME_PATTERN.fullmatch(tool_name):
                result.errors.append(
                    f"Provider `{provider_name}` has invalid tool name `{tool_name}` in provider catalog."
                )
                continue
            if tool_name in seen_tools:
                result.errors.append(
                    f"Provider `{provider_name}` lists duplicate tool `{tool_name}` in provider catalog."
                )
                continue
            seen_tools.add(tool_name)
            normalized_tools.append(tool_name)

        providers[provider_name] = ProviderCatalogEntry(
            name=provider_name,
            server=server,
            tools=tuple(normalized_tools),
            description=str(description),
        )

    return providers


def _load_capabilities(root: Path, result: ValidationResult) -> dict[str, CapabilitySpec]:
    capability_dir = root / ".github" / "capabilities"
    if not capability_dir.exists():
        result.errors.append(f"Missing capability directory: {capability_dir}")
        return {}

    capabilities: dict[str, CapabilitySpec] = {}
    for path in sorted(capability_dir.glob("*.yaml")):
        try:
            payload = _read_yaml_file(path) or {}
        except yaml.YAMLError as exc:
            result.errors.append(f"Capability definition is not valid YAML: {path}: {exc}")
            continue

        if not isinstance(payload, dict):
            result.errors.append(f"Capability definition must be a YAML object: {path}")
            continue

        name = payload.get("name")
        description = payload.get("description")
        inputs = payload.get("inputs", [])
        outputs = payload.get("outputs", [])
        determinism = payload.get("determinism", {})
        constraints = payload.get("constraints", [])
        requires = payload.get("requires", [])

        if not isinstance(name, str) or not CAPABILITY_NAME_PATTERN.fullmatch(name):
            result.errors.append(f"Capability file `{path.name}` has invalid `name`: {name!r}")
            continue

        if path.stem != name:
            result.errors.append(
                f"Capability file `{path.name}` must match capability name `{name}` exactly."
            )

        if name in capabilities:
            result.errors.append(f"Duplicate capability definition for `{name}`.")
            continue

        if not isinstance(description, str) or not description.strip():
            result.errors.append(f"Capability `{name}` must declare a non-empty `description`.")
            continue

        normalized_inputs = _validate_field_name_list(name, "inputs", inputs, result)
        normalized_outputs = _validate_field_name_list(name, "outputs", outputs, result)
        normalized_constraints = _validate_string_list(name, "constraints", constraints, result)
        normalized_requires = _validate_capability_name_list(name, "requires", requires, result)

        if not isinstance(determinism, dict):
            result.errors.append(f"Capability `{name}` must declare a `determinism` mapping.")
            continue

        normalized_determinism: dict[str, str] = {}
        for key in ("resolution", "fallback", "ambiguity"):
            value = determinism.get(key)
            if not isinstance(value, str) or not value.strip():
                result.errors.append(
                    f"Capability `{name}` determinism must include non-empty `{key}`."
                )
                continue
            normalized_determinism[key] = value.strip()

        capabilities[name] = CapabilitySpec(
            name=name,
            description=description.strip(),
            inputs=tuple(normalized_inputs),
            outputs=tuple(normalized_outputs),
            determinism=normalized_determinism,
            constraints=tuple(normalized_constraints),
            requires=tuple(normalized_requires),
            source_path=path,
        )

    return capabilities


def _validate_field_name_list(
    capability_name: str,
    field_name: str,
    values: Any,
    result: ValidationResult,
) -> list[str]:
    if not isinstance(values, list):
        result.errors.append(f"Capability `{capability_name}` field `{field_name}` must be a list.")
        return []

    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not isinstance(value, str) or not FIELD_NAME_PATTERN.fullmatch(value):
            result.errors.append(
                f"Capability `{capability_name}` field `{field_name}` contains invalid name `{value}`."
            )
            continue
        if value in seen:
            result.errors.append(
                f"Capability `{capability_name}` field `{field_name}` contains duplicate entry `{value}`."
            )
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


def _validate_string_list(
    capability_name: str,
    field_name: str,
    values: Any,
    result: ValidationResult,
) -> list[str]:
    if not isinstance(values, list):
        result.errors.append(f"Capability `{capability_name}` field `{field_name}` must be a list.")
        return []

    normalized: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            result.errors.append(
                f"Capability `{capability_name}` field `{field_name}` contains an invalid blank entry."
            )
            continue
        normalized.append(value.strip())
    return normalized


def _validate_capability_name_list(
    capability_name: str,
    field_name: str,
    values: Any,
    result: ValidationResult,
) -> list[str]:
    if not isinstance(values, list):
        result.errors.append(f"Capability `{capability_name}` field `{field_name}` must be a list.")
        return []

    normalized: list[str] = []
    for value in values:
        if not isinstance(value, str) or not CAPABILITY_NAME_PATTERN.fullmatch(value):
            result.errors.append(
                f"Capability `{capability_name}` field `{field_name}` contains invalid capability name `{value}`."
            )
            continue
        normalized.append(value)
    return normalized


def _load_bindings(root: Path, result: ValidationResult) -> dict[str, CapabilityBinding]:
    binding_path = root / ".github" / "runtime" / "capability-bindings.yaml"
    if not binding_path.exists():
        result.errors.append(f"Missing capability binding registry: {binding_path}")
        return {}

    try:
        payload = _read_yaml_file(binding_path) or {}
    except yaml.YAMLError as exc:
        result.errors.append(f"Capability binding registry is not valid YAML: {exc}")
        return {}

    bindings_payload = payload.get("bindings") if isinstance(payload, dict) else None
    if not isinstance(bindings_payload, dict):
        result.errors.append("Capability binding registry must contain a top-level `bindings` mapping.")
        return {}

    bindings: dict[str, CapabilityBinding] = {}
    for capability_name, binding_payload in bindings_payload.items():
        if not isinstance(capability_name, str) or not CAPABILITY_NAME_PATTERN.fullmatch(capability_name):
            result.errors.append(f"Invalid capability binding name: {capability_name!r}")
            continue

        if not isinstance(binding_payload, dict):
            result.errors.append(f"Binding `{capability_name}` must map to a YAML object.")
            continue

        policy_payload = binding_payload.get("policy") or {"mode": "single"}
        routes_payload = binding_payload.get("routes")
        if not isinstance(routes_payload, list) or not routes_payload:
            result.errors.append(f"Binding `{capability_name}` must declare a non-empty `routes` list.")
            continue

        if not isinstance(policy_payload, dict):
            result.errors.append(f"Binding `{capability_name}` policy must be a YAML object.")
            continue

        policy_mode = policy_payload.get("mode", "single")
        if not isinstance(policy_mode, str) or not POLICY_MODE_PATTERN.fullmatch(policy_mode):
            result.errors.append(
                f"Binding `{capability_name}` has invalid policy mode `{policy_mode}`."
            )
            continue

        routes: list[RouteBinding] = []
        seen_route_pairs: set[tuple[str, str]] = set()
        priorities: set[int] = set()
        for index, route_payload in enumerate(routes_payload, start=1):
            if not isinstance(route_payload, dict):
                result.errors.append(
                    f"Binding `{capability_name}` route #{index} must be a YAML object."
                )
                continue

            provider = route_payload.get("provider")
            tool = route_payload.get("tool")
            priority = route_payload.get("priority")

            if not isinstance(provider, str) or not PROVIDER_NAME_PATTERN.fullmatch(provider):
                result.errors.append(
                    f"Binding `{capability_name}` route #{index} has invalid provider `{provider}`."
                )
                continue

            if not isinstance(tool, str) or not TOOL_NAME_PATTERN.fullmatch(tool):
                result.errors.append(
                    f"Binding `{capability_name}` route #{index} has invalid tool `{tool}`."
                )
                continue

            route_key = (provider, tool)
            if route_key in seen_route_pairs:
                result.errors.append(
                    f"Binding `{capability_name}` duplicates route `{provider}/{tool}`."
                )
                continue
            seen_route_pairs.add(route_key)

            if priority is not None and not isinstance(priority, int):
                result.errors.append(
                    f"Binding `{capability_name}` route `{provider}/{tool}` has non-integer priority `{priority}`."
                )
                continue

            if isinstance(priority, int):
                if priority in priorities:
                    result.errors.append(
                        f"Binding `{capability_name}` reuses priority `{priority}` across multiple routes."
                    )
                    continue
                priorities.add(priority)

            routes.append(RouteBinding(provider=provider, tool=tool, priority=priority))

        bindings[capability_name] = CapabilityBinding(
            capability_name=capability_name,
            routes=tuple(routes),
            policy=BindingPolicy(mode=policy_mode),
        )

    return bindings


def load_registry(root: Path) -> tuple[CapabilityRegistry | None, ValidationResult]:
    result = ValidationResult()
    normalized_root = root.resolve(strict=False)
    mcp_servers = _read_mcp_servers(normalized_root, result)
    providers = _load_provider_catalog(normalized_root, result)
    capabilities = _load_capabilities(normalized_root, result)
    bindings = _load_bindings(normalized_root, result)

    registry = CapabilityRegistry(
        root=normalized_root,
        capabilities=capabilities,
        bindings=bindings,
        providers=providers,
        mcp_servers=mcp_servers,
    )
    return registry, result


def validate_registry(registry: CapabilityRegistry) -> ValidationResult:
    result = ValidationResult()

    for provider_name, provider in registry.providers.items():
        if provider.server not in registry.mcp_servers:
            result.errors.append(
                f"Provider `{provider_name}` points to missing MCP server `{provider.server}` in `.vscode/mcp.json`."
            )

    for capability_name, capability in registry.capabilities.items():
        for dependency in capability.requires:
            if dependency not in registry.capabilities:
                result.errors.append(
                    f"Capability `{capability_name}` requires unknown capability `{dependency}`."
                )

    for capability_name, binding in registry.bindings.items():
        if capability_name not in registry.capabilities:
            result.errors.append(
                f"Binding registry contains orphan binding for undefined capability `{capability_name}`."
            )

        if not binding.routes:
            result.errors.append(f"Binding `{capability_name}` has no routes.")
            continue

        if len(binding.routes) == 1 and binding.policy.mode not in {"single", "explicit", "priority"}:
            result.errors.append(
                f"Binding `{capability_name}` has unsupported single-route policy `{binding.policy.mode}`."
            )

        if len(binding.routes) > 1 and binding.policy.mode == "single":
            result.errors.append(
                f"Binding `{capability_name}` is ambiguous: multiple routes require explicit routing policy."
            )

        if binding.policy.mode == "priority":
            missing_priority = [route for route in binding.routes if route.priority is None]
            if missing_priority:
                result.errors.append(
                    f"Binding `{capability_name}` uses priority routing but at least one route is missing `priority`."
                )

        for route in binding.routes:
            provider = registry.providers.get(route.provider)
            if provider is None:
                result.errors.append(
                    f"Binding `{capability_name}` references missing provider `{route.provider}`."
                )
                continue
            if route.tool not in provider.tools:
                result.errors.append(
                    f"Binding `{capability_name}` maps to unknown tool `{route.tool}` for provider `{route.provider}`."
                )

    result.errors.extend(_detect_capability_cycles(registry.capabilities))
    return result


def _detect_capability_cycles(capabilities: dict[str, CapabilitySpec]) -> list[str]:
    errors: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(capability_name: str, trail: list[str]) -> None:
        if capability_name in visited:
            return
        if capability_name in visiting:
            cycle_start = trail.index(capability_name)
            cycle = trail[cycle_start:] + [capability_name]
            errors.append(f"Capability dependency cycle detected: {' -> '.join(cycle)}")
            return

        visiting.add(capability_name)
        trail.append(capability_name)
        for dependency in capabilities[capability_name].requires:
            if dependency in capabilities:
                visit(dependency, trail)
        trail.pop()
        visiting.remove(capability_name)
        visited.add(capability_name)

    for capability_name in capabilities:
        visit(capability_name, [])

    return sorted(set(errors))


def scan_skill_capability_refs(root: Path) -> dict[Path, list[str]]:
    refs_by_path: dict[Path, list[str]] = {}
    skill_root = root / ".github" / "skills"
    if not skill_root.exists():
        return refs_by_path

    for skill_path in sorted(skill_root.glob("*/SKILL.md")):
        refs = extract_capability_refs(skill_path.read_text(encoding="utf-8"))
        if refs:
            refs_by_path[skill_path] = refs
    return refs_by_path


def validate_skill_capability_refs(
    root: Path,
    text: str,
    *,
    source_name: str = "SKILL.md",
) -> ValidationResult:
    registry, result = load_registry(root)
    if registry is None:
        return result

    result.extend(validate_registry(registry))

    refs = extract_capability_refs(text)
    result.data["capability_refs"] = refs
    if not refs:
        return result

    raw_markers = sum(line.count("capability:") for line in iter_code_fence_filtered_lines(text))
    if raw_markers > len(refs):
        result.warnings.append(
            f"One or more capability markers appear malformed in {source_name}; use `capability:<dot.separated.name>`."
        )

    for capability_name in refs:
        if not CAPABILITY_NAME_PATTERN.fullmatch(capability_name):
            result.errors.append(
                f"Invalid capability marker `{capability_name}` in {source_name}; use lowercase dot-separated names."
            )
            continue

        if capability_name not in registry.capabilities:
            result.errors.append(
                f"Unknown capability reference `{capability_name}` in {source_name}."
            )
            continue

        if capability_name not in registry.bindings:
            result.errors.append(
                f"Capability `{capability_name}` is referenced in {source_name} but is not bound in `.github/runtime/capability-bindings.yaml`."
            )

    return result


def validate_repository(root: Path) -> ValidationResult:
    registry, result = load_registry(root)
    if registry is None:
        return result

    result.extend(validate_registry(registry))
    refs_by_path = scan_skill_capability_refs(root)
    result.data["skill_capability_refs"] = {
        path.relative_to(root).as_posix(): refs for path, refs in refs_by_path.items()
    }
    for path, refs in refs_by_path.items():
        for capability_name in refs:
            if capability_name not in registry.capabilities:
                result.errors.append(
                    f"Unknown capability reference `{capability_name}` in {path.relative_to(root).as_posix()}."
                )
                continue
            if capability_name not in registry.bindings:
                result.errors.append(
                    f"Capability `{capability_name}` is referenced in {path.relative_to(root).as_posix()} but is not bound."
                )

    return result


def resolve_capability(
    root: Path,
    capability_name: str,
    *,
    provider_name: str | None = None,
) -> CapabilityResolution:
    registry, load_result = load_registry(root)
    if load_result.errors:
        raise ValueError("; ".join(load_result.errors))
    if registry is None:
        raise ValueError(f"Could not load capability registry under {root}")

    registry_result = validate_registry(registry)
    if registry_result.errors:
        raise ValueError("; ".join(registry_result.errors))

    capability = registry.capabilities.get(capability_name)
    if capability is None:
        raise ValueError(f"Unknown capability: {capability_name}")

    binding = registry.bindings.get(capability_name)
    if binding is None:
        raise ValueError(f"Capability `{capability_name}` is not bound.")

    if len(binding.routes) == 1:
        route = binding.routes[0]
        provider = registry.providers[route.provider]
        return CapabilityResolution(
            capability=capability,
            binding=binding,
            route=route,
            server_name=provider.server,
        )

    if binding.policy.mode == "explicit":
        if not provider_name:
            raise ValueError(
                f"Capability `{capability_name}` has multiple providers and requires an explicit provider hint."
            )
        for route in binding.routes:
            if route.provider == provider_name:
                provider = registry.providers[route.provider]
                return CapabilityResolution(
                    capability=capability,
                    binding=binding,
                    route=route,
                    server_name=provider.server,
                )
        raise ValueError(
            f"Capability `{capability_name}` is not bound to provider `{provider_name}`."
        )

    if binding.policy.mode == "priority":
        prioritized_routes = sorted(binding.routes, key=lambda route: route.priority or 0)
        route = prioritized_routes[0]
        provider = registry.providers[route.provider]
        return CapabilityResolution(
            capability=capability,
            binding=binding,
            route=route,
            server_name=provider.server,
        )

    raise ValueError(
        f"Capability `{capability_name}` has ambiguous routing and no deterministic policy."
    )