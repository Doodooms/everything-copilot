import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LINTER_PATH = REPO_ROOT / "scripts" / "customization_lint.py"

DEFAULT_MCP_CONFIG = {
    "servers": {
        "graphify": {
            "type": "stdio",
            "command": "uv",
            "args": ["run", "python", "scripts/atomic_index.py", "serve-graphify"],
            "env": {},
        },
        "gitnexus": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@duytransipher/gitnexus@latest", "mcp"],
            "env": {},
        },
    }
}

DEFAULT_PROVIDER_CATALOG = textwrap.dedent(
    """
    providers:
      graphify:
        server: graphify
        tools:
          - query_graph
          - get_node
          - get_neighbors
          - shortest_path
      gitnexus:
        server: gitnexus
        tools:
          - impact
          - context
          - detect_changes
          - rename
          - route_map
    """
).strip() + "\n"

DEFAULT_CAPABILITY = textwrap.dedent(
    """
    name: graph.semantic.related
    description: Resolve semantically related entities from the workspace graph.
    inputs:
      - query
      - scope
    outputs:
      - related_entities
      - confidence
    determinism:
      resolution: explicit
      fallback: forbidden
      ambiguity: fail
    constraints: []
    requires: []
    """
).strip() + "\n"

DEFAULT_BINDINGS = textwrap.dedent(
    """
    bindings:
      graph.semantic.related:
        routes:
          - provider: graphify
            tool: query_graph
    """
).strip() + "\n"

DEFAULT_SKILL = textwrap.dedent(
    """
    ---
    name: capability-aware-skill
    description: "WHAT: Exercise capability-aware skill linting. USE FOR: validating deterministic capability references. DO NOT USE FOR: production workflows."
    user-invocable: false
    ---

    <definitions>

    - **capability reference** : Abstract deterministic execution contract resolved to a concrete MCP tool later.

    </definitions>

    <workflow>

    ## Step 0 - **CONFIRMATION**

    1. Confirm the capability-aware workflow applies.

    <rules>

    - Keep provider routing explicit and deterministic.

    </rules>

    ## Step 1 - Inspect

    1. Inspect the available capability surfaces before using one.
       - Review [capability guide](./references/guide.md) only if the contract still needs clarification.

    ## Step 2 - Resolve

    1. Use capability:graph.semantic.related to retrieve semantically related graph context.

    ## Step 3 - Return

    1. Return the resolved graph context to the caller.

    </workflow>
    """
).strip() + "\n"


class CapabilityLayerTest(unittest.TestCase):
    def test_skill_lint_accepts_capability_reference_without_tool_warning(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT, prefix=".tmp-capability-") as temp_dir:
            root = Path(temp_dir)
            skill_dir = self._write_workspace(root)

            result = subprocess.run(
                [sys.executable, str(LINTER_PATH), "skill", "--skill-dir", str(skill_dir)],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, msg=(result.stdout + result.stderr).strip())
        self.assertNotIn("No `#tool:` references found", result.stdout)

    def test_resolver_returns_single_deterministic_route(self) -> None:
        from scripts import capability_resolver

        with tempfile.TemporaryDirectory(dir=REPO_ROOT, prefix=".tmp-capability-") as temp_dir:
            root = Path(temp_dir)
            self._write_workspace(root)

            resolution = capability_resolver.resolve_capability(
                root=root,
                capability_name="graph.semantic.related",
            )

        self.assertEqual(resolution.capability.name, "graph.semantic.related")
        self.assertEqual(resolution.route.provider, "graphify")
        self.assertEqual(resolution.route.tool, "query_graph")
        self.assertEqual(resolution.server_name, "graphify")

    def test_validator_rejects_unknown_provider_tool(self) -> None:
        from scripts import capability_validator

        bad_bindings = textwrap.dedent(
            """
            bindings:
              graph.semantic.related:
                routes:
                  - provider: graphify
                    tool: missing_tool
            """
        ).strip() + "\n"

        with tempfile.TemporaryDirectory(dir=REPO_ROOT, prefix=".tmp-capability-") as temp_dir:
            root = Path(temp_dir)
            self._write_workspace(root, bindings_text=bad_bindings)

            result = capability_validator.validate_repository(root)

        self.assertTrue(
            any("missing_tool" in error and "graphify" in error for error in result.errors),
            msg=result.errors,
        )

    def test_validator_rejects_ambiguous_binding_without_policy(self) -> None:
        from scripts import capability_validator

        ambiguous_bindings = textwrap.dedent(
            """
            bindings:
              graph.semantic.related:
                routes:
                  - provider: graphify
                    tool: query_graph
                  - provider: gitnexus
                    tool: context
            """
        ).strip() + "\n"

        with tempfile.TemporaryDirectory(dir=REPO_ROOT, prefix=".tmp-capability-") as temp_dir:
            root = Path(temp_dir)
            self._write_workspace(root, bindings_text=ambiguous_bindings)

            result = capability_validator.validate_repository(root)

        self.assertTrue(
            any("ambiguous" in error.lower() for error in result.errors),
            msg=result.errors,
        )

    def test_validator_rejects_capability_dependency_cycles(self) -> None:
        from scripts import capability_validator

        capabilities = {
            "graph.semantic.related.yaml": textwrap.dedent(
                """
                name: graph.semantic.related
                description: Resolve related graph entities.
                inputs: [query]
                outputs: [related_entities]
                determinism:
                  resolution: explicit
                  fallback: forbidden
                  ambiguity: fail
                constraints: []
                requires: [graph.code.impact-analysis]
                """
            ).strip() + "\n",
            "graph.code.impact-analysis.yaml": textwrap.dedent(
                """
                name: graph.code.impact-analysis
                description: Compute blast radius for graph-linked code changes.
                inputs: [symbol]
                outputs: [impact_summary]
                determinism:
                  resolution: explicit
                  fallback: forbidden
                  ambiguity: fail
                constraints: []
                requires: [graph.semantic.related]
                """
            ).strip() + "\n",
        }
        bindings = textwrap.dedent(
            """
            bindings:
              graph.semantic.related:
                routes:
                  - provider: graphify
                    tool: query_graph
              graph.code.impact-analysis:
                routes:
                  - provider: gitnexus
                    tool: impact
            """
        ).strip() + "\n"

        with tempfile.TemporaryDirectory(dir=REPO_ROOT, prefix=".tmp-capability-") as temp_dir:
            root = Path(temp_dir)
            self._write_workspace(root, capability_files=capabilities, bindings_text=bindings)

            result = capability_validator.validate_repository(root)

        self.assertTrue(
            any("cycle" in error.lower() for error in result.errors),
            msg=result.errors,
        )

    def test_live_repo_capability_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "capability_validator.py"), "repo", "--root", str(REPO_ROOT)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=(result.stdout + result.stderr).strip())

    def _write_workspace(
        self,
        root: Path,
        *,
        capability_files: dict[str, str] | None = None,
        bindings_text: str | None = None,
        provider_catalog_text: str | None = None,
        skill_text: str | None = None,
    ) -> Path:
        capability_dir = root / ".github" / "capabilities"
        runtime_dir = root / ".github" / "runtime"
        skill_dir = root / ".github" / "skills" / "capability-aware-skill"
        reference_dir = skill_dir / "references"
        vscode_dir = root / ".vscode"

        capability_dir.mkdir(parents=True, exist_ok=True)
        runtime_dir.mkdir(parents=True, exist_ok=True)
        reference_dir.mkdir(parents=True, exist_ok=True)
        vscode_dir.mkdir(parents=True, exist_ok=True)

        for relative_path, content in (capability_files or {"graph.semantic.related.yaml": DEFAULT_CAPABILITY}).items():
            (capability_dir / relative_path).write_text(content, encoding="utf-8")

        (runtime_dir / "provider-catalog.yaml").write_text(
            provider_catalog_text or DEFAULT_PROVIDER_CATALOG,
            encoding="utf-8",
        )
        (runtime_dir / "capability-bindings.yaml").write_text(
            bindings_text or DEFAULT_BINDINGS,
            encoding="utf-8",
        )
        (vscode_dir / "mcp.json").write_text(
            json.dumps(DEFAULT_MCP_CONFIG, indent=2) + "\n",
            encoding="utf-8",
        )
        (reference_dir / "guide.md").write_text("# Guide\n\nCapability guidance.\n", encoding="utf-8")
        (skill_dir / "SKILL.md").write_text(skill_text or DEFAULT_SKILL, encoding="utf-8")

        return skill_dir


if __name__ == "__main__":
    unittest.main()