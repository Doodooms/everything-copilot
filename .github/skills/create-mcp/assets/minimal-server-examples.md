# Minimal MCP Server Examples

## Purpose

- Use this asset after the language is chosen and you need a smallest-working-server starting point.
- Start with one tool over `stdio`, then expand to the rest of the declared capability set only after the first executable validation passes.
- Verify the exact SDK API against [URIs](../references/URIs.md) before copying one of these examples verbatim.

## Go

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

## Rust

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

## Python

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

## Node.js exception

```ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
  name: "my-node-server",
  version: "1.0.0",
});

server.tool(
  "add",
  {
    a: z.number(),
    b: z.number(),
  },
  async ({ a, b }) => ({
    content: [{ type: "text", text: String(a + b) }],
  }),
);

const transport = new StdioServerTransport();
await server.connect(transport);
```

## How to expand after the first tool works

- Add the rest of the declared capability set in the same language rather than mixing SDKs.
- Keep transport-specific wiring at the entrypoint so `stdio` and HTTP can be swapped without rewriting handlers.
- Promote reusable read-only context to resources, reusable workflows to prompts, and interactive UI to apps when the contract explicitly requires them.