from __future__ import annotations

import json
import re

import yaml

from ..errors import TargetError
from ..ir import PackSource
from .common import CompiledTarget, ensure_supported_agent_plugins
from .copilot import _repository_root, _validate_agent
from .portable import _compile_portable_core, _read_source_snapshot

_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?(.*)\Z", re.DOTALL)
_COPILOT_MODEL_SUFFIX = re.compile(r"\s+\(copilot\)$", re.IGNORECASE)
_SUPPORTED_REASONING_EFFORTS = frozenset(
    {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}
)


def _toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_codex_agent(agent_id: str, content: bytes, *, source_name: str) -> bytes:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TargetError(
            f"Codex agent source is not valid UTF-8: {source_name}"
        ) from exc

    match = _FRONTMATTER.match(text.replace("\r\n", "\n"))
    if match is None:
        raise TargetError(
            f"Codex agent source is missing YAML frontmatter: {source_name}"
        )
    try:
        metadata = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        raise TargetError(f"Codex agent frontmatter is invalid: {source_name}") from exc
    if not isinstance(metadata, dict):
        raise TargetError(f"Codex agent frontmatter must be a mapping: {source_name}")

    name = metadata.get("name")
    description = metadata.get("description")
    instructions = match.group(2).strip()
    if name != agent_id:
        raise TargetError(f"Codex agent name must match contribution ID: {agent_id}")
    if not isinstance(description, str) or not description.strip():
        raise TargetError(f"Codex agent description must be non-empty: {agent_id}")
    if not instructions:
        raise TargetError(f"Codex agent instructions must be non-empty: {agent_id}")

    fields = [
        f"name = {_toml_string(name)}",
        f"description = {_toml_string(description)}",
    ]

    model = metadata.get("model")
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

    reasoning_effort = metadata.get("reasoning-effort")
    if reasoning_effort is not None:
        if (
            not isinstance(reasoning_effort, str)
            or reasoning_effort not in _SUPPORTED_REASONING_EFFORTS
        ):
            raise TargetError(
                f"unsupported Codex reasoning effort for {agent_id}: {reasoning_effort!r}"
            )
        fields.append(f"model_reasoning_effort = {_toml_string(reasoning_effort)}")

    fields.append(f"developer_instructions = {_toml_string(instructions)}")
    document = "\n".join(fields) + "\n"
    return document.encode("utf-8")


def _codex_agent(source: PackSource, agent_id: str, relative_path: str) -> bytes:
    try:
        content = source.source_snapshot[relative_path]
    except KeyError as exc:
        raise TargetError(
            f"Codex agent source is unavailable: {relative_path}"
        ) from exc
    return render_codex_agent(agent_id, content, source_name=relative_path)


def compile_codex(source: PackSource) -> CompiledTarget:
    if "codex" not in source.ir.compatibility.targets:
        raise TargetError(f"pack {source.ir.id!r} does not support the Codex target")

    ensure_supported_agent_plugins(source)
    snapshot = _read_source_snapshot(source)
    files = _compile_portable_core(source, snapshot).file_map()
    repository_root = _repository_root()

    for contribution in source.ir.agents.contributions:
        content = snapshot.get(contribution.source)
        if content is None:
            raise TargetError(
                f"Codex agent source is absent from the validated snapshot: {contribution.source}"
            )
        _validate_agent(content, source.root / contribution.source, repository_root)
        output_path = f"codex-agents/{contribution.id}.toml"
        if output_path in files:
            raise TargetError(f"duplicate Codex agent export: {output_path}")
        files[output_path] = _codex_agent(source, contribution.id, contribution.source)

    return CompiledTarget.create(
        "codex",
        source.ir.reference,
        files,
        source_digest=source.ir.content_digest,
    )
