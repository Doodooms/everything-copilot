"""Check that a project exposes a plausible test tool and test layout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


TOOL_MARKERS = {
    "python": ("pytest.ini", "pyproject.toml", "tox.ini", "setup.cfg"),
    "javascript": ("package.json", "vitest.config.ts", "jest.config.js", "jest.config.ts"),
    "typescript": ("package.json", "vitest.config.ts", "jest.config.ts"),
    "go": ("go.mod",),
}
TEST_DIR_NAMES = ("test", "tests", "__tests__", "e2e")


def detect_languages(project_dir: Path) -> list[str]:
    languages = []
    for language, markers in TOOL_MARKERS.items():
        if any((project_dir / marker).exists() for marker in markers):
            languages.append(language)
    return sorted(set(languages))


def find_test_dirs(project_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in project_dir.iterdir()
        if path.is_dir() and path.name in TEST_DIR_NAMES
    )


def find_test_files(test_dirs: list[Path]) -> list[Path]:
    patterns = ("test_*.py", "*_test.py", "*.test.js", "*.test.ts", "*.spec.js", "*.spec.ts", "*_test.go")
    return sorted({path for directory in test_dirs for pattern in patterns for path in directory.rglob(pattern)})


def verify_framework_usage(project_dir: Path, languages: list[str], test_files: list[Path]) -> list[str]:
    errors = []
    contents = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in test_files)
    if "python" in languages and not any(marker in contents for marker in ("import pytest", "from pytest", "import unittest", "from unittest")):
        errors.append("Python test files do not import pytest or unittest.")
    if any(language in languages for language in ("javascript", "typescript")):
        package_json = project_dir / "package.json"
        package_data = json.loads(package_json.read_text(encoding="utf-8")) if package_json.is_file() else {}
        scripts = package_data.get("scripts", {})
        if not any(command in scripts for command in ("test", "test:unit", "test:e2e")) and not any(
            marker in contents for marker in ("describe(", "it(", "test(")
        ):
            errors.append("JavaScript or TypeScript has no test script or recognizable test declaration.")
    if "go" in languages and not any(path.name.endswith("_test.go") for path in test_files):
        errors.append("Go tooling is present but no *_test.go file was found.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", nargs="?", default=".", type=Path)
    args = parser.parse_args()
    project_dir = args.project.resolve()
    if not project_dir.is_dir():
        parser.error(f"project directory does not exist: {project_dir}")

    languages = detect_languages(project_dir)
    test_dirs = find_test_dirs(project_dir)
    if not languages:
        print("No supported test-tool marker found (pytest, Jest/Vitest, or Go).")
        return 1
    if not test_dirs:
        print("No conventional test directory found: test, tests, __tests__, or e2e.")
        return 1
    test_files = find_test_files(test_dirs)
    if not test_files:
        print("No recognizable test files found in the conventional test directories.")
        return 1
    framework_errors = verify_framework_usage(project_dir, languages, test_files)
    if framework_errors:
        print("\n".join(framework_errors))
        return 1

    print(f"Detected test tooling: {', '.join(languages)}")
    print("Detected test directories: " + ", ".join(path.name for path in test_dirs))
    print(f"Recognized test files: {len(test_files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
