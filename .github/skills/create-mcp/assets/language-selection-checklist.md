# MCP Language Selection Checklist

## Purpose

- Use this file only while choosing the implementation language and packaging strategy.
- Finish with one explicit decision: language, reason, transport target, package manager, and the first validation command.

## Go

- Choose Go when the user needs the safest default for production-oriented servers, strong performance, and a single deployable binary.
- Choose Go when the server may need both local `stdio` and remote HTTP entrypoints without pulling in a heavier runtime.
- Avoid Go when the team explicitly needs the fastest iteration loop and is already standardized on Python.
- Avoid Go when the surrounding host ecosystem is already locked to Node.js or another language.

## Rust

- Choose Rust when memory control, low latency, or a tighter security posture is a primary constraint.
- Choose Rust when the server will run in a constrained environment or must keep a small and predictable runtime footprint.
- Avoid Rust when the main goal is to produce a working internal tool as quickly as possible.
- Avoid Rust when the team cannot realistically maintain Rust code after the initial delivery.

## Python

- Choose Python when the user wants the fastest path to a working MCP server, especially for internal tools, orchestration, or data access.
- Choose Python when the repository already ships Python tooling or the server logic depends on Python libraries.
- Avoid Python when startup cost, packaging into a single binary, or tighter runtime control is a hard requirement.
- Avoid Python when the task requires a language already mandated by the surrounding host ecosystem.

## Node.js exception

- Choose Node.js only when the user explicitly requests it, the repository is already TypeScript or Node-first, or the MCP server must live inside an existing JavaScript runtime boundary.
- Use the TypeScript SDK when you take this path; treat Node.js as a compatibility or ecosystem decision, not the default recommendation.
- Avoid Node.js when the only reason is personal familiarity. That is not a strong enough constraint.

## Cross-cutting checks

- Choose the language before you choose the exact SDK example.
- Decide transport separately: `stdio` for local editor or desktop clients, Streamable HTTP for remote deployments, or both if the contract requires both.
- Pin the SDK version before you write examples because MCP APIs evolve quickly.
- Use [URIs](../references/URIs.md) to open the official repository or docs for the selected SDK.
- If no language is mandated and the task is production-oriented, default to Go.
- If no language is mandated and speed of delivery dominates, default to Python.
- If performance or security constraints dominate, escalate Rust.