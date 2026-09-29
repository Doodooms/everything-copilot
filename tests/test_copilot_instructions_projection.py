from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/project_copilot_instructions.py"
SOURCE = ROOT / "AGENTS.md"
OUTPUT = ROOT / ".github/copilot-instructions.md"
MARKER = b"</risk_assessment>"


class CopilotInstructionsProjectionTests(unittest.TestCase):
    def test_projector_preserves_source_bytes_to_marker_and_is_repeatable(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            source = temp_root / "AGENTS.md"
            output = temp_root / "copilot-instructions.md"
            source_bytes = (
                b"policy prefix\r\n"
                b"</risk_assessment>\r\n"
                b"## Git workflow\r\n"
                b"excluded section\r\n"
            )
            source.write_bytes(source_bytes)

            first = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--source",
                    str(source),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            projected = output.read_bytes()

            second = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--source",
                    str(source),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)

            self.assertEqual(projected, b"policy prefix\r\n</risk_assessment>\r\n")
            self.assertEqual(output.read_bytes(), projected)

    def test_checked_in_projection_matches_canonical_source(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        source_lines = SOURCE.read_bytes().splitlines(keepends=True)
        marker_lines = [
            index
            for index, line in enumerate(source_lines)
            if line.rstrip(b"\r\n") == MARKER
        ]
        self.assertEqual(len(marker_lines), 1)
        expected = b"".join(source_lines[: marker_lines[0] + 1])
        self.assertEqual(OUTPUT.read_bytes(), expected)
        self.assertNotIn(b"## Git workflow", OUTPUT.read_bytes())


if __name__ == "__main__":
    unittest.main()
