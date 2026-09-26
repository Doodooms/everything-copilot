import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "agentic-core/skills/context-management/references/token-optimization/scripts/measure_context.py"
)


class AgenticCoreContextMeasurementTests(unittest.TestCase):
    def run_measurement(self, manifest: Path) -> subprocess.CompletedProcess[str]:
        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--manifest", str(manifest)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            env=environment,
        )

    def test_counts_one_local_skill_file_without_projection_manifest(self):
        self.assertTrue(SCRIPT.is_file(), "token-optimization needs its local measurement script")
        with tempfile.TemporaryDirectory() as directory:
            skill_file = Path(directory) / "SKILL.md"
            skill_file.write_text("Compact skill: MUST preserve behavior.", encoding="utf-8")
            environment = dict(os.environ)
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--file", str(skill_file)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
                env=environment,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["tokenizer"], "local-regex-estimate-v1")
        self.assertTrue(report["approximate"])
        self.assertEqual(report["file"], str(skill_file))
        self.assertEqual(report["tokens"], 7)

    def test_counts_target_context_and_treats_budget_exceedance_as_warning(self):
        self.assertTrue(SCRIPT.is_file(), "token-optimization needs its local measurement script")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "agents").mkdir()
            (root / "skills/architecture-design/workflows").mkdir(parents=True)
            (root / "skills/architecture-design/references").mkdir()
            (root / "tools").mkdir()
            (root / "agents/architect.agent.md").write_text(
                "Architect role and responsibilities.", encoding="utf-8"
            )
            skill_path = "skills/architecture-design/SKILL.md"
            workflow_path = "skills/architecture-design/workflows/decision.md"
            reference_path = "skills/architecture-design/references/background.md"
            (root / skill_path).write_text(
                "Reusable architecture method.", encoding="utf-8"
            )
            (root / workflow_path).write_text(
                "Selected workflow with a specific decision procedure.", encoding="utf-8"
            )
            second_workflow_path = "skills/architecture-design/workflows/tdd.md"
            (root / second_workflow_path).write_text(
                "Second selected workflow with a test-first procedure.", encoding="utf-8"
            )
            (root / reference_path).write_text(
                "This long reference must not contribute any tokens. " * 500,
                encoding="utf-8",
            )
            (root / "tools/read-schema.json").write_text(
                '{"name":"read","inputSchema":{"type":"object"}}', encoding="utf-8"
            )
            manifest = root / "projection.json"
            manifest.write_text(
                json.dumps(
                    {
                        "warning_budget_tokens": 1,
                        "agents": {
                            "architect": {
                                "definition": "agents/architect.agent.md",
                                "skills": [skill_path],
                                "workflows": [workflow_path, second_workflow_path],
                                "references": [reference_path],
                                "tools": ["tools/read-schema.json"],
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_measurement(manifest)

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["tokenizer"], "local-regex-estimate-v1")
        architect = report["agents"]["architect"]
        self.assertEqual(architect["definition"], "agents/architect.agent.md")
        self.assertEqual(architect["skills"], [skill_path])
        self.assertEqual(architect["workflows"], [workflow_path, second_workflow_path])
        self.assertEqual(architect["references_excluded"], [reference_path])
        self.assertEqual(architect["tools"], ["tools/read-schema.json"])
        self.assertGreater(architect["definition_tokens"], 0)
        self.assertGreater(architect["skill_tokens"], 0)
        self.assertGreater(architect["workflow_tokens"], 0)
        self.assertGreater(architect["tool_tokens"], 0)
        self.assertEqual(
            architect["total_tokens"],
            architect["definition_tokens"]
            + architect["skill_tokens"]
            + architect["workflow_tokens"]
            + architect["tool_tokens"],
        )
        self.assertTrue(report["warnings"], "a soft budget must warn, not reject")
        self.assertIn("above the advisory budget", report["warnings"][0])

    def test_rejects_projection_paths_that_escape_the_local_manifest_root(self):
        self.assertTrue(SCRIPT.is_file(), "token-optimization needs its local measurement script")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "projection.json"
            manifest.write_text(
                json.dumps(
                    {
                        "agents": {
                            "architect": {
                                "definition": "../outside.agent.md",
                                "skills": [],
                                "tools": [],
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_measurement(manifest)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("outside the manifest root", result.stderr.lower())

    def test_rejects_nested_workflow_paths_and_legacy_subskills(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "agents").mkdir()
            (root / "agents/architect.agent.md").write_text("Architect.", encoding="utf-8")
            manifest = root / "projection.json"
            manifest.write_text(
                json.dumps(
                    {
                        "agents": {
                            "architect": {
                                "definition": "agents/architect.agent.md",
                                "skills": [],
                                "workflows": [
                                    "skills/architecture/references/design/workflows/tdd.md"
                                ],
                                "tools": [],
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            nested_workflow = self.run_measurement(manifest)
            manifest.write_text(
                json.dumps(
                    {
                        "agents": {
                            "architect": {
                                "definition": "agents/architect.agent.md",
                                "skills": [],
                                "workflows": [],
                                "subskills": ["skills/architecture/references/tdd.md"],
                                "tools": [],
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            legacy_subskill = self.run_measurement(manifest)

        self.assertNotEqual(nested_workflow.returncode, 0)
        self.assertIn("immediate markdown procedures", nested_workflow.stderr.lower())
        self.assertNotEqual(legacy_subskill.returncode, 0)
        self.assertIn("subskills are unsupported", legacy_subskill.stderr.lower())

    def test_rejects_a_symlink_that_escapes_the_local_manifest_root(self):
        self.assertTrue(SCRIPT.is_file(), "token-optimization needs its local measurement script")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package_root = root / "projection"
            package_root.mkdir()
            outside_file = root / "outside.agent.md"
            outside_file.write_text("outside the permitted root", encoding="utf-8")
            try:
                (package_root / "agent-link.md").symlink_to(outside_file)
            except OSError as exc:
                self.skipTest(f"symlink creation is unavailable: {exc}")

            manifest = package_root / "projection.json"
            manifest.write_text(
                json.dumps(
                    {
                        "agents": {
                            "architect": {
                                "definition": "agent-link.md",
                                "skills": [],
                                "tools": [],
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_measurement(manifest)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("outside the manifest root", result.stderr.lower())

    def test_rejects_malformed_projection_json(self):
        self.assertTrue(SCRIPT.is_file(), "token-optimization needs its local measurement script")
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "projection.json"
            manifest.write_text('{"agents":', encoding="utf-8")

            result = self.run_measurement(manifest)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not readable json", result.stderr.lower())
        self.assertNotIn("traceback", result.stderr.lower())

    def test_rejects_a_missing_projected_file(self):
        self.assertTrue(SCRIPT.is_file(), "token-optimization needs its local measurement script")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "projection.json"
            manifest.write_text(
                json.dumps(
                    {
                        "agents": {
                            "architect": {
                                "definition": "missing.agent.md",
                                "skills": [],
                                "tools": [],
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_measurement(manifest)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not a file", result.stderr.lower())

    def test_reports_multiple_agent_projections_without_cross_contamination(self):
        self.assertTrue(SCRIPT.is_file(), "token-optimization needs its local measurement script")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for subdirectory in ("agents", "skills", "tools"):
                (root / subdirectory).mkdir()
            (root / "skills/architecture").mkdir()
            (root / "skills/research").mkdir()
            files = {
                "agents/architect.agent.md": "Architect role.",
                "agents/researcher.agent.md": "Researcher role with more details.",
                "skills/architecture/SKILL.md": "Architect method.",
                "skills/research/SKILL.md": "Research method with distinct words.",
                "tools/architecture.json": '{"name":"architecture"}',
                "tools/research.json": '{"name":"research","description":"longer"}',
            }
            for relative_path, content in files.items():
                (root / relative_path).write_text(content, encoding="utf-8")

            manifest = root / "projection.json"
            manifest.write_text(
                json.dumps(
                    {
                        "agents": {
                            "architect": {
                                "definition": "agents/architect.agent.md",
                                "skills": ["skills/architecture/SKILL.md"],
                                "tools": ["tools/architecture.json"],
                            },
                            "researcher": {
                                "definition": "agents/researcher.agent.md",
                                "skills": ["skills/research/SKILL.md"],
                                "tools": ["tools/research.json"],
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_measurement(manifest)

        self.assertEqual(result.returncode, 0, result.stderr)
        agents = json.loads(result.stdout)["agents"]
        self.assertEqual(
            agents["architect"]["definition"], "agents/architect.agent.md"
        )
        self.assertEqual(
            agents["researcher"]["definition"], "agents/researcher.agent.md"
        )
        self.assertEqual(
            agents["architect"]["skills"], ["skills/architecture/SKILL.md"]
        )
        self.assertEqual(
            agents["researcher"]["skills"], ["skills/research/SKILL.md"]
        )
        self.assertEqual(agents["architect"]["tools"], ["tools/architecture.json"])
        self.assertEqual(agents["researcher"]["tools"], ["tools/research.json"])
        self.assertNotEqual(
            agents["architect"]["total_tokens"], agents["researcher"]["total_tokens"]
        )

    def test_rejects_non_package_skill_and_nested_workflow_paths(self):
        self.assertTrue(SCRIPT.is_file(), "token-optimization needs its local measurement script")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "agent.agent.md").write_text("agent", encoding="utf-8")
            manifest = root / "projection.json"
            manifest.write_text(
                json.dumps(
                    {
                        "agents": {
                            "architect": {
                                "definition": "agent.agent.md",
                                "skills": ["skills/architecture.md"],
                                "workflows": [
                                    "skills/architecture/workflows/nested/procedure.md"
                                ],
                                "tools": [],
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_measurement(manifest)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SKILL.md", result.stderr)

    def test_measurement_runs_under_a_subprocess_local_only_audit_guard(self):
        self.assertTrue(SCRIPT.is_file(), "token-optimization needs its local measurement script")
        with tempfile.TemporaryDirectory() as directory:
            fixture_root = Path(directory) / "fixture"
            (fixture_root / "scripts").mkdir(parents=True)
            (fixture_root / "agents").mkdir()
            script_copy = fixture_root / "scripts/measure_context.py"
            shutil.copy2(SCRIPT, script_copy)
            (fixture_root / "agents/architect.agent.md").write_text(
                "Local agent definition.", encoding="utf-8"
            )
            manifest = fixture_root / "projection.json"
            manifest.write_text(
                json.dumps(
                    {
                        "agents": {
                            "architect": {
                                "definition": "agents/architect.agent.md",
                                "skills": [],
                                "tools": [],
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            sentinel = Path(directory) / "outside-sentinel.txt"
            sentinel.write_text("must remain unchanged", encoding="utf-8")
            missing_target = Path(directory) / "outside-missing.txt"

            audit_runner = textwrap.dedent(
                r"""
                import os
                import pathlib
                import sys
                import sysconfig

                script_path = pathlib.Path(sys.argv[1]).resolve()
                fixture_root = pathlib.Path(sys.argv[2]).resolve()
                stdlib_root = pathlib.Path(sysconfig.get_path("stdlib")).resolve()
                manifest_path = pathlib.Path(sys.argv[3]).resolve()
                violations = []
                forbidden_prefixes = (
                    "socket.",
                    "http.client.",
                    "urllib.",
                    "ssl.",
                    "subprocess.",
                    "os.exec",
                    "os.spawn",
                    "os.posix_spawn",
                )
                forbidden_events = {
                    "os.system",
                    "os.fork",
                    "os.forkpty",
                    "os.startfile",
                    "ctypes.dlopen",
                }
                mutation_path_indexes = {
                    "os.remove": (0,),
                    "os.unlink": (0,),
                    "os.rmdir": (0,),
                    "os.mkdir": (0,),
                    "os.rename": (0, 1),
                    "os.replace": (0, 1),
                    "os.link": (0, 1),
                    "os.symlink": (0, 1),
                    "os.chmod": (0,),
                    "os.chown": (0,),
                    "os.lchown": (0,),
                    "os.chflags": (0,),
                    "os.lchflags": (0,),
                    "os.lchmod": (0,),
                    "os.truncate": (0,),
                    "os.utime": (0,),
                    "os.chdir": (0,),
                }
                mutation_dir_fd_indexes = {
                    "os.remove": (1,),
                    "os.unlink": (1,),
                    "os.rmdir": (1,),
                    "os.mkdir": (2,),
                    "os.rename": (2, 3),
                    "os.replace": (2, 3),
                    "os.link": (2, 3),
                    "os.symlink": (3,),
                    "os.chmod": (2,),
                    "os.chown": (3,),
                    "os.lchown": (3,),
                    "os.utime": (3,),
                }
                mutation_fd_events = {"os.fchdir", "os.fchmod", "os.fchown", "os.ftruncate"}
                mutator_specs = {
                    "remove": ((0,), ("path",)),
                    "unlink": ((0,), ("path",)),
                    "rmdir": ((0,), ("path",)),
                    "mkdir": ((0,), ("path",)),
                    "rename": ((0, 1), ("src", "dst")),
                    "replace": ((0, 1), ("src", "dst")),
                    "link": ((0, 1), ("src", "dst")),
                    "symlink": ((0, 1), ("src", "dst")),
                    "chmod": ((0,), ("path",)),
                    "chown": ((0,), ("path",)),
                    "lchown": ((0,), ("path",)),
                    "chflags": ((0,), ("path",)),
                    "lchflags": ((0,), ("path",)),
                    "lchmod": ((0,), ("path",)),
                    "truncate": ((0,), ("path",)),
                    "utime": ((0,), ("path",)),
                    "chdir": ((0,), ("path",)),
                }
                write_flags = (
                    os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
                )

                def deny(event, detail):
                    violations.append(f"{event}: {detail}")
                    raise PermissionError("local-only guard blocked " + event)

                def check_mutation_path(event, raw_path):
                    if not isinstance(raw_path, (str, bytes, os.PathLike)):
                        deny(event, f"unresolved mutation target {raw_path!r}")
                    mutation_path = pathlib.Path(os.fsdecode(os.fspath(raw_path)))
                    if not mutation_path.is_absolute():
                        mutation_path = pathlib.Path.cwd() / mutation_path
                    resolved_path = mutation_path.resolve(strict=False)
                    if not resolved_path.is_relative_to(fixture_root):
                        deny(event, resolved_path)

                def check_dir_fds(event, args, kwargs):
                    for index in mutation_dir_fd_indexes.get(event, ()):
                        if index < len(args) and args[index] not in (None, -1):
                            deny(event, "dir_fd makes the mutation path ambiguous")
                    for name, value in kwargs.items():
                        if name.endswith("dir_fd") and value not in (None, -1):
                            deny(event, "dir_fd makes the mutation path ambiguous")

                def install_mutation_wrapper(function_name, positions, names):
                    original = getattr(os, function_name, None)
                    if original is None:
                        return

                    def guarded(*args, **kwargs):
                        event = "os." + function_name
                        check_dir_fds(event, args, kwargs)
                        for index, keyword in zip(positions, names):
                            raw_path = (
                                args[index]
                                if index < len(args)
                                else kwargs.get(keyword)
                            )
                            if raw_path is not None:
                                check_mutation_path(event, raw_path)
                        return original(*args, **kwargs)

                    setattr(os, function_name, guarded)

                for function_name, (positions, names) in mutator_specs.items():
                    install_mutation_wrapper(function_name, positions, names)

                for event in mutation_fd_events:
                    function_name = event.removeprefix("os.")
                    if getattr(os, function_name, None) is not None:
                        def deny_fd_mutation(*args, _event=event, **kwargs):
                            deny(_event, "file-descriptor mutation")

                        setattr(os, function_name, deny_fd_mutation)

                def audit(event, args):
                    if event.startswith(forbidden_prefixes) or event in forbidden_events:
                        deny(event, args[:1])
                    if event in mutation_fd_events:
                        deny(event, "file-descriptor mutation")
                    if event in mutation_path_indexes:
                        check_dir_fds(event, args, {})
                        for path_index in mutation_path_indexes[event]:
                            if path_index >= len(args):
                                continue
                            check_mutation_path(event, args[path_index])
                    if event != "open":
                        return

                    raw_path = args[0]
                    if not isinstance(raw_path, (str, bytes, os.PathLike)):
                        return
                    opened_path = pathlib.Path(
                        os.fsdecode(os.fspath(raw_path))
                    ).resolve(strict=False)
                    mode = args[1] if len(args) > 1 else None
                    flags = args[2] if len(args) > 2 and isinstance(args[2], int) else 0
                    writes = isinstance(mode, str) and any(
                        character in mode for character in "wax+"
                    )
                    if writes or flags & write_flags:
                        deny("open-write", opened_path)
                    # Interpreter runtime files are permitted; projected/user data is fixture-only.
                    in_fixture = opened_path.is_relative_to(fixture_root)
                    in_python_runtime = opened_path.is_relative_to(stdlib_root)
                    if not (in_fixture or in_python_runtime):
                        deny("open-outside-fixture-or-python-runtime", opened_path)

                sys.addaudithook(audit)
                probe_operations = [
                    (sys.argv[index], pathlib.Path(sys.argv[index + 1]))
                    for index in range(4, len(sys.argv), 2)
                ]
                sys.argv = [str(script_path), "--manifest", str(manifest_path)]
                exit_code = 0
                try:
                    code = compile(
                        script_path.read_text(encoding="utf-8"),
                        str(script_path),
                        "exec",
                    )
                    namespace = {
                        "__name__": "__main__",
                        "__file__": str(script_path),
                    }
                    exec(code, namespace)
                except SystemExit as exc:
                    exit_code = exc.code if isinstance(exc.code, int) else 0
                except Exception:
                    if violations:
                        print(
                            "LOCAL_ONLY_GUARD_BLOCKED: " + "; ".join(violations),
                            file=sys.stderr,
                        )
                        raise SystemExit(97)
                    raise

                for operation, probe_path in probe_operations:
                    try:
                        if operation == "path-unlink":
                            probe_path.unlink(missing_ok=True)
                        elif operation == "os-remove":
                            os.remove(probe_path)
                        elif operation == "audit-remove":
                            sys.audit("os.remove", str(probe_path), -1)
                    except PermissionError:
                        pass

                if violations:
                    print(
                        "LOCAL_ONLY_GUARD_BLOCKED: " + "; ".join(violations),
                        file=sys.stderr,
                    )
                    raise SystemExit(97)
                raise SystemExit(exit_code)
                """
            )
            environment = dict(os.environ)
            environment["PYTHONDONTWRITEBYTECODE"] = "1"

            def run_guarded(
                *probe_operations: tuple[str, Path],
            ) -> subprocess.CompletedProcess[str]:
                return subprocess.run(
                    [
                        sys.executable,
                        "-c",
                        audit_runner,
                        str(script_copy),
                        str(fixture_root),
                        str(manifest),
                        *(
                            value
                            for operation, path in probe_operations
                            for value in (operation, str(path))
                        ),
                    ],
                    cwd=fixture_root,
                    capture_output=True,
                    text=True,
                    check=False,
                    env=environment,
                )

            result = run_guarded()
            blocked_mutations = run_guarded(
                ("path-unlink", sentinel),
                ("os-remove", missing_target),
                ("audit-remove", missing_target),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("LOCAL_ONLY_GUARD_BLOCKED", result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(set(report["agents"]), {"architect"})
            self.assertEqual(blocked_mutations.returncode, 97, blocked_mutations.stderr)
            self.assertIn("LOCAL_ONLY_GUARD_BLOCKED", blocked_mutations.stderr)
            self.assertIn("os.unlink", blocked_mutations.stderr)
            self.assertIn("os.remove", blocked_mutations.stderr)
            self.assertIn(str(sentinel), blocked_mutations.stderr)
            self.assertIn(str(missing_target), blocked_mutations.stderr)
            self.assertEqual(
                json.loads(blocked_mutations.stdout)["agents"]["architect"]["definition"],
                "agents/architect.agent.md",
            )
            self.assertTrue(sentinel.is_file(), blocked_mutations.stderr)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "must remain unchanged")
            self.assertFalse(missing_target.exists())


if __name__ == "__main__":
    unittest.main()
