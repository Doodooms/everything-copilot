# Copilot Tool Snapshot Extension

This local workspace extension exposes the live VS Code language model tool list through two commands:

- `Agentic Workflow: Export Copilot Tool Snapshot`
- `Agentic Workflow: Check Copilot Tool Name`

On startup, the extension also refreshes `.vscode/copilot-tools.snapshot.json` automatically for each open workspace folder after the tool registry stabilizes.
The export command remains available when you want an explicit on-demand refresh in a selected workspace folder.
The check command lets you test whether a `#tool:` reference matches a live tool or a derived toolset name.

## Run the extension locally

1. Open this repository in VS Code.
2. Start the launch configuration in `.vscode/launch.json` named `Run Copilot Tool Snapshot Extension`.
3. Wait for the startup refresh to populate `.vscode/copilot-tools.snapshot.json`, or run `Agentic Workflow: Export Copilot Tool Snapshot` from the Command Palette.
4. Inspect `.vscode/copilot-tools.snapshot.json`.

## Validator integration

When `.vscode/copilot-tools.snapshot.json` exists, `.github/skills/create-skill/scripts/validate_skill.py` reads it and merges it with a deterministic scan of installed extension manifests. That lets skill validation keep working even when a live runtime snapshot is missing or slightly stale.