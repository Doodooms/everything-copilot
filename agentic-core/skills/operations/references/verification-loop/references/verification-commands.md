# Verification Command Guide

Choose commands from the target repository, not from this guide alone.

| Gate | Typical evidence | Blocking condition |
|---|---|---|
| Build | Build command exit status and diagnostics | Build failure |
| Types | Type-check command output | Type errors |
| Lint | Lint output and configured severity | Errors or policy-defined warnings |
| Tests | Focused and full test results | Failed or unexecuted required tests |
| Coverage | Repository coverage report | Below the repository threshold or unavailable when required |
| Security | Repository scan or specialist review | Critical finding |
| Diff | Changed-file and diff inspection | Unintended or out-of-scope change |

Record skipped gates with a reason. Never infer a pass from the absence of output.
