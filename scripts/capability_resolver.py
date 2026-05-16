from __future__ import annotations

import json
from pathlib import Path

import typer

try:
    from scripts.capability_registry import resolve_capability
except ImportError:
    from capability_registry import resolve_capability  # type: ignore


app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.callback()
def main() -> None:
    """Resolve abstract capabilities to deterministic MCP provider routes."""


@app.command()
def resolve(
    capability_name: str = typer.Option(..., "--capability", help="Capability name to resolve."),
    provider: str | None = typer.Option(
        None,
        "--provider",
        help="Optional explicit provider hint when the capability exposes multiple providers.",
    ),
    root: Path = typer.Option(
        Path.cwd(),
        "--root",
        exists=True,
        file_okay=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
        help="Repository root containing capability definitions and runtime bindings.",
    ),
) -> None:
    try:
        resolution = resolve_capability(root=root, capability_name=capability_name, provider_name=provider)
    except ValueError as exc:
        typer.echo(f"ERROR: {exc}")
        raise typer.Exit(code=1) from exc

    payload = {
        "capability": resolution.capability.name,
        "provider": resolution.route.provider,
        "tool": resolution.route.tool,
        "server": resolution.server_name,
        "policy": resolution.binding.policy.mode,
        "inputs": list(resolution.capability.inputs),
        "outputs": list(resolution.capability.outputs),
    }
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))
    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()