from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


class ClaudeProjectionTests(unittest.TestCase):
    def test_explicit_source_projects_plugin_without_mutating_source(self):
        from factory.projection.claude import project_claude_plugin

        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            source = workspace / "a-plugin"
            output = workspace / "projected-plugin"
            shutil.copytree(
                ROOT / "agentic-core",
                source,
                ignore=shutil.ignore_patterns("com.github.copilot"),
            )
            before = _tree_digest(source)

            projection = project_claude_plugin(source)
            projection.write(output)

            self.assertEqual(_tree_digest(source), before)
            self.assertTrue((output / ".claude-plugin/plugin.json").is_file())
            self.assertTrue((output / ".mcp.json").is_file())
            self.assertTrue((output / "skills/plugin-engineering/SKILL.md").is_file())
            manifest = json.loads(
                (output / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["name"], "agentic-core")
            self.assertEqual(manifest["version"], "0.3.5")
            self.assertNotIn(b"/home/pm/", b"".join(projection.files.values()))
            self.assertNotIn(b"/Users/", b"".join(projection.files.values()))
            agents = sorted((output / "agents").glob("*.md"))
            self.assertEqual(len(agents), 9)
            for agent_path in agents:
                content = agent_path.read_text(encoding="utf-8")
                frontmatter, body = content.split("---", 2)[1:]
                metadata = yaml.safe_load(frontmatter)
                self.assertEqual(set(metadata), {"name", "description"})
                self.assertEqual(metadata["name"], agent_path.stem)
                self.assertTrue(body.strip())
            mcp = json.loads((output / ".mcp.json").read_text(encoding="utf-8"))
            github = mcp["mcpServers"]["github-mcp-server"]
            self.assertIn("${CLAUDE_PLUGIN_ROOT}", " ".join(github["args"]))
            self.assertNotIn("/home/pm/", json.dumps(mcp))
            mappings = {
                item["capability"]: item
                for item in projection.provenance["capability_mappings"]
            }
            self.assertEqual(mappings["search"]["claude_form"], "Glob/Grep")
            self.assertEqual(mappings["search"]["classification"], "ADAPTED")
            self.assertEqual(mappings["question"]["classification"], "UNSUPPORTED")
            for agent_path in agents:
                self.assertNotIn(
                    "[[capability:", agent_path.read_text(encoding="utf-8")
                )
            for finding in projection.provenance["resource_findings"]:
                self.assertIn(finding["classification"], {"PRESERVED", "UNSUPPORTED"})
            generated_agent = output / "agents/orchestrator.md"
            sidecar = output.with_name(f"{output.name}.projection.json")
            original_agent = generated_agent.read_bytes()
            generated_agent.write_text("different output", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "differing projected file"):
                projection.write(output)
            projection.write(output, replace=True)
            self.assertEqual(generated_agent.read_bytes(), original_agent)
            sidecar.write_text("different provenance", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "differing provenance sidecar"):
                projection.write(output)
            projection.write(output, replace=True)

            sidecar.unlink()
            sidecar.symlink_to(generated_agent)
            with self.assertRaisesRegex(ValueError, "provenance symlink"):
                projection.write(output, replace=True)

    def test_projection_is_deterministic_and_provenance_tracks_target_and_digests(self):
        from factory.projection.claude import project_claude_plugin

        first = project_claude_plugin(ROOT / "agentic-core")
        second = project_claude_plugin(ROOT / "agentic-core")

        self.assertEqual(first.files, second.files)
        self.assertEqual(first.provenance, second.provenance)
        self.assertEqual(first.provenance["target"], "claude")
        self.assertEqual(first.provenance["source"]["name"], "agentic-core")
        self.assertEqual(first.provenance["artifact_sha256"], _map_digest(first.files))
        self.assertIn("adaptations", first.provenance)
        self.assertIn("git_base_commit", first.provenance["source"])
        self.assertIn("dirty", first.provenance["source"])

    def test_existing_directory_skill_link_is_reported_as_preserved(self):
        from factory.projection.claude import project_claude_plugin

        projection = project_claude_plugin(ROOT / "agentic-core")
        directory_reference = next(
            finding
            for finding in projection.provenance["resource_findings"]
            if finding["source"]
            == "skills/orchestration/references/orchestrate/references/manifest_schema.md"
            and finding["target"] == "../schemas/"
        )

        self.assertEqual(directory_reference["classification"], "PRESERVED")
        self.assertEqual(directory_reference["resource_type"], "directory")

    def test_source_machine_paths_and_escaping_skill_links_are_rejected(self):
        from factory.projection.claude import project_claude_plugin

        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "plugin"
            _write(source / "plugin.json", '{"name":"sample","version":"1.0.0"}')
            _write(
                source / "agents/worker.md",
                "---\nname: worker\ndescription: A worker.\n---\nInstructions.\n",
            )
            _write(
                source / "mcp.json",
                '{"mcpServers":{"local":{"command":"/opt/local/server","args":[]}}}',
            )

            with self.assertRaisesRegex(ValueError, "absolute machine path"):
                project_claude_plugin(source)

            _write(
                source / "mcp.json",
                '{"mcpServers":{"local":{"command":"bash","args":["../outside/script.sh"]}}}',
            )
            with self.assertRaisesRegex(ValueError, "escapes the plugin root"):
                project_claude_plugin(source)

            _write(source / "mcp.json", '{"mcpServers":{}}')
            _write(
                source / "skills/sample/SKILL.md",
                "---\nname: sample\ndescription: A skill.\n---\n"
                "Read [outside](../../../outside.md).\n",
            )
            with self.assertRaisesRegex(ValueError, "escapes packaged skills"):
                project_claude_plugin(source)


def _tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file() and not path.is_symlink():
            digest.update(path.relative_to(root).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
    return digest.hexdigest()


def _map_digest(files: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for name, data in sorted(files.items()):
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
