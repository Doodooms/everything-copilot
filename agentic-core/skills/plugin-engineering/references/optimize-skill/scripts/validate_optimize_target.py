from __future__ import annotations

import argparse
from pathlib import Path

from skill_harness.scaffold import ScaffoldConfig
from skill_harness.validator import validate_skill_structure


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    validate_skill_structure(args.skill, ScaffoldConfig.from_file(args.config))
    print("structural validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
