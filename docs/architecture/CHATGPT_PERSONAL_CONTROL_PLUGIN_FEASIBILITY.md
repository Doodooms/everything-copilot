# ChatGPT Personal Control Plugin Feasibility

**Status:** PARTIAL — the portable package projector and external-consumer build are verified. ChatGPT account installation, tool discovery, and invocation remain untested.

**Evidence checked:** 2026-09-29. OpenAI documentation changes independently of this repository; recheck the linked plan and account requirements before a deployment decision.

## Decision summary

Plugin Factory can project the existing portable Expertise Pack contract into a small OpenAI-compatible package that contains one MCP server mapping and one expected tool, `control_ping`. The projection reuses the existing portable Pack compiler and the Agentic Core runtime already bundled with the plugin. It adds only the OpenAI `extensions.com.openai.apps` reference and the corresponding `.app.json` entry.

This proves packaging and checkout-independent reconstruction. It does **not** prove that ChatGPT installed the package, can reach the supplied endpoint, exposes exactly the expected tool, or invoked it. MCP tools are supplied by the MCP server. The eventual Control endpoint must itself expose only the approved public operations; the Pack's expected-tool catalog cannot filter an endpoint that advertises more tools.

## ChatGPT surfaces and Plus availability

| Surface | Documented path | What installation means |
| --- | --- | --- |
| ChatGPT web Chat | Register a remote MCP app in Developer Mode, then select Developer Mode and that app in a conversation. The current Developer Mode guide lists Pro, Plus, Business, Enterprise, and Education for web. | Registering the app does not select it for a conversation. |
| ChatGPT desktop, Work mode | Add a local or personal plugin marketplace, then install the package through the Plugins Directory. | The app installs a cached copy. It remains a local desktop plugin, not a package installed into ordinary web Chat. |
| ChatGPT desktop, Codex | The same local marketplace model can expose the package to Codex. | Codex plugin availability does not establish web Chat visibility. |

The current OpenAI Developer Mode guide lists Plus accounts on web as eligible to create and use full MCP apps. This audit did not have access to the user's ChatGPT account UI or workspace policy, so Plus surface availability is **DOCUMENTED**, not observed for this account.

OpenAI documents local marketplaces separately from web Developer Mode apps. In the desktop flow, the app package references the registered MCP connection through `.app.json`; in web Chat, the registered app is selected from the conversation's Developer Mode tool. The package cannot make itself active in every Chat conversation.

## Evidence states

| State | Result | Evidence / limit |
| --- | --- | --- |
| `documented` | PASS | Developer Mode, plugin packaging, MCP server, and local marketplace flows are documented. The Developer Mode guide lists Plus for web. |
| `packaged` | PASS | The installed Agentic Core runtime projected the canonical Pack into a portable plugin package with one app mapping and one MCP server. |
| `installed` | UNTESTED | The external test copied Agentic Core into a clean consumer directory. It did not install the generated package into ChatGPT desktop or an account. |
| `surface_available` | DOCUMENTED_NOT_OBSERVED | Developer Mode guide includes Plus for web. Account UI and workspace policy were not checked. |
| `runtime_visible` | UNTESTED | No ChatGPT conversation was opened with the app selected. |
| `actually_invoked` | UNTESTED | No ChatGPT MCP tool call occurred. No remote server endpoint was supplied. |
| `blocked` | ACCOUNT_AND_ENDPOINT_UNAVAILABLE | This environment has no authorized ChatGPT UI session, registered app ID, or deployed HTTPS MCP endpoint. These prevent runtime proof. No Plus-specific blocker is documented by the current Developer Mode guide. |

For `runtime_visible`, retain evidence from a **new ChatGPT web conversation** showing Developer Mode selected, the registered app attached to that conversation, and the app's discovered tool available to that runtime. An installed directory, generated manifest, marketplace listing, or developer-mode Draft alone is insufficient. For `actually_invoked`, retain the tool call and deterministic `control_ping` result tied to the same registered app.

## Canonical source and projection

Canonical probe Pack:

```text
agentic-core/packs/control-ping-probe/
├── pack.yaml
└── mcp.json
```

It declares the read-only `control.health` capability, one MCP alias (`control`), and one expected tool (`control_ping`). It adds no agent, skill, ticket model, persistent state, or broad Agentic Core MCP servers.

Packaged projector:

```text
agentic-core/runtime/project_chatgpt_personal_plugin.py
```

It calls the existing `expertise.parse_pack` and portable target compiler, then adds:

- `extensions.com.openai.apps: "./.app.json"` to the portable root `plugin.json`;
- `.app.json` mapping the `control` alias to the user's registered app ID;
- the supplied HTTPS endpoint in root `mcp.json`;
- `com.doodooms.agentic-workflow/projection.json` with source, projector, app-ID, artifact, and SHA-256 endpoint digests. It does not repeat the full endpoint URL.

The script requires the account-specific app ID and endpoint as inputs. The endpoint must be an ASCII URI using HTTPS and the exact `/mcp` path, with no userinfo, query or fragment delimiters (including empty trailing `?` or `#`), whitespace, or control characters. Supply international hostnames in IDNA ASCII form. The tested fixture values are deliberately non-deployable (`asdk_app_fixture` and `https://control.example.invalid/mcp`); they prove deterministic packaging only. A real build must use the ID copied from ChatGPT Developer Mode and the matching endpoint. The endpoint hostname must be operator-controlled and contain no secrets: URL parsing can reject credentials and unsafe URL syntax, but cannot determine whether arbitrary hostname text itself contains a secret. Do not put credentials in the URL; use the connection's supported authentication configuration.

### Registered app ID format remains unresolved

The current OpenAI documentation presents conflicting `.app.json` ID guidance. The [plugin packaging guide](https://developers.openai.com/plugins/build/plugins) says the Developer Mode technical ID begins with `plugin_asdk_app...` and instructs using that copied ID in `.app.json`. The [plugin submission error reference](https://developers.openai.com/plugins/deploy/submission-errors) says `.app.json` app IDs must begin with `asdk_app_`, `connector_`, or `templated_apps_`, without the `plugin_` prefix. This projector preserves the supplied ID; it does not normalize it. The `asdk_app_fixture` test value only exercises a schema-shaped fixture and does not resolve which representation a real package accepts. No live registration or package validation was performed, so the real ID representation is **UNRESOLVED**.

Example from the installed plugin copy:

```sh
uv run --no-project --script /path/to/agentic-core/runtime/project_chatgpt_personal_plugin.py \
  --output /absolute/path/to/new-plugin \
  --app-id '<registered-app-id>' \
  --mcp-url 'https://<host>/mcp'
```

The package is not materialized from a source checkout at runtime. The packaged `runtime/expertise` and canonical Pack travel inside the Agentic Core plugin directory. The external-consumer test copied only that plugin directory, ran the projector from an unrelated working directory with `PYTHONPATH` and `PYTHONHOME` removed, confirmed there was no `.git` or top-level source `expertise` package, and compared two generated trees byte-for-byte.

One clean external-consumer run produced:

```text
source_pack:                 control-ping-probe@0.1.0
source_sha256:               f44a20a60a1256d0df1d18486c28f3c4afb1e6d2787fd6392c09659836912272
projector_package_sha256:    38b2130e1b1b6191187cfdc8b48782bad9bd9ef40b6d2d641c2b94cd4d3bdc30
artifact_sha256:             ce9fc39a1cd31f87ce2a9287b504d6643aff699c9407f1389ce120175a42871e
mcp_url_sha256:              4ab2f7b86a43096a0914d3e9ba4be2423dfb305dfbf3fa07a08a7963867bdf90
registered app:              asdk_app_fixture (test fixture; not registered)
MCP URL:                     https://control.example.invalid/mcp (reserved test domain; fixture input only)
```

## MCP surface boundary

The package declares one server and the Pack catalog expects exactly `control_ping`. OpenAI's MCP documentation says the MCP server defines the tools available to ChatGPT and provides settings to toggle discovered tools. The package manifest is not an enforcement boundary for the endpoint's `tools/list` response.

Therefore the future Control service should be a dedicated MCP endpoint that implements only the Control operations approved after the durable Control domain contract is stable. Do not connect a broad project-management server or Agentic Core's general Context7, GitHub, or Semgrep servers to this package. Before claiming a narrow runtime surface, query the real endpoint with an MCP Inspector, verify its complete `tools/list` result, and verify the exact list shown in ChatGPT app settings.

This feasibility Pack records a single expected health operation, but no MCP service implementation or endpoint is included. The Control Task API and Substrat remain outside this task.

## Validation performed

- `tests/test_chatgpt_personal_plugin_projection.py`: PASS (3 tests, 12 subtests), including clean external copy, unrelated CWD, no `PYTHONPATH`/`PYTHONHOME`, no `.git`, no source checkout import, deterministic package bytes, one MCP mapping, exact `/mcp` path validation, ASCII-only input, raw whitespace/control rejection, empty query/fragment delimiter rejection, and endpoint digest-only provenance.
- `tests/test_checkout_independent_projections.py`: PASS (3 tests, 9 subtests), including the already-supported Codex and Antigravity external projectors.
- Package generation uses the existing Pack parser/portable compiler and therefore validates the Pack, MCP schema, and portable plugin manifest before writing.
- `codex plugin --help`: confirmed available commands include add/list/marketplace/remove; there is no `codex plugin validate` command. No install command was run because it would alter a user plugin marketplace/cache and would not prove ordinary web Chat availability.
- ChatGPT installation, registered-app discovery, endpoint reachability, Plus UI eligibility, conversation visibility, and MCP invocation: NOT EXECUTED.

## Remaining gates

1. Check the user's current ChatGPT web account UI and workspace policy; Plus eligibility is documented, but this account's access was not observed.
2. Make the stable Control domain contract the source of truth for which public MCP tools are needed.
3. Implement/deploy the separately owned Control MCP endpoint. For this probe, it must answer only `control_ping`; the production endpoint should expose only the approved Control operations.
4. Register the real HTTPS endpoint in ChatGPT Developer Mode, capture its app ID, and resolve which documented `.app.json` ID representation the live package accepts.
5. Generate the package with those real values; install through a personal marketplace only for desktop Work/Codex testing. Separately attach the Developer Mode app to a new web Chat conversation.
6. Verify the server's entire tool list, visible app/tool list in Chat, and a successful deterministic `control_ping` invocation. Keep each result in its own evidence state.

## Official sources

- [ChatGPT Developer Mode](https://developers.openai.com/api/docs/guides/developer-mode) — current plan eligibility, web app registration, protocols, tool toggles, and per-conversation selection.
- [Package your plugin](https://developers.openai.com/plugins/build/plugins) — portable package layout, OpenAI app mapping, app IDs, and local marketplace behavior.
- [Build an MCP server](https://developers.openai.com/plugins/build/mcp-server) — MCP server owns the available tool surface.
- [Connect and test your plugin](https://developers.openai.com/plugins/deploy/connect-chatgpt) — public HTTPS/Secure MCP Tunnel, endpoint tests, and new-conversation tool-selection evidence.
