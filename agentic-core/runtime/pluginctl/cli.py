from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from expertise.errors import ExpertiseError

from .controller import PluginController
from .models import PluginControlError, TrustedRegistry


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pluginctl")
    parser.add_argument(
        "--store-root",
        type=Path,
        required=True,
        help="explicit private store root; no default store path is assumed",
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=Path.cwd(),
        help="workspace whose .agentic profile state is managed",
    )
    parser.add_argument(
        "--trusted-registry",
        type=Path,
        help="optional local trusted registry file; otherwise read store-root/trusted-registry.json",
    )
    parser.add_argument(
        "--host-capability",
        action="append",
        default=[],
        help="capability explicitly provided by the selected host",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    check = commands.add_parser("check", help="validate one explicit local pack source")
    check.add_argument("source_root", type=Path)

    commands.add_parser("resolve", help="resolve the workspace Active Set without writing")

    install = commands.add_parser("install", help="install a registry-pinned local pack")
    install.add_argument("pack_id")
    install.add_argument("version")
    install.add_argument("--digest")
    install.add_argument("--approve", action="store_true")

    activate = commands.add_parser("activate", help="select an installed pack for this workspace")
    activate.add_argument("pack_id")
    activate.add_argument("version")
    activate.add_argument("--capability", action="append", required=True)

    deactivate = commands.add_parser("deactivate", help="remove a pack from the desired Active Set")
    deactivate.add_argument("pack_id")
    deactivate.add_argument("version")

    commands.add_parser("materialize", help="stage and validate the Effective Profile")
    commands.add_parser("inspect", help="inspect local availability, installation, and workspace state")
    commands.add_parser("rollback", help="restore prior state and recompose the profile")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        registry = (
            TrustedRegistry.from_file(args.trusted_registry)
            if args.trusted_registry is not None
            else None
        )
        controller = PluginController(
            args.store_root,
            workspace_root=args.workspace_root,
            trusted_registry=registry,
            host_capabilities=args.host_capability,
        )
        if args.command == "check":
            result = controller.check(args.source_root)
        elif args.command == "resolve":
            effective = controller.resolve()
            result = {
                "status": "resolved",
                "fingerprint": effective.fingerprint,
                "effective_ir": effective.as_dict(),
            }
        elif args.command == "install":
            result = controller.install(
                args.pack_id,
                args.version,
                approved=args.approve,
                expected_digest=args.digest,
            )
        elif args.command == "activate":
            result = controller.activate(
                args.pack_id,
                args.version,
                capabilities=args.capability,
            )
        elif args.command == "deactivate":
            result = controller.deactivate(args.pack_id, args.version)
        elif args.command == "materialize":
            result = controller.materialize()
        elif args.command == "inspect":
            result = controller.inspect()
        elif args.command == "rollback":
            result = controller.rollback()
        else:
            raise PluginControlError(f"unsupported pluginctl command: {args.command}")
        _emit(result)
        return 0
    except (PluginControlError, ExpertiseError, OSError, ValueError) as exc:
        _emit(
            {
                "status": "error",
                "error": type(exc).__name__,
                "message": str(exc),
            }
        )
        return 2
