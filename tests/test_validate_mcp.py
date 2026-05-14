import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATE_MCP_PATH = REPO_ROOT / ".github" / "skills" / "create-mcp" / "scripts" / "validate_mcp.py"


def test_validate_mcp_accepts_valid_stdio_config(tmp_path: Path) -> None:
    config_path = tmp_path / "mcp.json"
    config_path.write_text(
        json.dumps(
            {
                "servers": {
                    "demo": {
                        "type": "stdio",
                        "command": "uv",
                        "args": ["run", "python", "server.py"],
                        "env": {"MODE": "test"},
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    result = _run_validate_mcp(config_path)

    assert result.returncode == 0, (result.stdout + result.stderr).strip()
    assert "Validation passed" in result.stdout


def test_validate_mcp_rejects_stdio_server_without_command(tmp_path: Path) -> None:
    config_path = tmp_path / "mcp.json"
    config_path.write_text(
        json.dumps({"servers": {"broken": {"type": "stdio", "args": ["serve"]}}}),
        encoding="utf-8",
    )

    result = _run_validate_mcp(config_path)

    assert result.returncode == 1, (result.stdout + result.stderr).strip()
    assert "must define a non-empty `command`" in result.stdout


def test_live_workspace_mcp_config_validates() -> None:
    result = _run_validate_mcp(REPO_ROOT / ".vscode" / "mcp.json")

    assert result.returncode == 0, (result.stdout + result.stderr).strip()


def _run_validate_mcp(config_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATE_MCP_PATH), "--config", str(config_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )