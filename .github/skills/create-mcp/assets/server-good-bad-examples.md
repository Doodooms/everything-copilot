# Good and Bad MCP Server Examples

## Purpose

- Use these comparisons when you need to sanity-check the server draft before validation.
- Reject the bad pattern instead of copying it and hoping validation will catch it later.

## Capability scope

Bad:

- "This server will expose tools, resources, prompts, and auth." Only one demo tool is implemented and the rest are left as TODOs.

Good:

- Either narrow the contract before coding, or implement the exact declared capability set in the same edit slice.

## Tool design

Bad:

```ts
server.tool("search", async (input) => runSearch(input as any));
```

Good:

```ts
server.tool(
  "search_docs",
  {
    query: z.string().min(1),
    limit: z.number().int().positive().default(5),
  },
  async ({ query, limit }) => makeSearchResult(await searchDocs(query, limit)),
);
```

- The good version names the tool precisely, validates input, and keeps business logic outside the transport bootstrap.

## Transport boundary

Bad:

```python
@mcp.tool()
def sync_repo(repo: str) -> str:
    transport = build_http_transport(os.environ["API_URL"])
    return transport.sync(repo)
```

Good:

```python
def sync_repo_service(repo: str, client: RepoClient) -> str:
    return client.sync(repo)


@mcp.tool()
def sync_repo(repo: str) -> str:
    return sync_repo_service(repo, repo_client)
```

- The good version keeps handler logic reusable and transport wiring thin.

## Secrets and configuration

Bad:

```json
{
  "servers": {
    "payments": {
      "type": "stdio",
      "command": "node",
      "args": ["server.js", "--token", "live-secret-value"]
    }
  }
}
```

Good:

```json
{
  "servers": {
    "payments": {
      "type": "stdio",
      "command": "node",
      "args": ["server.js"],
      "env": {
        "PAYMENTS_TOKEN": "${input:paymentsToken}"
      }
    }
  }
}
```

- The good version keeps secrets out of the command line and lets the host provide them safely.

## Capability choice

Bad:

- Expose a mutating tool when the user only needs read-only documentation or data.

Good:

- Use a resource for read-only context, a prompt for reusable workflows, a tool for invocable actions, and an app only when the client benefits from interactive UI.

## Node.js selection

Bad:

- Choose Node.js because it feels familiar even though the request did not ask for it and the repository is not Node-first.

Good:

- Choose Node.js only because the user explicitly requested it or the surrounding system already requires the TypeScript ecosystem.