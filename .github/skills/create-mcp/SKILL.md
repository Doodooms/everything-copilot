---
name: create-mcp
description: "What: Create or update MCP servers with Go, Rust, or Python as the primary implementation targets. When to use: creating a new MCP server, selecting a language and transport, wiring tool or resource registration, configuring VS Code mcp.json, or fixing MCP setup drift after a rename or refactor."
user-invocable: false
disable-model-invocation: false
---

# Create MCP Servers

Use this skill to create or update MCP servers methodically. The canonical decision
points are defined once below, while the workflow points to those sections instead of
repeating them. Load these runtime inputs explicitly:
- #file:./references/URIs.md
- #file:./references/manage_mcp.md
- #file:./assets/language-selection-checklist.md

> The SDK API evolves. Check [modelcontextprotocol.io](https://modelcontextprotocol.io)
> or query Context7 for "MCP" to get current method signatures.

<rules>

- Only reference `#tool:` names that already exist in the runtime or installed extension manifests. Prefer exact names such as `copilot_readFile`, `explore_subagent`, `run_in_terminal`, and `vscode_askQuestions`.
- Do not place punctuation immediately after a `#file:` reference.
- Use the Language Selection section below as the canonical decision matrix for choosing between Go, Rust, Python, and the Node.js exception.
- Node.js must only be used if the user formally requests it, due to its heaviness.
- If the user's constraints are unclear, use #tool:vscode_askQuestions to clarify deployment target, performance envelope, security sensitivity, and iteration speed before recommending a language.
- Use #tool:copilot_readFile to load the runtime inputs listed above before drafting or modifying server code.
- If the codebase is unfamiliar or a rename left stale references behind, use #tool:explore_subagent to locate current MCP entrypoints and configuration files.
- Prefer official SDKs and pin versions. MCP SDK APIs evolve quickly; always verify the installed version's docs before coding.
- Keep tool, resource, and prompt logic independent from transport so `stdio` and Streamable HTTP can be swapped at the entrypoint.
- Start from the smallest tool registration that proves the SDK wiring works before adding resources, auth, or business logic.
- Use #tool:run_in_terminal to run language-specific install, build, or validation commands after the first edit.
</rules>

<workflow>

## Step 1 - Load MCP references

Use #tool:copilot_readFile to load #file:./references/URIs.md before you choose an SDK or package path.
Use #tool:copilot_readFile to load #file:./references/manage_mcp.md before you edit VS Code MCP configuration.
Use #tool:copilot_readFile to load #file:./assets/language-selection-checklist.md before you select the implementation language.

## Step 2 - Inspect the current MCP state

If the repository already contains MCP code or was recently renamed, use #tool:explore_subagent to locate current entrypoints, `mcp.json`, and stale references.
If the exact files are already known, use #tool:copilot_readFile on those files directly.

## Step 3 - Clarify constraints

If the language, deployment target, or transport is not clear from the request and repo state, use #tool:vscode_askQuestions before choosing an implementation path.

## Step 4 - Choose the language

Apply the Language Selection section below and the [language selection checklist](./assets/language-selection-checklist.md).

## Step 5 - Choose the transport

Apply the Transport Selection section below and the operational guidance in [manage MCP servers in VS Code](./references/manage_mcp.md).

## Step 6 - Implement the smallest working server

Pick one of the language setup blocks below, register a single tool, validate it over `stdio`, then expand to resources, prompts, and HTTP transport as needed.

## Step 7 - Validate

Use #tool:run_in_terminal to run the narrowest build, install, or smoke-test command for the touched implementation.
If VS Code integration is part of the task, verify the configuration against [manage MCP servers in VS Code](./references/manage_mcp.md).

## Language Selection

| Primary goal | Recommended language | Why |
|--------------|----------------------|-----|
| Reliable default for production | Go | Strong performance, simple deployment, single binary, low operational friction |
| Maximum performance and safety | Rust | Best control over latency, memory use, and safety-sensitive behavior |
| Fastest prototype | Python | Smallest time-to-first-server, minimal ceremony, easy experimentation |
| Existing Node-only stack | Node.js | Use only when the user explicitly requires it |

## Transport Selection

| Client Type | Transport |
|-------------|-----------|
| Local (Claude Desktop, VS Code) | `stdio` |
| Remote (Cursor, cloud) | Streamable HTTP |
| Backward compatibility | Legacy HTTP/SSE |

Keep server logic (tools + resources) independent of transport so you can plug in
either in the entrypoint.

</workflow>

## When to Use

- Implementing a new MCP server
- Selecting between Go, Rust, Python, or an explicitly requested Node.js server
- Adding tools or resources to an existing server
- Choosing between stdio vs HTTP transport
- Debugging MCP registration or transport issues
- Upgrading the MCP SDK version

## Core Concepts

<mcp-concepts>
- **Tools**: Actions the model can invoke (e.g., search, run a command).
  Register with `server.tool()` or `registerTool()` depending on SDK version.
- **Resources**: Read-only data the model can fetch (e.g., file contents, API responses).
  Register with `server.resource()` or `registerResource()`.
- **Prompts**: Reusable, parameterized prompt templates the client can surface.
  Register with `server.prompt()` or equivalent.
- **Transport**: stdio for local clients (Claude Desktop, VS Code);
  Streamable HTTP for remote clients (Cursor, cloud).
</mcp-concepts>

## Server Setup

**API Stability Warning**: MCP SDK APIs are evolving quickly. The examples below are
minimal current patterns, but method names, decorators, and import paths can change
between major versions. Verify the exact API against the version you install.

### Go

| Item | Guidance |
|------|----------|
| Default fit | Reliable, performant production server |
| Packaging | Single deployable binary |
| Install | `go get github.com/modelcontextprotocol/go-sdk@latest` |
| Tool registration pattern | `mcp.AddTool()` |
| Notes | Official SDK; verify exact signatures against the installed version |

```go
package main

import (
    "context"
    "log"

    "github.com/modelcontextprotocol/go-sdk/mcp"
)

type AddParams struct {
    A int `json:"a" jsonschema:"first number"`
    B int `json:"b" jsonschema:"second number"`
}

type AddResult struct {
    Sum int `json:"sum"`
}

func add(
    ctx context.Context,
    req *mcp.CallToolRequest,
    input AddParams,
) (*mcp.CallToolResult, AddResult, error) {
    return nil, AddResult{Sum: input.A + input.B}, nil
}

func main() {
    server := mcp.NewServer(&mcp.Implementation{
        Name:    "my-go-server",
        Version: "1.0.0",
    }, nil)

    mcp.AddTool(server, &mcp.Tool{
        Name:        "add",
        Description: "Add two integers",
    }, add)

    if err := server.Run(context.Background(), &mcp.StdioTransport{}); err != nil {
        log.Fatal(err)
    }
}
```

### Rust

| Item | Guidance |
|------|----------|
| Default fit | Critical performance and security-sensitive services |
| Packaging | Single native binary |
| Install | Add `rmcp`, `tokio`, `serde`, `schemars`, and `anyhow` to `Cargo.toml` |
| Tool registration pattern | `#[tool]` with `#[tool_router]` |
| Notes | Official Rust SDK uses proc macros; pin the crate version |

```rust
use rmcp::{
    handler::server::wrapper::Parameters,
    schemars,
    tool,
    tool_router,
    transport::stdio,
    ServiceExt,
};

#[derive(Debug, serde::Deserialize, schemars::JsonSchema)]
struct AddParams {
    a: i32,
    b: i32,
}

#[derive(Clone)]
struct Calculator;

#[tool_router(server_handler)]
impl Calculator {
    #[tool(description = "Add two numbers")]
    fn add(&self, Parameters(AddParams { a, b }): Parameters<AddParams>) -> String {
        (a + b).to_string()
    }
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let service = Calculator.serve(stdio()).await?;
    service.waiting().await?;
    Ok(())
}
```

### Python

| Item | Guidance |
|------|----------|
| Default fit | Rapid prototyping and fast iteration |
| Packaging | Script or module execution with a Python runtime |
| Install | `pip install "mcp[cli]"` |
| Tool registration pattern | `@mcp.tool()` via `FastMCP` |
| Notes | Prefer the stable v1.x API unless you intentionally target v2 |

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-python-server")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


if __name__ == "__main__":
    mcp.run()
```

## Resource Registration Pattern

After the first tool works, add resources and prompts using the equivalent API in the
selected SDK. Keep handlers deterministic, return structured errors, and avoid mixing
transport concerns into the business logic.

## stdio Transport (Local)

Use `stdio` first for local development and validation. It keeps the initial feedback
loop short and matches the most common local MCP client integrations.

## VS Code mcp.json Configuration

```json
{
  "servers": {
    "my-go-server": {
      "type": "stdio",
      "command": "./bin/my-go-server"
    },
    "my-rust-server": {
      "type": "stdio",
      "command": "./target/release/my-rust-server"
    },
    "my-python-server": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "my_server"]
    }
  }
}
```

If the user explicitly requests Node.js, configure it as a deliberate exception rather
than the default path.

## Best Practices

<mcp-rules>
- **Language choice first**: Decide Go, Rust, or Python before discussing SDK details.
- **Smallest working tool first**: Register one tool, validate it, then expand the server.
- **Structured errors**: Return structured error messages the model can interpret; avoid raw stack traces.
- **Idempotency**: Prefer idempotent tools where possible so retries are safe.
- **Rate and cost awareness**: For tools that call external APIs, consider rate limits and cost; document them in the tool description.
- **Versioning**: Pin the MCP SDK version and check release notes before upgrading.
- **Transport separation**: Keep tool/resource logic separate from transport so you can swap `stdio` and HTTP without changing business logic.
</mcp-rules>

## Official Resources

- [Official MCP SDK references](./references/URIs.md)
- [Language selection checklist](./assets/language-selection-checklist.md)
