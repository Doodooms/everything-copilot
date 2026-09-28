from __future__ import annotations

import json
import re

from ..agent_validation import AgentSource, validate_agent_semantics
from ..errors import TargetError
from ..ir import PackSource
from .common import CompiledTarget, ensure_supported_agent_plugins
from .portable import _compile_portable_core, _read_source_snapshot

_COPILOT_MODEL_SUFFIX = re.compile(r"\s+\(copilot\)$", re.IGNORECASE)
_SUPPORTED_REASONING_EFFORTS = frozenset(
    {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}
)


def _toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_codex_fields(
    agent_id: str,
    description: str,
    instructions: str,
    *,
    model: object = None,
    reasoning_effort: object = None,
) -> bytes:
    """Render already separated agent semantics and Codex-specific settings."""
    if not isinstance(description, str) or not description.strip():
        raise TargetError(f"Codex agent description must be non-empty: {agent_id}")
    if not isinstance(instructions, str) or not instructions.strip():
        raise TargetError(f"Codex agent instructions must be non-empty: {agent_id}")

    fields = [
        f"name = {_toml_string(agent_id)}",
        f"description = {_toml_string(description)}",
    ]
    if model is not None:
        if not isinstance(model, str) or not model.strip():
            raise TargetError(
                f"Codex agent model must be a non-empty string: {agent_id}"
            )
        codex_model = _COPILOT_MODEL_SUFFIX.sub("", model.strip()).casefold()
        codex_model = re.sub(r"\s+", "-", codex_model)
        if "(copilot)" in codex_model:
            raise TargetError(
                f"Codex cannot map the Copilot-specific model identifier: {model!r}"
            )
        fields.append(f"model = {_toml_string(codex_model)}")
    if reasoning_effort is not None:
        if (
            not isinstance(reasoning_effort, str)
            or reasoning_effort not in _SUPPORTED_REASONING_EFFORTS
        ):
            raise TargetError(
                f"unsupported Codex reasoning effort for {agent_id}: {reasoning_effort!r}"
            )
        fields.append(f"model_reasoning_effort = {_toml_string(reasoning_effort)}")
    fields.append(f"developer_instructions = {_toml_string(instructions.strip())}")
    return ("\n".join(fields) + "\n").encode("utf-8")


def render_codex_agent(agent_id: str, source: AgentSource) -> bytes:
    metadata = source.metadata
    description = metadata.get("description")
    if not isinstance(description, str):
        raise TargetError(f"Codex agent description must be non-empty: {agent_id}")
    return render_codex_fields(
        agent_id,
        description,
        source.body,
        model=metadata.get("model"),
        reasoning_effort=metadata.get("reasoning-effort"),
    )


def compile_codex(source: PackSource) -> CompiledTarget:
    if "codex" not in source.ir.compatibility.targets:
        raise TargetError(f"pack {source.ir.id!r} does not support the Codex target")

    ensure_supported_agent_plugins(source)
    snapshot = _read_source_snapshot(source)
    files = _compile_portable_core(source, snapshot).file_map()

    for contribution in source.ir.agents.contributions:
        content = snapshot.get(contribution.source)
        if content is None:
            raise TargetError(
                f"Codex agent source is absent from the validated snapshot: {contribution.source}"
            )
        parsed = validate_agent_semantics(content, contribution.id, contribution.source)
        output_path = f"codex-agents/{contribution.id}.toml"
        if output_path in files:
            raise TargetError(f"duplicate Codex agent export: {output_path}")
        files[output_path] = render_codex_agent(contribution.id, parsed)

    return CompiledTarget.create(
        "codex",
        source.ir.reference,
        files,
        source_digest=source.ir.content_digest,
    )
