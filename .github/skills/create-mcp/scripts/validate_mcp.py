from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer


app = typer.Typer(add_completion=False, no_args_is_help=True)
REMOTE_SERVER_TYPES = {"http", "sse", "streamable-http"}


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_string_list(value: Any, field_name: str, server_name: str, errors: list[str]) -> None:
    if value is None:
        return
    if not isinstance(value, list) or any(not _is_non_empty_string(item) for item in value):
        errors.append(
            f"Server `{server_name}` field `{field_name}` must be a list of non-empty strings when present."
        )


def _validate_string_mapping(value: Any, field_name: str, server_name: str, errors: list[str]) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        errors.append(f"Server `{server_name}` field `{field_name}` must be a mapping when present.")
        return
    for key, item in value.items():
        if not _is_non_empty_string(key) or not _is_non_empty_string(item):
            errors.append(
                f"Server `{server_name}` field `{field_name}` must map non-empty strings to non-empty strings."
            )
            return


def _validate_stdio_server(server_name: str, config: dict[str, Any], errors: list[str]) -> None:
    if not _is_non_empty_string(config.get("command")):
        errors.append(f"Server `{server_name}` with `type: stdio` must define a non-empty `command`.")
    _validate_string_list(config.get("args"), "args", server_name, errors)
    _validate_string_mapping(config.get("env"), "env", server_name, errors)
    if "cwd" in config and not _is_non_empty_string(config.get("cwd")):
        errors.append(f"Server `{server_name}` field `cwd` must be a non-empty string when present.")


def _validate_remote_server(server_name: str, config: dict[str, Any], errors: list[str]) -> None:
    if not _is_non_empty_string(config.get("url")):
        errors.append(
            f"Server `{server_name}` with remote transport must define a non-empty `url`."
        )
    _validate_string_mapping(config.get("headers"), "headers", server_name, errors)


def _resolve_server_type(server_name: str, config: dict[str, Any], errors: list[str], warnings: list[str]) -> str | None:
    server_type = config.get("type")
    if _is_non_empty_string(server_type):
        return server_type.strip().lower()

    if _is_non_empty_string(config.get("command")):
        warnings.append(
            f"Server `{server_name}` omits `type`; assuming `stdio` because `command` is present."
        )
        return "stdio"

    errors.append(
        f"Server `{server_name}` must define a non-empty `type`, or a local stdio `command` that lets the validator infer `stdio`."
    )
    return None


def _validate_server(server_name: str, config: Any, errors: list[str], warnings: list[str]) -> None:
    if not isinstance(config, dict):
        errors.append(f"Server `{server_name}` must be a JSON object.")
        return

    normalized_type = _resolve_server_type(server_name, config, errors, warnings)
    if normalized_type is None:
        return

    if normalized_type == "stdio":
        _validate_stdio_server(server_name, config, errors)
        return

    if normalized_type in REMOTE_SERVER_TYPES:
        _validate_remote_server(server_name, config, errors)
        return

    warnings.append(
        f"Server `{server_name}` uses unsupported type `{config.get('type')}`; only basic shape validation was applied."
    )


@app.command()
def validate_mcp(
    config: Path = typer.Option(
        Path(".vscode") / "mcp.json",
        "--config",
        exists=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
        help="Path to the VS Code MCP configuration file.",
    ),
    server: str | None = typer.Option(
        None,
        "--server",
        help="Optional server name to validate. Defaults to all configured servers.",
    ),
) -> None:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        payload = json.loads(config.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"MCP config is not valid JSON: {exc}")
        payload = {}

    if not isinstance(payload, dict):
        errors.append("MCP config root must be a JSON object.")
        payload = {}

    servers = payload.get("servers")
    if not isinstance(servers, dict) or not servers:
        errors.append("MCP config must define a non-empty `servers` object.")
        servers = {}

    selected_servers: dict[str, Any] = {}
    if isinstance(servers, dict) and servers:
        if server is None:
            selected_servers = dict(sorted(servers.items()))
        elif server in servers:
            selected_servers = {server: servers[server]}
        else:
            errors.append(f"Server `{server}` was not found in `{config}`.")

    for server_name, server_config in selected_servers.items():
        _validate_server(server_name, server_config, errors, warnings)

    if errors:
        typer.echo("ERRORS:")
        for error in errors:
            typer.echo(f"  - {error}")
    if warnings:
        typer.echo("WARNINGS:")
        for warning in warnings:
            typer.echo(f"  - {warning}")

    if errors:
        raise typer.Exit(code=1)

    typer.echo(f"Validation passed for {len(selected_servers)} server(s).")


if __name__ == "__main__":
    app()