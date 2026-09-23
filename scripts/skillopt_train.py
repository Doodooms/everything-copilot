"""Run SkillOpt with the repository's custom create-skill environment."""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
import shutil

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PROMPTS_ROOT = REPOSITORY_ROOT / "skill_harness" / "skillopt_prompts"


def install_skillopt_prompts() -> None:
    """Materialize prompt resources omitted from the SkillOpt 0.2.0 wheel."""
    import skillopt.prompts

    destination = Path(skillopt.prompts.__file__).resolve().parent
    for prompt in PROMPTS_ROOT.glob("*.md"):
        shutil.copy2(prompt, destination / prompt.name)


def _load_skillopt_train():
    original_path = sys.path[:]
    original_modules = {
        name: module
        for name, module in sys.modules.items()
        if name == "scripts" or name.startswith("scripts.")
    }
    for name in original_modules:
        del sys.modules[name]
    sys.path[:] = [
        entry
        for entry in sys.path
        if Path(entry or Path.cwd()).resolve()
        not in {REPOSITORY_ROOT, REPOSITORY_ROOT / "scripts"}
    ]
    try:
        return importlib.import_module("scripts.train")
    finally:
        for name in list(sys.modules):
            if (name == "scripts" or name.startswith("scripts.")) and name not in original_modules:
                del sys.modules[name]
        sys.modules.update(original_modules)
        sys.path[:] = original_path


skillopt_train = _load_skillopt_train()

if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from skill_harness.skillopt_adapter import WazaSkillOptAdapter


def register_create_skill() -> None:
    """Register the repository adapter with SkillOpt 0.2.0's trainer."""
    skillopt_train._ENV_REGISTRY["create-skill"] = WazaSkillOptAdapter


def main() -> None:
    install_skillopt_prompts()
    register_create_skill()
    skillopt_train.main()


if __name__ == "__main__":
    main()