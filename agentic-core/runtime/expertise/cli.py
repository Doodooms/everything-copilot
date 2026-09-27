from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .errors import ExpertiseError, PackValidationError, TargetError
from .ontology import PACK_ID_PATTERN, SUPPORTED_TARGETS
from .parser import parse_pack
from .scaffold import scaffold_pack
from .targets import compile_target, materialize_target


def _pack_root(repository_root: Path, pack_id: str) -> Path:
    if PACK_ID_PATTERN.fullmatch(pack_id) is None:
        raise PackValidationError((f"invalid pack ID {pack_id!r}",))
    packs_root = repository_root / "expertise" / "packs"
    candidate = packs_root / pack_id
    if candidate.is_symlink():
        raise PackValidationError((f"pack source must not be a symlink: {candidate}",))
    try:
        resolved_root = packs_root.resolve(strict=True)
        resolved_candidate = candidate.resolve(strict=True)
        resolved_candidate.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise PackValidationError(
            (f"pack source is not present under expertise/packs/: {pack_id}",)
        ) from exc
    return resolved_candidate


def _json_line(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="expertise")
    commands = parser.add_subparsers(dest="command", required=True)

    scaffold = commands.add_parser(
        "scaffold",
        help="create a validated starter Expertise Pack source and skill package",
    )
    scaffold.add_argument("pack_id")
    scaffold.add_argument("--type", choices=("horizontal", "vertical"), default="horizontal")
    scaffold.add_argument("--name", required=True)
    scaffold.add_argument("--description", required=True)
    scaffold.add_argument("--capability", required=True)
    scaffold.add_argument("--skill-id", required=True)
    scaffold.add_argument("--skill-description", required=True)
    scaffold.add_argument("--publisher", required=True)
    scaffold.add_argument("--source", required=True)
    scaffold.add_argument("--version", default="0.1.0")
    scaffold.add_argument(
        "--project-to",
        action="append",
        default=[],
        help="core agent to receive this skill/capability projection; may be repeated",
    )
    scaffold.add_argument(
        "--target",
        action="append",
        choices=sorted(SUPPORTED_TARGETS),
        help="target to validate in the scaffold; may be repeated (default: all supported)",
    )

    validate = commands.add_parser("validate", help="parse and validate one local pack source")
    validate.add_argument("pack_id")

    build = commands.add_parser("build", help="compile a pack to a portable or Copilot target")
    build.add_argument("pack_id")
    build.add_argument("--target", choices=sorted(SUPPORTED_TARGETS), required=True)
    build.add_argument(
        "--output",
        type=Path,
        help="optional output path; it must resolve below this repository's dist/ directory",
    )

    test = commands.add_parser("test", help="validate and smoke-compile declared targets in memory")
    test.add_argument("pack_id")
    return parser


def _test_pack(source, repository_root: Path) -> dict[str, Any]:
    artifacts = [
        compile_target(source, target)
        for target in source.ir.compatibility.targets
    ]
    by_target = {artifact.target: artifact for artifact in artifacts}
    if "portable" in by_target:
        portable_files = by_target["portable"].file_map()
        for target in ("copilot", "codex"):
            if target not in by_target:
                continue
            target_artifact = by_target[target]
            target_files = target_artifact.file_map()
            if by_target["portable"].source_digest != target_artifact.source_digest:
                raise TargetError(
                    f"portable and {target} targets used different source snapshots"
                )
            for relative, content in portable_files.items():
                if target_files.get(relative) != content:
                    raise TargetError(
                        f"{target} target differs from portable core at {relative}"
                    )
    return {
        "status": "passed",
        "pack": source.ir.id,
        "version": source.ir.version,
        "targets": {
            target: {
                "digest": artifact.digest,
                "source_digest": artifact.source_digest,
                "files": sorted(artifact.files),
            }
            for target, artifact in sorted(by_target.items())
        },
    }


def main(argv: list[str] | None = None, *, repo_root: Path | None = None) -> int:
    args = build_parser().parse_args(argv)
    repository_root = Path(repo_root or Path.cwd()).resolve()
    try:
        if args.command == "scaffold":
            result = scaffold_pack(
                repository_root,
                pack_id=args.pack_id,
                pack_type=args.type,
                name=args.name,
                description=args.description,
                capability=args.capability,
                skill_id=args.skill_id,
                skill_description=args.skill_description,
                project_to=args.project_to,
                publisher=args.publisher,
                source=args.source,
                version=args.version,
                targets=args.target or sorted(SUPPORTED_TARGETS),
            )
            _json_line(result)
            return 0

        source = parse_pack(_pack_root(repository_root, args.pack_id))
        if args.command == "validate":
            _json_line(
                {
                    "status": "valid",
                    "pack": source.ir.id,
                    "version": source.ir.version,
                    "fingerprint": source.ir.fingerprint,
                    "content_digest": source.ir.content_digest,
                }
            )
            return 0
        if args.command == "test":
            _json_line(_test_pack(source, repository_root))
            return 0
        if args.command == "build":
            artifact = compile_target(source, args.target)
            dist_root = repository_root / "dist"
            default_output = (
                dist_root / source.ir.id / source.ir.version / args.target
            )
            if args.output is None:
                output = default_output
            else:
                output = args.output
                if not output.is_absolute():
                    output = repository_root / output
            written = materialize_target(
                artifact, output_dir=output, dist_root=dist_root
            )
            _json_line(
                {
                    "status": "built",
                    "pack": source.ir.id,
                    "version": source.ir.version,
                    "target": args.target,
                    "output": written.relative_to(repository_root).as_posix(),
                    "digest": artifact.digest,
                    "source_digest": artifact.source_digest,
                    "files": sorted(artifact.files),
                }
            )
            return 0
        raise TargetError(f"unsupported command: {args.command}")
    except ExpertiseError as exc:
        diagnostics = getattr(exc, "diagnostics", ())
        _json_line(
            {
                "status": "error",
                "error": type(exc).__name__,
                "message": str(exc),
                "diagnostics": list(diagnostics),
            }
        )
        return 2
    except OSError as exc:
        _json_line(
            {
                "status": "error",
                "error": "FilesystemError",
                "message": str(exc),
                "diagnostics": [],
            }
        )
        return 2
