# Foam Agent Plugin

This Pack provides explicit note workflows over the Foam MCP server. Its canonical MCP configuration contains an install-time workspace marker; do not replace it with a machine-specific path.

## Build for a local Foam workspace

Install Foam CLI and keep the Foam workspace under the user's control. Generate a local portable or Codex package with an absolute workspace path:

```sh
python scripts/project_foam_pack.py \
  --target codex \
  --workspace /absolute/path/to/foam-workspace \
  --output /absolute/path/to/output/foam-agent
```

Use `--target portable` for a portable package. The generated `mcp.json` launches the installed Foam CLI directly as `foam mcp --workspace <bound workspace> --allow-writes`. Workspace binding changes only generated output, not the Pack source.

The Foam MCP server exposes read and write tools. Invoke the skills explicitly; `process-inbox` never runs automatically. MCP `create_resource` creates an empty resource, so the skills write content with `update_resource` and verify it with `read_resource` before treating a note as materialized.

## ChatGPT package and local connection

Generate the local workspace-bound ChatGPT package before registering the ChatGPT app. It starts with an empty `.app.json`; its `chatgpt-connection.md` includes the Secure MCP Tunnel command for the bound Foam workspace:

```sh
python scripts/project_chatgpt_plugin.py \
  --pack-id foam-agent-plugin \
  --workspace /absolute/path/to/foam-workspace \
  --tunnel-id your_tunnel_id \
  --output /absolute/path/to/output/foam-chatgpt
```

Create the OpenAI-hosted tunnel, run the generated `tunnel-client` setup with `CONTROL_PLANE_API_KEY` supplied only in the runtime environment, then create the ChatGPT developer-mode app and select that tunnel. After ChatGPT provides the registered app ID, map it to `foam` and regenerate the package:

```sh
printf '{"foam":"asdk_app_your_registered_id"}\n' > app-ids.json
python scripts/project_chatgpt_plugin.py \
  --pack-id foam-agent-plugin \
  --app-ids-json app-ids.json \
  --workspace /absolute/path/to/foam-workspace \
  --tunnel-id your_tunnel_id \
  --output /absolute/path/to/output/foam-chatgpt-registered
```

Package generation does not create the tunnel, register the app, discover tools in ChatGPT, or prove ChatGPT invocation. Those are separate connection/runtime gates.
