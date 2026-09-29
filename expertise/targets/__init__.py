from __future__ import annotations

from pathlib import Path

from ..errors import TargetError
from ..ir import PackSource
from ..ontology import SUPPORTED_TARGETS
from .codex import compile_codex
from .common import CompiledTarget, validate_target_files
from .copilot import compile_copilot
from .portable import compile_portable
from .validation import validate_mcp_manifest, validate_plugin_manifest


def compile_target(
    source: PackSource,
    target: str,
) -> CompiledTarget:
    if target not in SUPPORTED_TARGETS:
        raise TargetError(f"unsupported Expertise Pack target: {target!r}")
    if target == "portable":
        return compile_portable(source)
    if target == "copilot":
        return compile_copilot(source)
    return compile_codex(source)


def materialize_target(
    artifact: CompiledTarget, *, output_dir: Path, dist_root: Path
) -> Path:
    if not isinstance(artifact, CompiledTarget):
        raise TargetError("artifact must be a CompiledTarget")
    files = validate_target_files(artifact.files)
    raw_dist = Path(dist_root)
    raw_output = Path(output_dir)
    if not raw_dist.is_absolute():
        raise TargetError("dist_root must be an absolute path")
    if raw_output.is_symlink() or raw_dist.is_symlink():
        raise TargetError("dist/output roots must not be symlinks")
    if not raw_output.is_absolute():
        raw_output = raw_dist / raw_output

    dist_path = raw_dist.resolve(strict=False)
    output_path = raw_output.resolve(strict=False)
    try:
        relative_output = output_path.relative_to(dist_path)
    except ValueError as exc:
        raise TargetError("generated output path must remain under dist") from exc
    if raw_dist.name != "dist" or not relative_output.parts:
        raise TargetError(
            "generated artifacts must be materialized below a dist directory"
        )
    if ".github" in relative_output.parts:
        raise TargetError(
            "generated output must not materialize consumer .github content"
        )
    if raw_output.exists() or raw_output.is_symlink():
        raise TargetError(
            f"generated output already exists; refusing to overwrite: {raw_output}"
        )

    try:
        raw_output.mkdir(parents=True, exist_ok=False)
        for relative, content in sorted(files.items()):
            target_file = raw_output / Path(relative)
            target_file.parent.mkdir(parents=True, exist_ok=True)
            with target_file.open("xb") as stream:
                stream.write(content)
    except FileExistsError as exc:
        raise TargetError(
            f"generated output already exists; refusing to overwrite: {raw_output}"
        ) from exc
    except OSError as exc:
        raise TargetError(
            f"could not materialize generated target under dist: {exc}"
        ) from exc
    return raw_output


__all__ = [
    "CompiledTarget",
    "compile_target",
    "materialize_target",
    "validate_mcp_manifest",
    "validate_plugin_manifest",
]
