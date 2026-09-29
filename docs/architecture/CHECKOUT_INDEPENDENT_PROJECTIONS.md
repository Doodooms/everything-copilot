# Checkout-independent Codex and Antigravity projections

## Result and scope

This change packages the existing Codex and Antigravity projectors with the
Agentic Core plugin so a consumer can run them from an installed plugin
directory. It does not add a general harness API. The package is the
`agentic-core/` plugin directory; this repository has no root Python wheel or
package configuration for Plugin Factory.

The implementation branch is `fix/checkout-independent-projections`, based on
`b191fef70459a121889fd091ef03104f4a0ec4ff`. The plugin manifest version is
`0.3.5`. The test-first checkpoint is `51ed2e2` (`test(projections): cover
installed Codex and Antigravity projectors`).

Projection remains separate from runtime execution. Codex output is agent TOML
under `CODEX_HOME/agents`; Antigravity output is a standalone plugin directory.
Neither path invokes a model. `codex_exec` remains an execution backend and is
not used by these projectors.

## Original checkout coupling, reproduced

The baseline experiment used a copied `agentic-core/` directory under a fresh
`/tmp` consumer root and invoked the existing scripts from a different CWD,
with `PYTHONPATH` and `PYTHONHOME` unset.

| Existing path | Observed dependency |
| --- | --- |
| `scripts/install_codex_agents.py` | The script derived the repository root from `__file__`, inserted the checkout root and `agentic-core/` into `sys.path`, loaded `core_agents` from `<checkout>/agentic-core/core_agents.py`, and loaded the `expertise` implementation from `<checkout>/expertise/`. The copied plugin had no installed Codex projector entrypoint. |
| `scripts/project_antigravity_plugin.py` | The script derived the repository root from `__file__` and imported `expertise` from the checkout. Passing the copied plugin to `--source` changed the content being projected, but did not change where the projection implementation was imported from. The copied plugin had no installed Antigravity projector entrypoint. |
| `expertise/targets/antigravity_plugin.py` | The canonical-source implementation found `core_agents.py` by deriving a repository-relative path from the module file. That worked from the checkout but did not identify the corresponding file when the module was loaded from `agentic-core/runtime/expertise/`. |

The current paths did **not** depend on the process CWD, a sibling checkout,
or Git metadata. The hidden dependency was the absolute source tree implied by
the launcher/module locations. Source content such as agents, skills,
`plugin.json`, and `mcp.json` already existed in the Agentic Core plugin. The
projection entrypoints and their implementation were not available as a
self-contained invocation from that copied plugin.

One `Doodooms/everything-copilot` slug remains in the ChatGPT Work handoff
skill's documentation. It is not required by either projection algorithm and
was left for a later repository-rename task. Antigravity projects that skill
text as documentation; this does not create a runtime checkout dependency.

## Installed-plugin seam

The installed plugin now contains:

- `runtime/project_codex_agents.py` — Codex entrypoint;
- `runtime/project_antigravity_plugin.py` — Antigravity entrypoint;
- `runtime/projection_metadata.py` — deterministic source and artifact digest
  helpers;
- `core_agents.py`, `agents/*.md`, and `agents/projections.json` — canonical
  Agentic Core source and target settings;
- `runtime/expertise/` — generated projection implementation synchronized
  from the canonical repository-level `expertise/` source by
  `scripts/sync_pluginctl_runtime.py`.

The Codex entrypoint adds only its own plugin and runtime directories to Python
module lookup. The Antigravity projection reads `core_agents.py` from the
plugin passed as `--source`; the installed plugin is the default source. For
existing minimal projection fixtures without `core_agents.py`, the target
implementation loads the packaged Core loader adjacent to itself and still
reads the fixture's explicit agent directory. This preserves the projection
function's existing fixture behavior without making the installed path depend
on a checkout.

Both entrypoints declare PyYAML through PEP 723 metadata for `uv run
--script`. Their JSON result reports plugin identity, source SHA-256, and
artifact SHA-256. Antigravity also reports the projector package SHA-256. The
Codex agent TOML schema has no supported provenance field, so provenance stays
in the CLI result rather than being added to Codex-native files. The stricter
Antigravity manifest likewise omits the source plugin version; the CLI result
retains it.

The original `scripts/` commands remain checkout developer launchers and now
delegate to the packaged entrypoints. They share the package implementation;
they are not the clean external-consumer route.

## Reproduction runbook

These commands treat a copied `agentic-core/` directory as the installed
plugin package, matching the repository's actual plugin distribution unit.
They deliberately run from an unrelated CWD and unset Python checkout paths.
The package-copy and projection tests also verify required contents and
deterministic tree digests. This is not a Python wheel build.

Run the setup commands from the Plugin Factory checkout root:

```sh
FACTORY="$PWD"
CONSUMER="$(mktemp -d /tmp/agentic-core-projections.XXXXXX)"
PLUGIN="$CONSUMER/installed/agentic-core"
WORKDIR="$CONSUMER/unrelated-cwd"
CODEX_A="$CONSUMER/codex-a"
CODEX_B="$CONSUMER/codex-b"
AGY_A="$CONSUMER/antigravity-a"
AGY_B="$CONSUMER/antigravity-b"

mkdir -p "$CONSUMER/installed" "$WORKDIR"
cp -a "$FACTORY/agentic-core" "$PLUGIN"
cd "$WORKDIR"

env -u PYTHONPATH -u PYTHONHOME \
  uv run --no-project --script "$PLUGIN/runtime/project_codex_agents.py" \
  --codex-home "$CODEX_A" > "$CONSUMER/codex-a.json"
env -u PYTHONPATH -u PYTHONHOME \
  uv run --no-project --script "$PLUGIN/runtime/project_codex_agents.py" \
  --codex-home "$CODEX_B" > "$CONSUMER/codex-b.json"
env -u PYTHONPATH -u PYTHONHOME \
  uv run --no-project --script "$PLUGIN/runtime/project_codex_agents.py" \
  --codex-home "$CODEX_A" --check
diff -qr "$CODEX_A/agents" "$CODEX_B/agents"

env -u PYTHONPATH -u PYTHONHOME \
  uv run --no-project --script "$PLUGIN/runtime/project_antigravity_plugin.py" \
  --output "$AGY_A" > "$CONSUMER/antigravity-a.json"
agy plugin validate "$AGY_A"
env -u PYTHONPATH -u PYTHONHOME \
  uv run --no-project --script "$PLUGIN/runtime/project_antigravity_plugin.py" \
  --output "$AGY_B" > "$CONSUMER/antigravity-b.json"
diff -qr "$AGY_A" "$AGY_B"

uv run --no-project python - "$CONSUMER" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
for name in ("codex-a", "codex-b", "antigravity-a", "antigravity-b"):
    result = json.loads((root / f"{name}.json").read_text(encoding="utf-8"))
    print(name, result["source_sha256"], result["artifact_sha256"])
PY
```

The source-of-truth `expertise/` implementation is synchronized into the
plugin before packaging when it changes:

```sh
cd "$FACTORY"
uv run --no-project python scripts/sync_pluginctl_runtime.py
```

## Observed external-consumer evidence

The runbook was also replayed from a fresh `/tmp` consumer directory. Both
projectors ran with `PYTHONPATH` and `PYTHONHOME` unset from an unrelated CWD.
Each pair of output trees was identical.

| Surface | Package/source SHA-256 | Artifact SHA-256 | Result |
| --- | --- | --- | --- |
| Codex | `de7d30a013816e82c854edbf3c6f5e7a68871caceab1b032c80605abb6e63b55` | `aa583ea2f70f296432898c8555365334be5e5b1f54ecd237be1df4a3058070fe` | 9 valid TOML agent files; repeat digest identical |
| Antigravity | `de7d30a013816e82c854edbf3c6f5e7a68871caceab1b032c80605abb6e63b55` | `659875a46442ef785dbf8658908a3922e276a97627b9d1266485e8befcf483f5` | 240 files, 11 root skills, 59 nested workflows, 9 agents, 3 MCP servers; repeat digest identical |

`agy plugin validate` passed on the generated output: 11 skills, 9 agents, and
3 MCP servers processed. Commands and hooks were skipped because the source
plugin emits neither. Validation is structural only.

The test copies only `agentic-core/` into a disposable installed-plugin
directory; it contains no `.git` metadata. It invokes each packaged entrypoint
from an unrelated CWD, with Python checkout paths removed, and validates
generated outputs. It checks package resources, Codex TOML structure,
Antigravity structure, repeatability, and source/output separation.

## Validation and remaining limits

Validation on Linux:

- The new external-projection test was first run before implementation and
  failed because the installed plugin lacked both projection entrypoints.
- Targeted tests: **125 passed, 68 subtests passed** across checkout-independent
  projections, Antigravity projection, Agentic Core sources, pluginctl package
  and lifecycle, Pack v1, Harness Factory, and ExecutionBackend.
- Ruff check and format check pass for the modified Python files.
- `scripts/sync_pluginctl_runtime.py` check passes.
- `agy plugin validate` passes as described above.
- `git diff --check` passes.

Still unproven:

- Windows execution has not been run.
- Codex host discovery and authenticated/model invocation have not been run;
  this work produces agent files only.
- Antigravity user-profile discovery, Google authentication, and model
  invocation have not been run.
- ChatGPT/Work compatibility remains unproven.
- Core+SWE composition remains untested because no distributable SWE Pack is
  present.
- No generic Plugin Factory-to-Substrat artifact contract was added or proven.

No generic pluginctl redesign, Runtime IR, Substrat integration, repository
rename, or self-maintenance behavior was introduced.
