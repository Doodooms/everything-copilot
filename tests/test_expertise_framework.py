import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tomllib
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"


def _agent_source(agent_id: str, skill_id: str) -> str:
    return f"""---
name: {agent_id}
target: vscode
description: "WHAT: Implement the declared demo responsibility. INVOKE FOR: approved demo-pack tasks. DO NOT INVOKE FOR: unrelated work."
user-invocable: false
tools: [read, skill]
---

<routing>
## ACCEPT
- Implement the declared demo responsibility.
## REJECT
- Work outside this role → `orchestrator`.
</routing>

<critical_rules>
- MUST stay within the declared demo responsibility.
- MUST NOT exceed the approved capability projection.
</critical_rules>

<general_rules>
- SHOULD use the declared skill when its method applies.
</general_rules>

<risk_assessment>
Consume the assigned `risk_level`; MUST NOT downgrade it. SHOULD escalate only when new evidence warrants it.
</risk_assessment>

<rules>
## Role
Own the declared demo responsibility.
## Responsibilities
- Use the declared skill for its approved method.
## Constraints
- Stay within the source pack's approved capability projection.
## Output Contract
- Return the implementation evidence and any blockers.
</rules>

<agent-skills>
- MUST load `{skill_id}` for the declared demo method.
</agent-skills>

<workflow>
## Step 1 - Inspect.
1. Consume the assigned `risk_level`, then resolve this agent's `<agent-skills>` policy for the assigned task.
2. Inspect the assigned source and target contract.
## Step 2 - Perform the method.
1. Apply the approved demo method.
## Step 3 - Return the result.
1. Return the defined evidence and remaining uncertainty.
</workflow>
"""


def write_pack(
    root: Path,
    *,
    pack_id: str = "demo-pack",
    pack_type: str = "vertical",
    capability_id: str = "demo.read",
    extra_capabilities: tuple[str, ...] = (),
    dependencies: list[dict[str, str]] | None = None,
    agent_id: str | None = None,
    include_mcp: bool = True,
    include_extension: bool = True,
    version: str = "1.0.0",
) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    agent_id = agent_id or f"{pack_id}-engineer"
    skill_id = f"{pack_id}-skill"
    server_id = f"{pack_id}-tools"
    all_capabilities = [capability_id, *extra_capabilities]
    (root / "agents").mkdir(exist_ok=True)
    (root / "skills" / skill_id).mkdir(parents=True, exist_ok=True)
    (root / "agents" / f"{agent_id}.agent.md").write_text(
        _agent_source(agent_id, skill_id), encoding="utf-8"
    )
    (root / "skills" / skill_id / "SKILL.md").write_text(
        f"---\nname: {skill_id}\ndescription: A local demo skill.\n---\n\n"
        "Use the declared capability locally.\n",
        encoding="utf-8",
    )

    mcp_servers = []
    mcp_config = None
    projection_servers = []
    if include_mcp:
        mcp_config = "mcp.json"
        mcp_servers = [
            {
                "id": server_id,
                "capabilities": [capability_id],
                "permissions": ["fixture.read"],
                "tools": ["search_docs"],
            }
        ]
        projection_servers = [server_id]
        (root / mcp_config).write_text(
            json.dumps(
                {
                    "$schema": MCP_SCHEMA,
                    "mcpServers": {
                        server_id: {
                            "type": "stdio",
                            "command": "demo-tool",
                            "args": ["--read-only"],
                        }
                    },
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    extensions = (
        [{"agent_id": "researcher", "capabilities": all_capabilities}]
        if include_extension
        else []
    )
    projections = [
        {
            "agent_id": agent_id,
            "capabilities": all_capabilities,
            "skills": [skill_id],
            "mcp_servers": projection_servers,
        }
    ]
    if include_extension:
        projections.append(
            {
                "agent_id": "researcher",
                "capabilities": all_capabilities,
                "skills": [skill_id],
                "mcp_servers": projection_servers,
            }
        )

    manifest = {
        "schema_version": 1,
        "id": pack_id,
        "type": pack_type,
        "name": f"{pack_id.replace('-', ' ').title()}",
        "version": version,
        "description": "A generic fixture Expertise Pack.",
        "compatibility": {
            "agent_plugins": ">=1.0",
            "targets": ["portable", "copilot"],
        },
        "trust": {
            "publisher": "fixture-publisher",
            "source": "local-test-fixture",
            "approval_required": True,
        },
        "capabilities": [
            {"id": cap_id, "description": f"Provide {cap_id}."}
            for cap_id in all_capabilities
        ],
        "dependencies": dependencies or [],
        "agents": {
            "contributions": [
                {
                    "id": agent_id,
                    "source": f"agents/{agent_id}.agent.md",
                    "capabilities": all_capabilities,
                }
            ],
            "extensions": extensions,
        },
        "skills": [
            {
                "id": skill_id,
                "path": f"skills/{skill_id}",
                "capabilities": [capability_id],
            }
        ],
        "mcp_config": mcp_config,
        "mcp_servers": mcp_servers,
        "projections": projections,
    }
    (root / "pack.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
    )
    return root


def read_pack_manifest(root: Path):
    return yaml.safe_load((root / "pack.yaml").read_text(encoding="utf-8"))


def write_pack_manifest(root: Path, manifest):
    (root / "pack.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
    )


class ExpertiseFrameworkTests(unittest.TestCase):
    def framework(self):
        expected_modules = (
            "cli.py",
            "errors.py",
            "ir.py",
            "parser.py",
            "registry.py",
            "resolver.py",
            "targets/__init__.py",
        )
        missing = [
            path
            for path in expected_modules
            if not (ROOT / "expertise" / path).is_file()
        ]
        self.assertEqual(
            missing,
            [],
            "the generic Expertise Pack framework is incomplete",
        )
        from expertise.cli import main as cli_main
        from expertise.errors import (
            PackValidationError,
            RegistryError,
            ResolutionError,
            TargetError,
        )
        from expertise.ir import PackReference
        from expertise.parser import parse_pack
        from expertise.registry import LocalPackRegistry
        from expertise.resolver import resolve_effective_ir
        from expertise.targets import compile_target, materialize_target

        fixture_agents = frozenset(
            {
                "architect",
                "challenger",
                "devops",
                "implementer",
                "orchestrator",
                "planner",
                "quality-assurance",
                "researcher",
                "reviewer",
            }
        )

        def parse_with_catalog(*args, **kwargs):
            kwargs.setdefault("known_agents", fixture_agents)
            return parse_pack(*args, **kwargs)

        def registry_with_catalog(*args, **kwargs):
            kwargs.setdefault("known_agents", fixture_agents)
            return LocalPackRegistry(*args, **kwargs)

        return {
            "PackValidationError": PackValidationError,
            "RegistryError": RegistryError,
            "ResolutionError": ResolutionError,
            "TargetError": TargetError,
            "PackReference": PackReference,
            "parse_pack": parse_with_catalog,
            "LocalPackRegistry": registry_with_catalog,
            "resolve_effective_ir": resolve_effective_ir,
            "compile_target": compile_target,
            "materialize_target": materialize_target,
            "cli_main": cli_main,
        }

    def test_pack_schema_declares_the_strict_source_manifest_fields(self):
        self.framework()
        from expertise.ontology import (
            AGENT_PLUGINS_REQUIREMENT_PATTERN,
            CAPABILITY_ID_PATTERN,
            COMPONENT_ID_PATTERN,
            RELATIVE_PATH_PATTERN,
            VERSION_PATTERN,
        )

        schema = json.loads(
            (ROOT / "expertise/schemas/pack.schema.json").read_text(encoding="utf-8")
        )
        expected = {
            "schema_version",
            "id",
            "type",
            "name",
            "version",
            "description",
            "compatibility",
            "trust",
            "capabilities",
            "dependencies",
            "agents",
            "skills",
            "mcp_config",
            "mcp_servers",
            "projections",
        }

        self.assertEqual(set(schema["required"]), expected)
        self.assertEqual(set(schema["properties"]), expected)
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["properties"]["schema_version"]["const"], 1)
        self.assertEqual(
            schema["properties"]["type"]["enum"],
            ["horizontal", "vertical"],
        )
        self.assertEqual(schema["$defs"]["packId"]["maxLength"], 64)
        self.assertEqual(
            schema["$defs"]["componentId"]["pattern"],
            COMPONENT_ID_PATTERN.pattern,
        )
        self.assertEqual(
            schema["$defs"]["capabilityId"]["pattern"],
            CAPABILITY_ID_PATTERN.pattern,
        )
        self.assertEqual(schema["$defs"]["version"]["pattern"], VERSION_PATTERN.pattern)
        self.assertEqual(
            schema["$defs"]["relativePath"]["pattern"],
            RELATIVE_PATH_PATTERN.pattern,
        )
        self.assertEqual(
            schema["properties"]["compatibility"]["required"],
            ["targets", "agent_plugins"],
        )
        self.assertEqual(
            schema["properties"]["compatibility"]["properties"]["agent_plugins"][
                "$ref"
            ],
            "#/$defs/agentPluginsRequirement",
        )
        self.assertEqual(
            schema["$defs"]["agentPluginsRequirement"]["pattern"],
            AGENT_PLUGINS_REQUIREMENT_PATTERN.pattern,
        )

    def test_pack_id_length_matches_plugin_name_limit(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            id_64 = "a" * 64
            valid_source = api["parse_pack"](write_pack(root / "id-64", pack_id=id_64))
            artifact = api["compile_target"](valid_source, "portable")
            plugin = json.loads(artifact.files["plugin.json"])
            self.assertEqual(len(plugin["name"]), 64)

            source_root = write_pack(root / "id-65", pack_id="a" * 65)
            with self.assertRaises(api["PackValidationError"]) as error:
                api["parse_pack"](source_root)
            self.assertIn("at most 64 characters", str(error.exception))

    def test_agent_plugins_minimum_range_normalization_and_target_support(self):
        api = self.framework()
        from expertise.ontology import AGENT_PLUGINS_VERSION

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index, requirement in enumerate((">=1.0", ">=1.0.0")):
                with self.subTest(requirement=requirement):
                    source_root = write_pack(root / f"supported-{index}")
                    manifest = read_pack_manifest(source_root)
                    manifest["compatibility"]["agent_plugins"] = requirement
                    write_pack_manifest(source_root, manifest)
                    source = api["parse_pack"](source_root)

                    self.assertEqual(source.ir.compatibility.agent_plugins, ">=1.0.0")
                    api["compile_target"](source, "portable")
                    api["compile_target"](source, "copilot")

            for index, requirement in enumerate((">=1.0.1", ">=99.0.0")):
                with self.subTest(requirement=requirement):
                    source_root = write_pack(root / f"unsupported-{index}")
                    manifest = read_pack_manifest(source_root)
                    manifest["compatibility"]["agent_plugins"] = requirement
                    write_pack_manifest(source_root, manifest)
                    source = api["parse_pack"](source_root)
                    self.assertEqual(source.ir.compatibility.agent_plugins, requirement)
                    for target in ("portable", "copilot"):
                        with self.subTest(target=target):
                            with self.assertRaisesRegex(
                                api["TargetError"],
                                f"target supports {AGENT_PLUGINS_VERSION}",
                            ):
                                api["compile_target"](source, target)

            malformed_requirements = (
                ">1.0",
                "~1.0",
                ">=01.0",
                ">=1.0.0.0",
                " >=1.0",
                ">=1.0 ",
                ">=1.0\n",
            )
            for index, requirement in enumerate(malformed_requirements):
                with self.subTest(malformed=requirement):
                    source_root = write_pack(root / f"malformed-{index}")
                    manifest = read_pack_manifest(source_root)
                    manifest["compatibility"]["agent_plugins"] = requirement
                    write_pack_manifest(source_root, manifest)
                    with self.assertRaises(api["PackValidationError"]) as error:
                        api["parse_pack"](source_root)
                    self.assertLessEqual(len(error.exception.diagnostics), 50)
                    self.assertIn("lower-bound constraint", str(error.exception))

    def test_component_ids_are_hyphen_only_and_capabilities_allow_dotted_ids(self):
        api = self.framework()
        invalid_ids = (
            (
                "agent-component",
                "demo.pack-engineer",
                lambda manifest, identifier: manifest["agents"]["contributions"][
                    0
                ].update(id=identifier),
            ),
            (
                "extension-component",
                "researcher.tool",
                lambda manifest, identifier: manifest["agents"]["extensions"][0].update(
                    agent_id=identifier
                ),
            ),
            (
                "skill-component",
                "demo.pack-skill",
                lambda manifest, identifier: manifest["skills"][0].update(
                    id=identifier
                ),
            ),
            (
                "mcp-component",
                "demo.pack-tools",
                lambda manifest, identifier: manifest["mcp_servers"][0].update(
                    id=identifier
                ),
            ),
            (
                "projection-agent",
                "demo.pack-engineer",
                lambda manifest, identifier: manifest["projections"][0].update(
                    agent_id=identifier
                ),
            ),
            (
                "projection-skill",
                "demo.pack-skill",
                lambda manifest, identifier: manifest["projections"][0].update(
                    skills=[identifier]
                ),
            ),
            (
                "projection-mcp",
                "demo.pack-tools",
                lambda manifest, identifier: manifest["projections"][0].update(
                    mcp_servers=[identifier]
                ),
            ),
        )
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            dotted_capability = api["parse_pack"](
                write_pack(
                    base / "dotted-capability",
                    capability_id="ml.dataset.inspect",
                    extra_capabilities=("ml.metrics.compare",),
                )
            )
            self.assertEqual(
                {item.id for item in dotted_capability.ir.capabilities},
                {"ml.dataset.inspect", "ml.metrics.compare"},
            )

            for case, identifier, mutate in invalid_ids:
                with self.subTest(case=case):
                    source_root = write_pack(base / case)
                    manifest = read_pack_manifest(source_root)
                    mutate(manifest, identifier)
                    write_pack_manifest(source_root, manifest)

                    with self.assertRaises(api["PackValidationError"]) as error:
                        api["parse_pack"](source_root)

                    self.assertIn(
                        f"invalid identifier {identifier!r}", str(error.exception)
                    )

    def test_duplicate_yaml_keys_and_invalid_schema_values_fail_deterministically(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            duplicate_root = write_pack(Path(directory) / "duplicate-yaml-key")
            manifest_path = duplicate_root / "pack.yaml"
            manifest_path.write_text(
                manifest_path.read_text(encoding="utf-8") + "\nid: duplicate\n",
                encoding="utf-8",
            )
            with self.assertRaises(api["PackValidationError"]) as duplicate_error:
                api["parse_pack"](duplicate_root)
            self.assertIn("duplicate key 'id'", str(duplicate_error.exception))

            invalid_values = (
                (
                    "bad-version",
                    lambda manifest: manifest.update(version="01.0.0"),
                    "semantic version",
                ),
                (
                    "bad-prerelease",
                    lambda manifest: manifest.update(version="1.0.0-alpha..1"),
                    "semantic version",
                ),
                (
                    "duplicate-target",
                    lambda manifest: manifest["compatibility"].update(
                        targets=["portable", "portable"]
                    ),
                    "duplicate value",
                ),
                (
                    "bad-target",
                    lambda manifest: manifest["compatibility"].update(
                        targets=["unknown"]
                    ),
                    "unsupported target",
                ),
                (
                    "approval-not-required",
                    lambda manifest: manifest["trust"].update(approval_required=False),
                    "approval_required: must be true",
                ),
                (
                    "bad-digest",
                    lambda manifest: manifest["trust"].update(
                        digest="sha256:" + ("A" * 64)
                    ),
                    "lowercase sha256 digest",
                ),
            )
            for name, mutate, expected in invalid_values:
                with self.subTest(name=name):
                    source_root = write_pack(Path(directory) / name)
                    manifest = read_pack_manifest(source_root)
                    mutate(manifest)
                    write_pack_manifest(source_root, manifest)

                    with self.assertRaises(api["PackValidationError"]) as first:
                        api["parse_pack"](source_root)
                    with self.assertRaises(api["PackValidationError"]) as second:
                        api["parse_pack"](source_root)

                    self.assertIn(expected, str(first.exception))
                    self.assertEqual(
                        first.exception.diagnostics, second.exception.diagnostics
                    )

    def test_valid_pack_normalizes_into_a_deeply_immutable_deterministic_ir(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            first_root = write_pack(Path(directory) / "first")
            second_root = Path(directory) / "second"
            shutil.copytree(first_root, second_root)

            first = api["parse_pack"](first_root)
            second = api["parse_pack"](second_root)

        self.assertEqual(first.ir.id, "demo-pack")
        self.assertEqual(first.ir.version, "1.0.0")
        self.assertEqual(first.ir.capabilities[0].id, "demo.read")
        self.assertEqual(first.ir.fingerprint, second.ir.fingerprint)
        self.assertEqual(first.ir.content_digest, second.ir.content_digest)
        with self.assertRaises((AttributeError, TypeError)):
            first.ir.capabilities[0].id = "changed"

    def test_rejects_unknown_schema_fields_duplicate_capabilities_and_bad_references(
        self,
    ):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            unknown_root = write_pack(Path(directory) / "unknown")
            unknown_manifest = yaml.safe_load(
                (unknown_root / "pack.yaml").read_text(encoding="utf-8")
            )
            unknown_manifest["unexpected"] = True
            (unknown_root / "pack.yaml").write_text(
                yaml.safe_dump(unknown_manifest, sort_keys=False), encoding="utf-8"
            )
            with self.assertRaises(api["PackValidationError"]) as unknown_error:
                api["parse_pack"](unknown_root)
            self.assertIn("unexpected", str(unknown_error.exception))

            duplicate_root = write_pack(Path(directory) / "duplicate")
            duplicate_manifest = yaml.safe_load(
                (duplicate_root / "pack.yaml").read_text(encoding="utf-8")
            )
            duplicate_manifest["capabilities"].append(
                dict(duplicate_manifest["capabilities"][0])
            )
            (duplicate_root / "pack.yaml").write_text(
                yaml.safe_dump(duplicate_manifest, sort_keys=False), encoding="utf-8"
            )
            with self.assertRaises(api["PackValidationError"]) as duplicate_error:
                api["parse_pack"](duplicate_root)
            self.assertIn("duplicate", str(duplicate_error.exception).lower())

            bad_reference_root = write_pack(Path(directory) / "bad-reference")
            bad_reference_manifest = yaml.safe_load(
                (bad_reference_root / "pack.yaml").read_text(encoding="utf-8")
            )
            bad_reference_manifest["projections"][0]["skills"] = ["missing-skill"]
            (bad_reference_root / "pack.yaml").write_text(
                yaml.safe_dump(bad_reference_manifest, sort_keys=False),
                encoding="utf-8",
            )
            with self.assertRaises(api["PackValidationError"]) as reference_error:
                api["parse_pack"](bad_reference_root)
            self.assertIn("missing-skill", str(reference_error.exception))

            unknown_capability_root = write_pack(Path(directory) / "unknown-capability")
            unknown_capability_manifest = yaml.safe_load(
                (unknown_capability_root / "pack.yaml").read_text(encoding="utf-8")
            )
            unknown_capability_manifest["projections"][0]["capabilities"] = [
                "missing.capability"
            ]
            (unknown_capability_root / "pack.yaml").write_text(
                yaml.safe_dump(unknown_capability_manifest, sort_keys=False),
                encoding="utf-8",
            )
            with self.assertRaises(api["PackValidationError"]) as capability_error:
                api["parse_pack"](unknown_capability_root)
            self.assertIn("missing.capability", str(capability_error.exception))

    def test_rejects_malformed_yaml_and_known_agent_id_collisions(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            malformed_root = write_pack(Path(directory) / "malformed")
            (malformed_root / "pack.yaml").write_text(
                "schema_version: [\n", encoding="utf-8"
            )
            with self.assertRaises(api["PackValidationError"]) as malformed_error:
                api["parse_pack"](malformed_root)
            self.assertIn("cannot parse", str(malformed_error.exception))

            duplicate_agent_root = write_pack(
                Path(directory) / "duplicate-agent",
                agent_id="researcher",
                include_extension=False,
            )
            with self.assertRaises(api["PackValidationError"]) as agent_error:
                api["parse_pack"](duplicate_agent_root)
            self.assertIn("duplicates known agent", str(agent_error.exception))

    def test_invalid_utf8_skill_frontmatter_is_a_structured_cli_error(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            source_root = write_pack(repo / "expertise/packs/demo-pack")
            skill_file = source_root / "skills/demo-pack-skill/SKILL.md"
            skill_file.write_bytes(skill_file.read_bytes() + b"\xff")

            with self.assertRaises(api["PackValidationError"]) as parse_error:
                api["parse_pack"](source_root)
            self.assertLessEqual(len(parse_error.exception.diagnostics), 50)
            self.assertIn("valid UTF-8", str(parse_error.exception))

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = api["cli_main"](
                    ["validate", "demo-pack", "--known-agent", "researcher"],
                    repo_root=repo,
                )

        self.assertEqual(result, 2)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["error"], "PackValidationError")
        self.assertIn("valid UTF-8", payload["message"])
        self.assertTrue(payload["diagnostics"])

    def test_rejects_mcp_configuration_outside_the_official_schema(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            source_root = write_pack(Path(directory) / "bad-mcp")
            config_path = source_root / "mcp.json"
            mcp = json.loads(config_path.read_text(encoding="utf-8"))
            mcp["unexpected"] = True
            config_path.write_text(json.dumps(mcp), encoding="utf-8")

            with self.assertRaises(api["PackValidationError"]) as mcp_error:
                api["parse_pack"](source_root)

        self.assertIn("unknown MCP configuration field", str(mcp_error.exception))

    def test_pack_parser_rejects_explicit_null_mcp_headers(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            source_root = write_pack(Path(directory) / "null-headers")
            mcp_path = source_root / "mcp.json"
            mcp = json.loads(mcp_path.read_text(encoding="utf-8"))
            mcp["mcpServers"]["demo-pack-tools"] = {
                "type": "streamable-http",
                "url": "https://example.test/mcp",
                "headers": None,
            }
            mcp_path.write_text(json.dumps(mcp), encoding="utf-8")

            with self.assertRaises(api["PackValidationError"]) as error:
                api["parse_pack"](source_root)

        self.assertIn("headers", str(error.exception))

    def test_pack_mcp_tool_catalog_is_validated_and_roundtripped(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            source_root = write_pack(Path(directory) / "mcp-tool-catalog")
            source = api["parse_pack"](source_root)
            self.assertEqual(source.ir.mcp_servers[0].tools, ("search_docs",))
            self.assertEqual(
                source.ir.as_dict()["mcp_servers"][0]["tools"], ["search_docs"]
            )

            manifest = read_pack_manifest(source_root)
            manifest["mcp_servers"][0]["tools"] = ["search/docs"]
            write_pack_manifest(source_root, manifest)
            with self.assertRaises(api["PackValidationError"]) as error:
                api["parse_pack"](source_root)

        self.assertIn("mcp_servers", str(error.exception))
        self.assertIn("tools", str(error.exception))

    def test_mcp_json_duplicate_keys_are_rejected_at_root_and_nested_levels(self):
        api = self.framework()
        duplicate_documents = (
            (
                "duplicate-root",
                f'{{"$schema":"{MCP_SCHEMA}","$schema":"{MCP_SCHEMA}",'
                '"mcpServers":{"demo-pack-tools":{"type":"stdio","command":"demo-tool"}}}',
            ),
            (
                "duplicate-server-field",
                f'{{"$schema":"{MCP_SCHEMA}","mcpServers":'
                '{"demo-pack-tools":{"type":"stdio","command":"first",'
                '"command":"second"}}}',
            ),
        )
        with tempfile.TemporaryDirectory() as directory:
            for case, contents in duplicate_documents:
                with self.subTest(case=case):
                    source_root = write_pack(Path(directory) / case)
                    (source_root / "mcp.json").write_text(contents, encoding="utf-8")

                    with self.assertRaises(api["PackValidationError"]) as error:
                        api["parse_pack"](source_root)

                    self.assertIn("duplicate JSON key", str(error.exception))
                    self.assertLessEqual(len(error.exception.diagnostics), 50)

    def test_valid_trust_metadata_is_preserved_in_the_normalized_ir(self):
        api = self.framework()
        digest = "sha256:" + ("a" * 64)
        with tempfile.TemporaryDirectory() as directory:
            source_root = write_pack(Path(directory) / "trusted")
            manifest = read_pack_manifest(source_root)
            manifest["trust"].update(
                publisher="trusted-publisher",
                source="approved-local-source",
                digest=digest,
                approval_required=True,
            )
            write_pack_manifest(source_root, manifest)

            source = api["parse_pack"](source_root)

        self.assertEqual(source.ir.trust.publisher, "trusted-publisher")
        self.assertEqual(source.ir.trust.source, "approved-local-source")
        self.assertTrue(source.ir.trust.approval_required)
        self.assertEqual(source.ir.trust.digest, digest)

    def test_registry_rejects_duplicate_sources_and_multiple_active_versions(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            version_one = api["parse_pack"](
                write_pack(root / "version-one", version="1.0.0")
            )
            with self.assertRaisesRegex(
                api["RegistryError"], "duplicate local pack source"
            ):
                api["LocalPackRegistry"]([version_one, version_one])

            version_two = api["parse_pack"](
                write_pack(root / "version-two", version="2.0.0")
            )
            registry = api["LocalPackRegistry"]([version_one, version_two])
            references = [version_one.ir.reference, version_two.ir.reference]

            with self.assertRaisesRegex(
                api["ResolutionError"], "multiple active versions"
            ):
                api["resolve_effective_ir"](
                    registry,
                    ["demo.read"],
                    installed_pack_refs=references,
                    active_pack_refs=references,
                    approved_pack_refs=references,
                    agent_ids=["demo-pack-engineer"],
                )

            shared_agent_packs = [
                api["parse_pack"](
                    write_pack(
                        root / "shared-one",
                        pack_id="shared-one",
                        capability_id="shared.one",
                        agent_id="shared-engineer",
                        include_extension=False,
                    )
                ),
                api["parse_pack"](
                    write_pack(
                        root / "shared-two",
                        pack_id="shared-two",
                        capability_id="shared.two",
                        agent_id="shared-engineer",
                        include_extension=False,
                    )
                ),
            ]
            shared_registry = api["LocalPackRegistry"](shared_agent_packs)
            shared_references = [item.ir.reference for item in shared_agent_packs]
            with self.assertRaisesRegex(
                api["ResolutionError"], "duplicate visible agent IDs"
            ):
                api["resolve_effective_ir"](
                    shared_registry,
                    [],
                    installed_pack_refs=shared_references,
                    active_pack_refs=shared_references,
                    approved_pack_refs=shared_references,
                )

    def test_dependency_resolution_enforces_active_providers_and_version_bounds(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            consumer = api["parse_pack"](
                write_pack(
                    root / "consumer",
                    pack_id="consumer-pack",
                    capability_id="consumer.call",
                    dependencies=[
                        {
                            "capability": "ml.dataset.inspect",
                            "pack_id": "provider-pack",
                            "minimum_version": "1.2.0",
                        }
                    ],
                )
            )

            for version in ("1.1.9", "1.2.0-rc.1"):
                with self.subTest(version=version):
                    provider = api["parse_pack"](
                        write_pack(
                            root / f"provider-{version}",
                            pack_id="provider-pack",
                            capability_id="ml.dataset.inspect",
                            version=version,
                        )
                    )
                    registry = api["LocalPackRegistry"]([consumer, provider])
                    references = [consumer.ir.reference, provider.ir.reference]
                    with self.assertRaisesRegex(
                        api["ResolutionError"],
                        "not provided by an installed, active, approved pack",
                    ):
                        api["resolve_effective_ir"](
                            registry,
                            ["consumer.call"],
                            installed_pack_refs=references,
                            active_pack_refs=references,
                            approved_pack_refs=references,
                            agent_ids=["consumer-pack-engineer"],
                        )

            provider = api["parse_pack"](
                write_pack(
                    root / "provider-minimum",
                    pack_id="provider-pack",
                    capability_id="ml.dataset.inspect",
                    version="1.2.0+fixture.1",
                )
            )
            registry = api["LocalPackRegistry"]([consumer, provider])
            references = [consumer.ir.reference, provider.ir.reference]

            with self.assertRaisesRegex(
                api["ResolutionError"],
                "not provided by an installed, active, approved pack",
            ):
                api["resolve_effective_ir"](
                    registry,
                    ["consumer.call"],
                    installed_pack_refs=references,
                    active_pack_refs=[consumer.ir.reference],
                    approved_pack_refs=references,
                    agent_ids=["consumer-pack-engineer"],
                )

            effective = api["resolve_effective_ir"](
                registry,
                ["consumer.call"],
                installed_pack_refs=references,
                active_pack_refs=references,
                approved_pack_refs=references,
                agent_ids=["consumer-pack-engineer"],
            )

        self.assertEqual(
            {reference.id for reference in effective.packs},
            {"consumer-pack", "provider-pack"},
        )
        self.assertIn("consumer.call", effective.capabilities)
        self.assertIn("ml.dataset.inspect", effective.capabilities)

    def test_default_deny_projection_hides_ungranted_capabilities_and_inactive_packs(
        self,
    ):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            source_root = write_pack(
                Path(directory) / "demo",
                extra_capabilities=("demo.private",),
            )
            manifest = read_pack_manifest(source_root)
            for projection in manifest["projections"]:
                projection["capabilities"] = ["demo.read"]
            write_pack_manifest(source_root, manifest)
            source = api["parse_pack"](source_root)
            reference = source.ir.reference
            registry = api["LocalPackRegistry"]([source])

            with self.assertRaisesRegex(
                api["ResolutionError"], "agent_ids must contain non-empty strings"
            ):
                api["resolve_effective_ir"](
                    registry,
                    [],
                    installed_pack_refs=[reference],
                    active_pack_refs=[],
                    approved_pack_refs=[reference],
                    agent_ids=[[]],
                )

            core_only = api["resolve_effective_ir"](
                registry,
                [],
                installed_pack_refs=[reference],
                active_pack_refs=[],
                approved_pack_refs=[reference],
            )
            active = api["resolve_effective_ir"](
                registry,
                ["demo.read"],
                installed_pack_refs=[reference],
                active_pack_refs=[reference],
                approved_pack_refs=[reference],
                agent_ids=["demo-pack-engineer", "researcher", "reviewer"],
            )

        self.assertEqual(core_only.packs, ())
        self.assertEqual(core_only.capabilities, ())
        self.assertEqual(
            {projection.agent_id for projection in core_only.agent_projections},
            set(registry.agent_ids),
        )
        self.assertTrue(
            all(
                not projection.capabilities
                and not projection.skills
                and not projection.mcp_servers
                for projection in core_only.agent_projections
            )
        )

        projections = {item.agent_id: item for item in active.agent_projections}
        self.assertIn("demo.private", active.capabilities)
        for projection in projections.values():
            self.assertNotIn("demo.private", projection.capabilities)
        self.assertEqual(projections["demo-pack-engineer"].capabilities, ("demo.read",))
        self.assertEqual(projections["reviewer"].capabilities, ())
        self.assertEqual(projections["reviewer"].skills, ())
        self.assertEqual(projections["reviewer"].mcp_servers, ())

    def test_target_validators_enforce_official_plugin_and_mcp_1_0_constraints(self):
        api = self.framework()
        from expertise.targets.validation import (
            validate_mcp_manifest,
            validate_plugin_manifest,
        )

        with tempfile.TemporaryDirectory() as directory:
            source = api["parse_pack"](write_pack(Path(directory) / "demo"))
            artifact = api["compile_target"](source, "portable")

        plugin_manifest = json.loads(artifact.files["plugin.json"])
        mcp_manifest = json.loads(artifact.files["mcp.json"])
        validate_plugin_manifest(plugin_manifest)
        validate_mcp_manifest(mcp_manifest)
        self.assertEqual(plugin_manifest["$schema"], PLUGIN_SCHEMA)
        self.assertEqual(mcp_manifest["$schema"], MCP_SCHEMA)

        valid_plugin = {
            "$schema": PLUGIN_SCHEMA,
            "name": "demo-pack",
            "version": "1.0.0",
            "description": "Fixture plugin.",
            "author": {"name": "fixture-publisher"},
            "keywords": ["demo"],
            "extensions": {"com.example.fixture": {"enabled": True}},
        }
        validate_plugin_manifest(valid_plugin)
        for invalid_name in ("demo..pack", "demo--pack", "x" * 65):
            with self.subTest(plugin_name=invalid_name):
                invalid_plugin = dict(valid_plugin, name=invalid_name)
                with self.assertRaises(api["TargetError"]):
                    validate_plugin_manifest(invalid_plugin)

        valid_mcp = {
            "$schema": MCP_SCHEMA,
            "mcpServers": {
                "stdio": {
                    "type": "stdio",
                    "command": "demo-tool",
                    "args": ["--read-only"],
                    "env": {"DEMO_MODE": "read-only"},
                    "cwd": "${PLUGIN_ROOT}/bin",
                },
                "stdio-relative": {
                    "type": "stdio",
                    "command": "demo-tool",
                    "cwd": "./workspace/bin",
                },
                "stdio-data": {
                    "type": "stdio",
                    "command": "demo-tool",
                    "cwd": "${PLUGIN_DATA}/cache",
                },
                "streamable": {
                    "type": "streamable-http",
                    "url": "https://example.test/mcp",
                    "headers": {"Accept": "application/json"},
                },
                "legacy-sse": {
                    "type": "sse",
                    "url": "https://example.test/events",
                },
            },
        }
        validate_mcp_manifest(valid_mcp)
        invalid_mcp = {
            "$schema": MCP_SCHEMA,
            "mcpServers": {
                "stdio": {
                    "type": "stdio",
                    "command": "demo-tool",
                    "env": {"PLUGIN_ROOT": "/outside"},
                }
            },
        }
        with self.assertRaises(api["TargetError"]):
            validate_mcp_manifest(invalid_mcp)

        null_headers = {
            "$schema": MCP_SCHEMA,
            "mcpServers": {
                "http": {
                    "type": "streamable-http",
                    "url": "https://example.test/mcp",
                    "headers": None,
                }
            },
        }
        with self.assertRaisesRegex(api["TargetError"], "headers"):
            validate_mcp_manifest(null_headers)

    def test_mcp_cwd_rejects_windows_traversal_in_source_and_target_validation(self):
        api = self.framework()
        from expertise.targets.validation import validate_mcp_manifest

        invalid_cwds = (
            r"./nested\..\..\outside",
            "./nested/.. /.. /outside",
        )
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            for index, invalid_cwd in enumerate(invalid_cwds):
                with self.subTest(cwd=invalid_cwd):
                    invalid_mcp = {
                        "$schema": MCP_SCHEMA,
                        "mcpServers": {
                            "stdio": {
                                "type": "stdio",
                                "command": "demo-tool",
                                "cwd": invalid_cwd,
                            }
                        },
                    }
                    with self.assertRaisesRegex(api["TargetError"], "cwd"):
                        validate_mcp_manifest(invalid_mcp)

                    source_root = write_pack(base / f"bad-cwd-{index}")
                    mcp_path = source_root / "mcp.json"
                    mcp = json.loads(mcp_path.read_text(encoding="utf-8"))
                    mcp["mcpServers"]["demo-pack-tools"]["cwd"] = invalid_cwd
                    mcp_path.write_text(json.dumps(mcp), encoding="utf-8")

                    with self.assertRaises(api["PackValidationError"]) as error:
                        api["parse_pack"](source_root)
                    self.assertIn("cwd", str(error.exception))

    def test_rejects_missing_files_path_traversal_and_symlink_escape(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)

            missing_root = write_pack(base / "missing")
            (missing_root / "skills/demo-pack-skill/SKILL.md").unlink()
            with self.assertRaises(api["PackValidationError"]) as missing_error:
                api["parse_pack"](missing_root)
            self.assertIn("SKILL.md", str(missing_error.exception))

            traversal_root = write_pack(base / "traversal")
            traversal_manifest = yaml.safe_load(
                (traversal_root / "pack.yaml").read_text(encoding="utf-8")
            )
            traversal_manifest["skills"][0]["path"] = "../outside-skill"
            (traversal_root / "pack.yaml").write_text(
                yaml.safe_dump(traversal_manifest, sort_keys=False), encoding="utf-8"
            )
            with self.assertRaises(api["PackValidationError"]) as traversal_error:
                api["parse_pack"](traversal_root)
            self.assertIn("relative", str(traversal_error.exception).lower())

            for index, unsafe_path in enumerate(
                (
                    "skills/./demo-pack-skill",
                    "skills//demo-pack-skill",
                    "skills/demo-pack-skill/",
                )
            ):
                with self.subTest(unsafe_path=unsafe_path):
                    source_root = write_pack(base / f"noncanonical-{index}")
                    manifest = read_pack_manifest(source_root)
                    manifest["skills"][0]["path"] = unsafe_path
                    write_pack_manifest(source_root, manifest)
                    with self.assertRaises(api["PackValidationError"]) as error:
                        api["parse_pack"](source_root)
                    self.assertIn("safe pack-root-relative path", str(error.exception))

            symlink_root = write_pack(base / "symlink")
            outside_skill = base / "outside-skill"
            outside_skill.mkdir()
            (outside_skill / "SKILL.md").write_text(
                "---\nname: demo-pack-skill\ndescription: outside\n---\n",
                encoding="utf-8",
            )
            (symlink_root / "skills/demo-pack-skill/SKILL.md").unlink()
            (symlink_root / "skills/demo-pack-skill").rmdir()
            (symlink_root / "skills/demo-pack-skill").symlink_to(
                outside_skill, target_is_directory=True
            )
            with self.assertRaises(api["PackValidationError"]) as symlink_error:
                api["parse_pack"](symlink_root)
            self.assertIn("symlink", str(symlink_error.exception).lower())

    def test_pack_registry_and_resolver_are_explicit_approved_and_default_deny(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            source = api["parse_pack"](write_pack(Path(directory) / "demo"))
            registry = api["LocalPackRegistry"]([source])
            reference = api["PackReference"](source.ir.id, source.ir.version)

            with self.assertRaises(api["ResolutionError"]):
                api["resolve_effective_ir"](
                    registry,
                    ["demo.read"],
                    installed_pack_refs=[],
                    active_pack_refs=[],
                    approved_pack_refs=[],
                    agent_ids=["demo-pack-engineer"],
                )

            with self.assertRaisesRegex(api["ResolutionError"], "not approved"):
                api["resolve_effective_ir"](
                    registry,
                    ["demo.read"],
                    installed_pack_refs=[reference],
                    active_pack_refs=[reference],
                    approved_pack_refs=[],
                    agent_ids=["demo-pack-engineer"],
                )
            with self.assertRaisesRegex(api["ResolutionError"], "not installed"):
                api["resolve_effective_ir"](
                    registry,
                    ["demo.read"],
                    installed_pack_refs=[],
                    active_pack_refs=[reference],
                    approved_pack_refs=[reference],
                    agent_ids=["demo-pack-engineer"],
                )
            with self.assertRaisesRegex(api["ResolutionError"], "Active Set"):
                api["resolve_effective_ir"](
                    registry,
                    ["demo.read"],
                    installed_pack_refs=[reference],
                    active_pack_refs=[],
                    approved_pack_refs=[reference],
                    agent_ids=["demo-pack-engineer"],
                )

            resolved = api["resolve_effective_ir"](
                registry,
                ["demo.read"],
                installed_pack_refs=[reference],
                active_pack_refs=[reference],
                approved_pack_refs=[reference],
                agent_ids=["demo-pack-engineer", "researcher", "reviewer"],
            )

        projections = {item.agent_id: item for item in resolved.agent_projections}
        self.assertEqual(resolved.capabilities, ("demo.read",))
        self.assertEqual(projections["demo-pack-engineer"].skills, ("demo-pack-skill",))
        self.assertEqual(projections["researcher"].mcp_servers, ("demo-pack-tools",))
        self.assertEqual(projections["reviewer"].capabilities, ())
        self.assertEqual(projections["reviewer"].skills, ())
        self.assertEqual(projections["reviewer"].mcp_servers, ())

    def test_explicit_agent_catalog_resolves_and_compiles_without_core_tree(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "workspace"
            workspace.mkdir()
            source_root = write_pack(workspace / "packs/demo-pack")
            manifest = read_pack_manifest(source_root)
            manifest["compatibility"]["targets"] = ["portable", "copilot", "codex"]
            write_pack_manifest(source_root, manifest)
            shutil.copytree(
                ROOT / "expertise",
                workspace / "expertise",
                ignore=shutil.ignore_patterns("__pycache__"),
            )

            child_environment = os.environ.copy()
            child_environment.pop("PYTHONPATH", None)
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    """
import json
from pathlib import Path
from expertise.parser import parse_pack
from expertise.registry import LocalPackRegistry
from expertise.resolver import resolve_effective_ir
from expertise.targets import compile_target

source = parse_pack(Path('packs/demo-pack'), known_agents={'researcher'})
registry = LocalPackRegistry([source], known_agents={'researcher'})
reference = source.reference
effective = resolve_effective_ir(
    registry,
    ['demo.read'],
    installed_pack_refs=[reference],
    active_pack_refs=[reference],
    approved_pack_refs=[reference],
)
artifacts = {
    target: compile_target(source, target)
    for target in ('portable', 'copilot', 'codex')
}
print(json.dumps({
    'agents': [projection.agent_id for projection in effective.agent_projections],
    'targets': {target: len(artifact.files) for target, artifact in artifacts.items()},
}))
""",
                ],
                cwd=workspace,
                env=child_environment,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("demo-pack-engineer", payload["agents"])
        self.assertIn("researcher", payload["agents"])
        self.assertEqual(set(payload["targets"]), {"portable", "copilot", "codex"})
        self.assertTrue(all(count > 0 for count in payload["targets"].values()))

    def test_active_pack_projection_is_static_not_filtered_per_task_capability(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            source = api["parse_pack"](
                write_pack(
                    Path(directory) / "demo",
                    extra_capabilities=("demo.extra",),
                )
            )
            reference = source.ir.reference
            registry = api["LocalPackRegistry"]([source])
            effective = api["resolve_effective_ir"](
                registry,
                ["demo.read"],
                installed_pack_refs=[reference],
                active_pack_refs=[reference],
                approved_pack_refs=[reference],
                agent_ids=["researcher"],
            )

        projection = effective.agent_projections[0]
        self.assertEqual(effective.capabilities, ("demo.extra", "demo.read"))
        self.assertEqual(projection.capabilities, ("demo.extra", "demo.read"))
        self.assertEqual(projection.skills, ("demo-pack-skill",))

    def test_resolver_rejects_ambiguous_providers_and_dependency_cycles(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = api["parse_pack"](
                write_pack(
                    root / "first", pack_id="first-pack", capability_id="shared.cap"
                )
            )
            second = api["parse_pack"](
                write_pack(
                    root / "second", pack_id="second-pack", capability_id="shared.cap"
                )
            )
            registry = api["LocalPackRegistry"]([first, second])
            references = [
                api["PackReference"](first.ir.id, first.ir.version),
                api["PackReference"](second.ir.id, second.ir.version),
            ]
            with self.assertRaisesRegex(api["ResolutionError"], "ambiguous"):
                api["resolve_effective_ir"](
                    registry,
                    ["shared.cap"],
                    installed_pack_refs=references,
                    active_pack_refs=references,
                    approved_pack_refs=references,
                    agent_ids=["researcher"],
                )

            cyclic_a = api["parse_pack"](
                write_pack(
                    root / "cycle-a",
                    pack_id="cycle-a",
                    capability_id="cycle.a",
                    dependencies=[{"capability": "cycle.b", "pack_id": "cycle-b"}],
                )
            )
            cyclic_b = api["parse_pack"](
                write_pack(
                    root / "cycle-b",
                    pack_id="cycle-b",
                    capability_id="cycle.b",
                    dependencies=[{"capability": "cycle.a", "pack_id": "cycle-a"}],
                )
            )
            cyclic_registry = api["LocalPackRegistry"]([cyclic_a, cyclic_b])
            cyclic_references = [
                api["PackReference"](cyclic_a.ir.id, cyclic_a.ir.version),
                api["PackReference"](cyclic_b.ir.id, cyclic_b.ir.version),
            ]
            with self.assertRaisesRegex(api["ResolutionError"], "cycle"):
                api["resolve_effective_ir"](
                    cyclic_registry,
                    ["cycle.a"],
                    installed_pack_refs=cyclic_references,
                    active_pack_refs=cyclic_references,
                    approved_pack_refs=cyclic_references,
                    agent_ids=["cycle-a-engineer"],
                )

    def test_targets_reject_post_parse_mutation_and_cli_never_builds_invalid_bytes(
        self,
    ):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            for target in ("portable", "copilot"):
                with self.subTest(target=target):
                    source_root = write_pack(base / target)
                    source = api["parse_pack"](source_root)
                    skill_file = source_root / "skills/demo-pack-skill/SKILL.md"
                    skill_file.write_bytes(
                        b"---\nname: demo-pack-skill\ndescription:\n---\n"
                        b"\nInvalid post-parse content.\n"
                    )

                    with self.assertRaisesRegex(
                        api["TargetError"], "changed since parsing"
                    ):
                        api["compile_target"](source, target)

            repo = base / "cli-repo"
            source_root = write_pack(repo / "expertise/packs/demo-pack")
            skill_file = source_root / "skills/demo-pack-skill/SKILL.md"

            def mutate_after_parse(pack_root, **kwargs):
                source = api["parse_pack"](pack_root, **kwargs)
                skill_file.write_bytes(
                    b"---\nname: demo-pack-skill\ndescription:\n---\n"
                    b"\nInvalid post-parse content.\n"
                )
                return source

            output = io.StringIO()
            with patch("expertise.cli.parse_pack", side_effect=mutate_after_parse):
                with contextlib.redirect_stdout(output):
                    result = api["cli_main"](
                        [
                            "build",
                            "demo-pack",
                            "--target",
                            "portable",
                            "--known-agent",
                            "researcher",
                        ],
                        repo_root=repo,
                    )

            self.assertEqual(result, 2)
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["status"], "error")
            self.assertEqual(payload["error"], "TargetError")
            self.assertIn("changed since parsing", payload["message"])
            self.assertFalse((repo / "dist").exists())

    def test_parse_and_compile_share_the_snapshot_captured_after_discovery(self):
        api = self.framework()
        from expertise import parser as parser_module
        from expertise.parser import source_content_digest

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = write_pack(root / "race-pack")
            skill_file = source_root / "skills/demo-pack-skill/SKILL.md"
            relative_skill = "skills/demo-pack-skill/SKILL.md"
            original_bytes = skill_file.read_bytes()
            mutated_bytes = (
                b"---\nname: demo-pack-skill\n"
                b"description: Changed but still valid.\n---\n\n"
                b"Captured snapshot bytes.\n"
            )
            original_capture = parser_module._capture_source_snapshot

            def mutate_after_snapshot(
                pack_root,
                relative_files,
                manifest_path,
                manifest_bytes,
                initial_files=None,
            ):
                snapshot = original_capture(
                    pack_root,
                    relative_files,
                    manifest_path,
                    manifest_bytes,
                    initial_files,
                )
                skill_file.write_bytes(mutated_bytes)
                return snapshot

            with patch(
                "expertise.parser._capture_source_snapshot",
                side_effect=mutate_after_snapshot,
            ):
                source = api["parse_pack"](source_root)

            self.assertEqual(source.source_snapshot[relative_skill], original_bytes)
            with self.assertRaisesRegex(api["TargetError"], "changed since parsing"):
                api["compile_target"](source, "portable")
        self.assertEqual(
            source.ir.content_digest,
            source_content_digest(source.source_snapshot),
        )

    def test_cli_validate_parses_current_source_without_using_a_stale_digest(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            source_root = write_pack(repo / "expertise/packs/demo-pack")
            original_source = api["parse_pack"](source_root)
            skill_file = source_root / "skills/demo-pack-skill/SKILL.md"
            skill_file.write_bytes(
                b"---\nname: demo-pack-skill\n"
                b"description: Updated valid description.\n---\n\n"
                b"Updated valid content.\n"
            )
            current_source = api["parse_pack"](source_root)
            self.assertNotEqual(
                current_source.ir.content_digest,
                original_source.ir.content_digest,
            )

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = api["cli_main"](
                    ["validate", "demo-pack", "--known-agent", "researcher"],
                    repo_root=repo,
                )

            self.assertEqual(result, 0)
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["status"], "valid")
            self.assertEqual(
                payload["content_digest"], current_source.ir.content_digest
            )
            self.assertFalse((repo / "dist").exists())
            with self.assertRaises(api["TargetError"]):
                api["compile_target"](original_source, "portable")

    def test_copilot_rejects_contributed_agent_mutation_after_parse(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = write_pack(root / "agent-source")
            source = api["parse_pack"](source_root)
            agent_file = source_root / "agents/demo-pack-engineer.agent.md"
            original = agent_file.read_bytes()
            agent_file.write_bytes(
                original.replace(
                    b"declared demo responsibility",
                    b"updated demo responsibility",
                )
            )
            output = root / "dist/demo-pack/1.0.0/copilot"

            try:
                artifact = api["compile_target"](source, "copilot")
            except api["TargetError"] as error:
                self.assertIn("changed since parsing", str(error))
            else:
                api["materialize_target"](
                    artifact,
                    output_dir=output,
                    dist_root=root / "dist",
                )

            self.assertFalse(output.exists())

    def test_copilot_validates_routing_file_references_against_the_pack_root(
        self,
    ):
        api = self.framework()

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            direct_root = write_pack(root / "direct")
            direct_agent = direct_root / "agents/demo-pack-engineer.agent.md"
            direct_agent.write_text(
                direct_agent.read_text(encoding="utf-8").replace(
                    "</workflow>", "#file:./references/USEFOR.md\n</workflow>"
                ),
                encoding="utf-8",
            )
            direct_source = api["parse_pack"](direct_root)
            with self.assertRaisesRegex(
                api["TargetError"], "per-agent package directory"
            ):
                api["compile_target"](direct_source, "copilot")

            def nested_pack(path: Path, *, include_support_files: bool) -> Path:
                nested_root = write_pack(path)
                agent_id = "demo-pack-engineer"
                old_agent = nested_root / f"agents/{agent_id}.agent.md"
                agent_dir = nested_root / f"agents/{agent_id}"
                reference_dir = agent_dir / "references"
                reference_dir.mkdir(parents=True)
                nested_agent = agent_dir / f"{agent_id}.agent.md"
                nested_agent.write_text(
                    old_agent.read_text(encoding="utf-8").replace(
                        "</workflow>", "#file:./references/USEFOR.md\n</workflow>"
                    ),
                    encoding="utf-8",
                )
                old_agent.unlink()
                manifest = read_pack_manifest(nested_root)
                manifest["agents"]["contributions"][0]["source"] = (
                    f"agents/{agent_id}/{agent_id}.agent.md"
                )
                write_pack_manifest(nested_root, manifest)
                if include_support_files:
                    (reference_dir / "USEFOR.md").write_text(
                        "Use this agent for demo work.\n", encoding="utf-8"
                    )
                    (reference_dir / "DONOTUSEFOR.md").write_text(
                        "Do not use for unrelated work.\n", encoding="utf-8"
                    )
                return nested_root

            missing_root = nested_pack(
                root / "nested-missing", include_support_files=False
            )
            missing_source = api["parse_pack"](missing_root)
            with self.assertRaisesRegex(
                api["TargetError"], "routing reference is unavailable"
            ):
                api["compile_target"](missing_source, "copilot")

            complete_root = nested_pack(
                root / "nested-complete", include_support_files=True
            )
            complete_source = api["parse_pack"](complete_root)
            artifact = api["compile_target"](complete_source, "copilot")
            self.assertIn(
                "com.github.copilot/agents/demo-pack-engineer.agent.md",
                artifact.files,
            )
            self.assertEqual(artifact.source_digest, complete_source.ir.content_digest)

    def test_portable_and_copilot_reject_mcp_mutation_after_parse(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = write_pack(root / "mcp-source")
            source = api["parse_pack"](source_root)
            mcp_file = source_root / "mcp.json"
            mcp = json.loads(mcp_file.read_text(encoding="utf-8"))
            mcp["mcpServers"]["demo-pack-tools"]["command"] = "updated-demo-tool"
            mcp_file.write_text(json.dumps(mcp), encoding="utf-8")

            for target in ("portable", "copilot"):
                with self.subTest(target=target):
                    output = root / f"dist/demo-pack/1.0.0/{target}"
                    try:
                        artifact = api["compile_target"](source, target)
                    except api["TargetError"] as error:
                        self.assertIn("changed since parsing", str(error))
                    else:
                        api["materialize_target"](
                            artifact,
                            output_dir=output,
                            dist_root=root / "dist",
                        )
                    self.assertFalse(output.exists())

    def test_portable_and_copilot_targets_are_deterministic_and_nonduplicating(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            source_root = write_pack(Path(directory) / "demo")
            source = api["parse_pack"](source_root)
            source_manifest_before = (source_root / "pack.yaml").read_bytes()
            portable_a = api["compile_target"](source, "portable")
            portable_b = api["compile_target"](source, "portable")
            copilot = api["compile_target"](source, "copilot")

            portable_files = portable_a.file_map()
            copilot_files = copilot.file_map()

            self.assertEqual(portable_files, portable_b.file_map())
            self.assertEqual(portable_a.digest, portable_b.digest)
            self.assertEqual(portable_a.source_digest, source.ir.content_digest)
            self.assertEqual(copilot.source_digest, source.ir.content_digest)
            self.assertEqual(
                set(portable_files),
                {
                    "plugin.json",
                    "mcp.json",
                    "skills/demo-pack-skill/SKILL.md",
                    "com.doodooms.agentic-workflow/integration.yaml",
                    "com.doodooms.agentic-workflow/agents/demo-pack-engineer.agent.md",
                },
            )
            self.assertEqual(
                set(copilot_files),
                {
                    "plugin.json",
                    "mcp.json",
                    "skills/demo-pack-skill/SKILL.md",
                    "com.github.copilot/agents/demo-pack-engineer.agent.md",
                    "com.doodooms.agentic-workflow/integration.yaml",
                    "com.doodooms.agentic-workflow/agents/demo-pack-engineer.agent.md",
                },
            )
            self.assertEqual(
                portable_files["skills/demo-pack-skill/SKILL.md"],
                copilot_files["skills/demo-pack-skill/SKILL.md"],
            )
            for relative, content in portable_files.items():
                self.assertEqual(copilot_files[relative], content)
            self.assertNotIn(
                "com.github.copilot/agents/demo-pack-engineer.agent.md",
                portable_files,
            )
            self.assertEqual(
                copilot_files["com.github.copilot/agents/demo-pack-engineer.agent.md"],
                (source_root / "agents/demo-pack-engineer.agent.md").read_bytes(),
            )
            integration = yaml.safe_load(
                portable_files["com.doodooms.agentic-workflow/integration.yaml"]
            )
            self.assertEqual(
                integration["agents"]["contributions"][0]["source"],
                "com.doodooms.agentic-workflow/agents/demo-pack-engineer.agent.md",
            )
            self.assertEqual(
                json.loads(portable_files["plugin.json"])["extensions"][
                    "com.doodooms.agentic-workflow"
                ]["integrationManifest"],
                "com.doodooms.agentic-workflow/integration.yaml",
            )
            self.assertTrue(
                all(".github" not in Path(path).parts for path in portable_files)
            )
            self.assertTrue(
                all(".github" not in Path(path).parts for path in copilot_files)
            )
            self.assertEqual(
                json.loads(portable_files["plugin.json"])["$schema"],
                "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
            )
            self.assertEqual(
                json.loads(portable_files["mcp.json"])["$schema"],
                "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
            )
            self.assertEqual(
                (source_root / "pack.yaml").read_bytes(), source_manifest_before
            )

    def test_copilot_only_pack_lowers_portable_core_but_rejects_portable_target(self):
        api = self.framework()
        from expertise.targets.portable import compile_portable

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = write_pack(root / "copilot-only")
            manifest = read_pack_manifest(source_root)
            manifest["compatibility"]["targets"] = ["copilot"]
            write_pack_manifest(source_root, manifest)
            source = api["parse_pack"](source_root)

            copilot = api["compile_target"](source, "copilot")
            self.assertEqual(copilot.target, "copilot")
            self.assertIn("plugin.json", copilot.files)
            self.assertIn("mcp.json", copilot.files)
            self.assertIn("skills/demo-pack-skill/SKILL.md", copilot.files)
            self.assertIn(
                "com.github.copilot/agents/demo-pack-engineer.agent.md",
                copilot.files,
            )
            with self.assertRaisesRegex(api["TargetError"], "portable target"):
                compile_portable(source)

    def test_codex_target_contains_plugin_wide_mcp_and_native_agent_sidecar(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = write_pack(root / "codex-pack")
            manifest = read_pack_manifest(source_root)
            manifest["compatibility"]["targets"] = ["codex"]
            write_pack_manifest(source_root, manifest)
            source = api["parse_pack"](source_root)

            artifact = api["compile_target"](source, "codex")

        self.assertEqual(artifact.target, "codex")
        self.assertIn("plugin.json", artifact.files)
        self.assertIn("mcp.json", artifact.files)
        mcp_manifest = json.loads(artifact.files["mcp.json"])
        self.assertEqual(
            mcp_manifest["mcpServers"]["demo-pack-tools"]["command"],
            "demo-tool",
        )
        self.assertIn("skills/demo-pack-skill/SKILL.md", artifact.files)
        agent_toml = tomllib.loads(
            artifact.files["codex-agents/demo-pack-engineer.toml"].decode("utf-8")
        )
        self.assertEqual(agent_toml["name"], "demo-pack-engineer")
        self.assertIn("declared demo responsibility", agent_toml["description"])
        self.assertIn("<workflow>", agent_toml["developer_instructions"])
        self.assertNotIn("mcp_servers", agent_toml)
        self.assertNotIn("tools", agent_toml)
        self.assertFalse(
            any(path.startswith("com.github.copilot/") for path in artifact.files)
        )
        self.assertIn(
            "com.doodooms.agentic-workflow/integration.yaml",
            artifact.files,
        )

    def test_immediate_workflows_survive_every_compiled_target(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = write_pack(root / "workflow-pack")
            manifest = read_pack_manifest(source_root)
            manifest["compatibility"]["targets"] = ["portable", "copilot", "codex"]
            write_pack_manifest(source_root, manifest)
            workflow_path = (
                source_root
                / "skills"
                / "demo-pack-skill"
                / "workflows"
                / "concurrency.md"
            )
            workflow_path.parent.mkdir()
            workflow_path.write_text(
                "---\n"
                "id: concurrency\n"
                "description: Falsify concurrent updates.\n"
                "invoke_for: [shared mutable state]\n"
                "avoid_for: [sequential behavior]\n"
                "references: []\n"
                "---\n"
                "## Check concurrent updates\n"
                "1. Test the shared-state contract.\n",
                encoding="utf-8",
            )
            source = api["parse_pack"](source_root)
            relative_path = "skills/demo-pack-skill/workflows/concurrency.md"

            for target in ("portable", "copilot", "codex"):
                with self.subTest(target=target):
                    artifact = api["compile_target"](source, target)
                    self.assertEqual(
                        artifact.files[relative_path],
                        workflow_path.read_bytes(),
                    )

    def test_scaffold_creates_a_valid_plugin_source_without_overwriting(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = io.StringIO()
            args = [
                "scaffold",
                "docs-helper",
                "--name",
                "Docs Helper",
                "--description",
                "Version-aware documentation workflows.",
                "--capability",
                "docs.lookup",
                "--skill-id",
                "docs-helper-lookup",
                "--skill-description",
                "Find reliable library documentation.",
                "--publisher",
                "Example Team",
                "--source",
                "local-workspace",
                "--project-to",
                "researcher",
                "--known-agent",
                "researcher",
            ]
            with contextlib.redirect_stdout(output):
                self.assertEqual(api["cli_main"](args, repo_root=root), 0)
            result = json.loads(output.getvalue())
            pack_root = root / "expertise/packs/docs-helper"
            source = api["parse_pack"](pack_root)

            self.assertEqual(result["status"], "scaffolded")
            self.assertEqual(source.ir.type, "horizontal")
            self.assertIn("docs-helper-lookup", {item.id for item in source.ir.skills})
            self.assertEqual(
                source.ir.compatibility.targets, ("codex", "copilot", "portable")
            )

            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(api["cli_main"](args, repo_root=root), 2)
            self.assertTrue((pack_root / "pack.yaml").is_file())
            self.assertTrue(
                (pack_root / "skills/docs-helper-lookup/SKILL.md").is_file()
            )

    def test_compiled_portable_plugin_can_be_parsed_as_an_installed_source(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = api["parse_pack"](write_pack(root / "source"))
            artifact = api["compile_target"](source, "portable")
            plugin_root = api["materialize_target"](
                artifact,
                output_dir=root / "dist" / "demo-plugin",
                dist_root=root / "dist",
            )

            installed_source = api["parse_pack"](plugin_root)
            rebuilt = api["compile_target"](installed_source, "copilot")

        self.assertEqual(installed_source.ir.id, source.ir.id)
        self.assertEqual(
            installed_source.ir.agents.contributions[0].source,
            "com.doodooms.agentic-workflow/agents/demo-pack-engineer.agent.md",
        )
        self.assertIn(
            "com.github.copilot/agents/demo-pack-engineer.agent.md",
            rebuilt.files,
        )
        self.assertEqual(
            rebuilt.files["skills/demo-pack-skill/SKILL.md"],
            artifact.files["skills/demo-pack-skill/SKILL.md"],
        )

    def test_build_materializes_only_under_dist_and_never_overwrites(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = api["parse_pack"](write_pack(root / "pack"))
            dist_root = root / "dist"
            output = dist_root / "demo-pack" / "1.0.0" / "portable"
            artifact = api["compile_target"](source, "portable")

            materialized = api["materialize_target"](
                artifact, output_dir=output, dist_root=dist_root
            )
            self.assertEqual(materialized, output)
            self.assertTrue((output / "plugin.json").is_file())
            self.assertTrue((output / "skills/demo-pack-skill/SKILL.md").is_file())
            self.assertFalse((output / ".github").exists())

            sentinel = output / "sentinel.txt"
            sentinel.write_text("keep", encoding="utf-8")
            with self.assertRaises(api["TargetError"]):
                api["materialize_target"](
                    artifact, output_dir=output, dist_root=dist_root
                )
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")

            with self.assertRaises(api["TargetError"]):
                api["materialize_target"](
                    artifact,
                    output_dir=root / ".github" / "consumer",
                    dist_root=dist_root,
                )

            with self.assertRaisesRegex(api["TargetError"], "under dist"):
                api["materialize_target"](
                    artifact,
                    output_dir=dist_root / ".." / "escaped",
                    dist_root=dist_root,
                )

            outside = root / "outside"
            outside.mkdir()
            linked_output = dist_root / "linked-output"
            linked_output.symlink_to(outside, target_is_directory=True)
            with self.assertRaises(api["TargetError"]):
                api["materialize_target"](
                    artifact,
                    output_dir=linked_output / "portable",
                    dist_root=dist_root,
                )
            self.assertFalse((outside / "portable").exists())

    def test_compiled_target_and_materializer_reject_unsafe_paths(self):
        api = self.framework()
        from expertise.targets.common import CompiledTarget

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = api["parse_pack"](write_pack(root / "pack"))
            unsafe_files = (
                {"../../outside/file": b"unsafe"},
                {".. /outside/file": b"windows-normalized traversal"},
                {"/outside/file": b"absolute"},
                {"C:/outside/file": b"windows absolute"},
                {".github/agent.md": b"consumer state"},
                {"plugin.json": "not bytes"},
            )
            for files in unsafe_files:
                with self.subTest(files=files):
                    with self.assertRaises(api["TargetError"]):
                        CompiledTarget(
                            "portable",
                            source.ir.reference,
                            source.ir.content_digest,
                            files,
                        )

            artifact = api["compile_target"](source, "portable")
            object.__setattr__(
                artifact,
                "files",
                {"../../outside/file": b"must not escape dist"},
            )
            dist_root = root / "dist"
            output = dist_root / "portable"
            with self.assertRaises(api["TargetError"]):
                api["materialize_target"](
                    artifact,
                    output_dir=output,
                    dist_root=dist_root,
                )

            self.assertFalse((root / "outside/file").exists())
            self.assertFalse(output.exists())

            sentinel = root / "outside/file"
            sentinel.parent.mkdir(parents=True)
            sentinel.write_text("preserve", encoding="utf-8")
            second_output = dist_root / "portable-sentinel-check"
            with self.assertRaises(api["TargetError"]):
                api["materialize_target"](
                    artifact,
                    output_dir=second_output,
                    dist_root=dist_root,
                )
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve")
            self.assertFalse(second_output.exists())

    def test_module_cli_validate_test_and_build_use_the_expertise_interface(self):
        api = self.framework()
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            pack_root = write_pack(repo / "expertise/packs/demo-pack")
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                self.assertEqual(
                    api["cli_main"](
                        ["validate", "demo-pack", "--known-agent", "researcher"],
                        repo_root=repo,
                    ),
                    0,
                )
                self.assertEqual(
                    api["cli_main"](
                        ["test", "demo-pack", "--known-agent", "researcher"],
                        repo_root=repo,
                    ),
                    0,
                )
                self.assertEqual(
                    api["cli_main"](
                        [
                            "build",
                            "demo-pack",
                            "--target",
                            "portable",
                            "--known-agent",
                            "researcher",
                        ],
                        repo_root=repo,
                    ),
                    0,
                )

            built = repo / "dist/demo-pack/1.0.0/portable"
            self.assertTrue((built / "plugin.json").is_file())
            self.assertTrue((built / "skills/demo-pack-skill/SKILL.md").is_file())
            self.assertFalse((repo / ".github").exists())
            self.assertTrue((pack_root / "pack.yaml").is_file())

            first_validate_output = io.StringIO()
            second_validate_output = io.StringIO()
            with contextlib.redirect_stdout(first_validate_output):
                self.assertEqual(
                    api["cli_main"](
                        ["validate", "demo-pack", "--known-agent", "researcher"],
                        repo_root=repo,
                    ),
                    0,
                )
            with contextlib.redirect_stdout(second_validate_output):
                self.assertEqual(
                    api["cli_main"](
                        ["validate", "demo-pack", "--known-agent", "researcher"],
                        repo_root=repo,
                    ),
                    0,
                )
            self.assertEqual(
                json.loads(first_validate_output.getvalue()),
                json.loads(second_validate_output.getvalue()),
            )

            first_test_output = io.StringIO()
            second_test_output = io.StringIO()
            with contextlib.redirect_stdout(first_test_output):
                self.assertEqual(
                    api["cli_main"](
                        ["test", "demo-pack", "--known-agent", "researcher"],
                        repo_root=repo,
                    ),
                    0,
                )
            with contextlib.redirect_stdout(second_test_output):
                self.assertEqual(
                    api["cli_main"](
                        ["test", "demo-pack", "--known-agent", "researcher"],
                        repo_root=repo,
                    ),
                    0,
                )
            self.assertEqual(
                json.loads(first_test_output.getvalue()),
                json.loads(second_test_output.getvalue()),
            )
            expected_source_digest = api["parse_pack"](pack_root).ir.content_digest
            test_payload = json.loads(first_test_output.getvalue())
            for target in ("portable", "copilot"):
                self.assertEqual(
                    test_payload["targets"][target]["source_digest"],
                    expected_source_digest,
                )

            copilot_build_output = io.StringIO()
            with contextlib.redirect_stdout(copilot_build_output):
                self.assertEqual(
                    api["cli_main"](
                        [
                            "build",
                            "demo-pack",
                            "--target",
                            "copilot",
                            "--known-agent",
                            "researcher",
                        ],
                        repo_root=repo,
                    ),
                    0,
                )
            self.assertEqual(
                json.loads(copilot_build_output.getvalue())["source_digest"],
                expected_source_digest,
            )

            original_plugin = (built / "plugin.json").read_bytes()
            overwrite_output = io.StringIO()
            with contextlib.redirect_stdout(overwrite_output):
                self.assertEqual(
                    api["cli_main"](
                        [
                            "build",
                            "demo-pack",
                            "--target",
                            "portable",
                            "--known-agent",
                            "researcher",
                        ],
                        repo_root=repo,
                    ),
                    2,
                )
            self.assertEqual((built / "plugin.json").read_bytes(), original_plugin)
            self.assertEqual(json.loads(overwrite_output.getvalue())["status"], "error")

            escaped_output = io.StringIO()
            with contextlib.redirect_stdout(escaped_output):
                self.assertEqual(
                    api["cli_main"](
                        [
                            "build",
                            "demo-pack",
                            "--target",
                            "portable",
                            "--output",
                            "dist/../escaped",
                        ],
                        repo_root=repo,
                    ),
                    2,
                )
            self.assertFalse((repo / "escaped").exists())


if __name__ == "__main__":
    unittest.main()
