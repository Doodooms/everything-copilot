---
name: mcp-server-patterns
description: "Choose and build MCP servers with Go, Rust, or Python first. Use when: implementing a new MCP server, selecting the language and transport, adding tools or resources."
user-invocable: false
disable-model-invocation: false
---

# MCP Server Patterns

Use this skill to choose the right MCP server language before writing code. Default to
Go for production-ready deployments, move to Rust when performance or security is
critical, and use Python for rapid prototyping. Treat Node.js as an exception, not
the baseline. For official SDK links, see #file:./references/URIs.md and the
[language selection checklist](./assets/language-selection-checklist.md).

> The SDK API evolves. Check [modelcontextprotocol.io](https://modelcontextprotocol.io)
> or query Context7 for "MCP" to get current method signatures.

<rules>
- Select the implementation language from the user's operational goals first:
  - Go is the default choice for a reliable, performant server that ships as a single deployable binary with minimal runtime dependencies.
  - Rust is the preferred choice when peak performance, tight resource control, and memory safety are critical requirements.
  - Python is recommended for rapid prototyping, experiments, and fast iteration.
- Node.js must only be used if the user formally requests it, due to its heaviness.
- If the user's constraints are unclear, use #tool:vscode/askQuestions to clarify deployment target, performance envelope, security sensitivity, and iteration speed before recommending a language.
- Prefer official SDKs and pin versions. MCP SDK APIs evolve quickly; always verify the installed version's docs before coding.
- Keep tool, resource, and prompt logic independent from transport so `stdio` and Streamable HTTP can be swapped at the entrypoint.
- Start from the smallest tool registration that proves the SDK wiring works before adding resources, auth, or business logic.
</rules>

<workflow>

## Step 1 - Choose the language

Use this decision order:
- Default to Go for most production servers.
- Upgrade to Rust when low latency, low memory usage, or stronger safety guarantees dominate.
- Choose Python when speed of delivery matters more than raw performance.
- Only keep or propose Node.js when the user formally requests Node.js or must integrate with an existing Node-only codebase.

## Step 2 - Choose the transport

Use `stdio` for local integrations such as VS Code, Claude Desktop, and local agent tooling.
Use Streamable HTTP for remote or hosted deployments.
Keep the transport at the entrypoint only.

## Step 3 - Start from the smallest working server

Pick one of the language setup blocks below, register a single tool, validate it over `stdio`, then expand to resources, prompts, and HTTP transport as needed.

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
- **Operational fit**: Prefer Go for general deployment, Rust for critical performance and safety, Python for fast prototypes.
- **Node.js exception**: Node.js must only be used if the user formally requests it, due to its heaviness.
</mcp-rules>

## Official Resources

- [Official MCP SDK references](./references/URIs.md)
- [Language selection checklist](./assets/language-selection-checklist.md)
