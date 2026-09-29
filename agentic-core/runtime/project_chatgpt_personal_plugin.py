# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML>=6.0,<7"]
# ///
"""Project the canonical Control ping probe as an OpenAI portable plugin."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlsplit

RUNTIME_ROOT = Path(__file__).resolve().parent
PLUGIN_ROOT = RUNTIME_ROOT.parent
sys.path[:0] = [str(RUNTIME_ROOT), str(PLUGIN_ROOT)]

from projection_metadata import file_map_digest, plugin_identity, plugin_tree_digest

from expertise.errors import PackValidationError, TargetError
from expertise.parser import parse_pack
from expertise.targets import compile_target
from expertise.targets.common import validate_target_files
from expertise.targets.validation import validate_mcp_manifest, validate_plugin_manifest
from expertise.validator import load_json_no_duplicate_keys

PACK_ROOT = PLUGIN_ROOT / "packs" / "control-ping-probe"
PACK_ID = "control-ping-probe"
MCP_SERVER_ID = "control"
MCP_TOOL_NAME = "control_ping"
OPENAI_APPS_PATH = "./.app.json"
APP_ID_PATTERN = re.compile(
    r"^(?:plugin_)?(?:asdk_app|connector|templated_apps)_[A-Za-z0-9][A-Za-z0-9_-]{0,127}$"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Project the canonical one-tool Control probe Pack as an OpenAI "
            "portable plugin. This does not register or install a ChatGPT app."
        )
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="new absolute output directory for the portable plugin package",
    )
    parser.add_argument(
        "--app-id",
        required=True,
        help="registered ChatGPT MCP app ID copied from ChatGPT Developer Mode",
    )
    parser.add_argument(
        "--mcp-url",
        required=True,
        help="HTTPS Streamable HTTP MCP endpoint registered with ChatGPT",
    )
    return parser


def _validate_app_id(app_id: str) -> None:
    if APP_ID_PATTERN.fullmatch(app_id) is None:
        raise ValueError(
            "app ID must use a documented OpenAI app prefix and contain only "
            "letters, digits, underscores, or hyphens"
        )


def _validate_mcp_url(mcp_url: str) -> None:
    try:
        mcp_url.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ValueError(
            "MCP URL must use ASCII; encode international hostnames as IDNA"
        ) from exc
    if any(
        character.isspace() or ord(character) < 0x20 or ord(character) == 0x7F
        for character in mcp_url
    ):
        raise ValueError("MCP URL must not contain whitespace or control characters")
    try:
        parsed = urlsplit(mcp_url)
        _ = parsed.port
    except ValueError as exc:
        raise ValueError("MCP URL is malformed") from exc
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path != "/mcp"
        or "?" in mcp_url
        or "#" in mcp_url
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError(
            "MCP URL must be an HTTPS endpoint at the exact /mcp path and without "
            "embedded credentials, query, or fragment"
        )


def _compile_files(
    app_id: str, mcp_url: str
) -> tuple[dict[str, bytes], dict[str, object]]:
    _validate_app_id(app_id)
    _validate_mcp_url(mcp_url)

    source = parse_pack(PACK_ROOT)
    pack = source.ir
    if pack.id != PACK_ID:
        raise TargetError(f"unexpected Control probe Pack ID: {pack.id!r}")
    if pack.skills or pack.agents.contributions or pack.agents.extensions:
        raise TargetError("Control probe Pack must not add skills or agents")
    if (
        len(pack.mcp_servers) != 1
        or pack.mcp_servers[0].id != MCP_SERVER_ID
        or pack.mcp_servers[0].tools != (MCP_TOOL_NAME,)
    ):
        raise TargetError("Control probe Pack must declare only control/control_ping")

    artifact = compile_target(source, "portable")
    files = dict(artifact.files)
    try:
        plugin_manifest = load_json_no_duplicate_keys(files["plugin.json"])
        mcp_manifest = load_json_no_duplicate_keys(files["mcp.json"])
    except (KeyError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise TargetError(
            "portable Pack output is missing valid plugin or MCP JSON"
        ) from exc
    if not isinstance(plugin_manifest, dict) or not isinstance(mcp_manifest, dict):
        raise TargetError("portable Pack output manifests must contain JSON objects")

    server_config = mcp_manifest.get("mcpServers")
    if not isinstance(server_config, dict) or set(server_config) != {MCP_SERVER_ID}:
        raise TargetError(
            "portable Pack output must configure only the control MCP server"
        )
    server = server_config[MCP_SERVER_ID]
    if not isinstance(server, dict) or server.get("type") != "streamable-http":
        raise TargetError("Control probe MCP must use Streamable HTTP")
    server["url"] = mcp_url

    extensions = plugin_manifest.setdefault("extensions", {})
    if not isinstance(extensions, dict):
        raise TargetError("portable plugin extensions must be an object")
    openai = extensions.setdefault("com.openai", {})
    if not isinstance(openai, dict):
        raise TargetError("OpenAI plugin extensions must be an object")
    if "apps" in openai and openai["apps"] != OPENAI_APPS_PATH:
        raise TargetError("source plugin already points to a different OpenAI app file")
    openai["apps"] = OPENAI_APPS_PATH

    app_manifest = {"apps": {MCP_SERVER_ID: {"id": app_id}}}
    files["plugin.json"] = (
        json.dumps(plugin_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    files["mcp.json"] = (
        json.dumps(mcp_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    files[".app.json"] = (
        json.dumps(app_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")

    validate_plugin_manifest(plugin_manifest)
    validate_mcp_manifest(mcp_manifest)
    if set(app_manifest["apps"]) != {MCP_SERVER_ID}:
        raise TargetError("OpenAI app mapping must contain only the Control probe")

    provenance: dict[str, object] = {
        "schema_version": 1,
        "target": "chatgpt-personal",
        "source_pack": f"{pack.id}@{pack.version}",
        "source_sha256": pack.content_digest,
        "projector_package_sha256": plugin_tree_digest(PLUGIN_ROOT),
        "registered_app_ids": [app_id],
        "mcp_servers": [MCP_SERVER_ID],
        "mcp_tools": [MCP_TOOL_NAME],
        "mcp_url_sha256": hashlib.sha256(mcp_url.encode("utf-8")).hexdigest(),
        "projected_files_sha256": file_map_digest(files),
    }
    provenance_path = "com.doodooms.agentic-workflow/projection.json"
    files[provenance_path] = (
        json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    files = dict(validate_target_files(files))
    return files, provenance


def _materialize(files: dict[str, bytes], output: Path) -> Path:
    if not output.is_absolute():
        raise ValueError("output path must be absolute")
    if output.exists() or output.is_symlink():
        raise ValueError(f"refusing to overwrite existing output: {output}")
    parent = output.parent
    if parent.is_symlink() or not parent.is_dir():
        raise ValueError(f"output parent must be an existing real directory: {parent}")

    output.mkdir()
    try:
        for relative, content in sorted(files.items()):
            target = output.joinpath(*relative.split("/"))
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(content)
    except OSError:
        shutil.rmtree(output, ignore_errors=True)
        raise
    return output


def _summary(
    files: dict[str, bytes], output: Path, provenance: dict[str, object]
) -> dict[str, object]:
    return {
        "status": "projected",
        "target": "chatgpt-personal",
        "plugin": plugin_identity(PLUGIN_ROOT),
        "source_pack": provenance["source_pack"],
        "source_sha256": provenance["source_sha256"],
        "projector_package_sha256": provenance["projector_package_sha256"],
        "artifact_sha256": file_map_digest(files),
        "mcp_servers": [MCP_SERVER_ID],
        "tools": [MCP_TOOL_NAME],
        "registered_apps": [MCP_SERVER_ID],
        "output": str(output),
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        files, provenance = _compile_files(args.app_id, args.mcp_url)
        output = _materialize(files, args.output)
        print(
            json.dumps(
                _summary(files, output, provenance),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
    except (OSError, PackValidationError, TargetError, TypeError, ValueError) as exc:
        print(
            json.dumps(
                {"status": "error", "error": type(exc).__name__, "message": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
