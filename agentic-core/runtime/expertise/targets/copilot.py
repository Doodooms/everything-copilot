from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from ..errors import TargetError
from ..ir import PackSource
from .common import CompiledTarget, ensure_supported_agent_plugins
from .portable import (
    _compile_portable_core,
    _read_source_snapshot,
)


def _repository_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        plugin_scripts = (
            parent
            / "skills"
            / "plugin-engineering"
            / "references"
            / "create-agent"
            / "scripts"
        )
        if plugin_scripts.is_dir():
            return parent
        repository_scripts = (
            parent
            / "agentic-core"
            / "skills"
            / "plugin-engineering"
            / "references"
            / "create-agent"
            / "scripts"
        )
        if repository_scripts.is_dir():
            return parent
    raise TargetError("canonical Copilot agent validator is unavailable")


_AGENT_VALIDATOR_SCRIPT = """\
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])
from agent_lint_core import (
    LintResult,
    lint_agent_frontmatter,
    lint_agent_markdown_contract,
    split_frontmatter,
)

agent_file = Path(sys.argv[2])
text = sys.stdin.read()
result = LintResult()
try:
    frontmatter, body = split_frontmatter(text)
except ValueError as exc:
    result.errors.append(str(exc))
    body = ""
else:
    expected_name = agent_file.name.removesuffix(".agent.md")
    if frontmatter.get("name") != expected_name:
        result.errors.append(
            f"Frontmatter `name` must match the `.agent.md` filename stem `{expected_name}`."
        )
    result.extend(lint_agent_frontmatter(frontmatter, agent_file))

if body:
    result.extend(lint_agent_markdown_contract(body, agent_file, frontmatter))
else:
    result.errors.append("Agent body is empty.")

if result.errors:
    print("\\n".join(result.errors))
    raise SystemExit(1)
"""


def _validate_agent(
    agent_content: bytes,
    agent_path: Path,
    repository_root: Path,
) -> None:
    core_root = (
        repository_root
        if (repository_root / "skills").is_dir()
        else repository_root / "agentic-core"
    )
    scripts = (
        core_root
        / "skills"
        / "plugin-engineering"
        / "references"
        / "create-agent"
        / "scripts"
    )
    validator = scripts / "validate_agent.py"
    linter = scripts / "agent_lint_core.py"
    if not validator.is_file() or not linter.is_file():
        raise TargetError("canonical Copilot agent validator is unavailable")
    try:
        text = agent_content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TargetError(
            f"Copilot agent source is not valid UTF-8: {agent_path.name}"
        ) from exc

    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            _AGENT_VALIDATOR_SCRIPT,
            str(scripts),
            str(agent_path),
        ],
        cwd=repository_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        input=text,
        check=False,
        env=environment,
    )
    if result.returncode != 0:
        details = (result.stdout + result.stderr).strip()
        raise TargetError(f"invalid Copilot agent source {agent_path.name}: {details}")


def compile_copilot(source: PackSource) -> CompiledTarget:
    if "copilot" not in source.ir.compatibility.targets:
        raise TargetError(f"pack {source.ir.id!r} does not support the Copilot target")

    ensure_supported_agent_plugins(source)
    source_snapshot = _read_source_snapshot(source)
    files = _compile_portable_core(source, source_snapshot).file_map()
    repo_root = _repository_root()
    for contribution in source.ir.agents.contributions:
        source_agent = source.root / contribution.source
        try:
            agent_content = source_snapshot[contribution.source]
        except KeyError as exc:
            raise TargetError(
                f"agent source is absent from the validated snapshot: {contribution.source}"
            ) from exc
        _validate_agent(agent_content, source_agent, repo_root)
        target_path = f"com.github.copilot/agents/{contribution.id}.agent.md"
        if target_path in files:
            raise TargetError(f"duplicate Copilot output path: {target_path}")
        files[target_path] = agent_content

    return CompiledTarget.create(
        "copilot",
        source.ir.reference,
        files,
        source_digest=source.ir.content_digest,
    )
