# Plugin Authoring Composition

The parent `plugin-engineering` workflow owns pack identity, capability scope, manifest integration, target validation, and the final handoff. Internal authoring workflows own only their bounded procedure. Every composed handoff MUST carry objective, relevant source requirements, constraints, expected output, and the exact parent resume point; validate the explicit return before continuing.

## use_case: author_plugin_with_optional_contributions

Select the `skill-authoring` workflow for each required skill package and `agent-authoring` only when a new pack-owned persona is needed. Delegate new MCP server code to Implementer with the `create-mcp` workflow; existing servers use their authoritative catalog. DevOps owns host configuration, installation, and deployment.

```mermaid
flowchart TD
    intake["Parent Step 1: fix pack identity, capabilities, targets"]
    scaffold["Parent: run expertise scaffold"]
    child_skill["Apply skill-authoring: create bounded skill package"]
    resume_skill["Parent: validate status/files; resume at manifest integration"]
    need_agent{"New pack-owned agent needed?"}
    child_agent["Apply agent-authoring: create bounded agent contract"]
    resume_agent["Parent: validate agent handoff; resume at manifest integration"]
    need_mcp{"New MCP implementation needed?"}
    child_mcp["Implementer applies create-mcp: implement deterministic server"]
    resume_mcp["Parent: validate server handoff; resume at pack projection"]
    join["Parent: integrate only successful child outputs"]
    test["Parent Step 3: validate, smoke-compile, build declared targets"]
    done["Return target paths, evidence, risks, blockers"]
    blocked["Stop and route failed, partial, or malformed child result"]

    intake --> scaffold --> child_skill --> resume_skill
    resume_skill -->|"valid return"| need_agent
    resume_skill -->|"invalid return"| blocked
    need_agent -->|"yes"| child_agent --> resume_agent
    need_agent -->|"no"| need_mcp
    resume_agent -->|"valid return"| need_mcp
    resume_agent -->|"invalid return"| blocked
    need_mcp -->|"yes"| child_mcp --> resume_mcp
    need_mcp -->|"no"| join
    resume_mcp -->|"valid return"| join
    resume_mcp -->|"invalid return"| blocked
    join --> test --> done
```

Each child returns control to its named parent resume node; the parent MUST NOT continue from an assumed implicit return. Optional branches terminate at the join and all routes end in either a validated build handoff or a blocker.

## use_case: compile_selected_targets_from_one_source

```mermaid
flowchart TD
    source["Canonical pack source"]
    validate["expertise validate"]
    test["expertise test: validate and smoke-compile declared targets"]
    select{"Declared targets"}
    portable["Build portable output"]
    copilot["Build Copilot output"]
    codex["Build Codex output and agent sidecars"]
    join["Collect paths, digests, diagnostics, and target gaps"]
    return["Parent returns exact outputs and Codex sidecar caveat"]
    blocked["Stop on any validation/build error; return exact diagnostics"]

    source --> validate
    validate -->|"valid"| test
    validate -->|"invalid"| blocked
    test -->|"all declared targets pass"| select
    test -->|"failure"| blocked
    select -->|"portable"| portable --> join
    select -->|"copilot"| copilot --> join
    select -->|"codex"| codex --> join
    join --> return
```

Build only targets declared in the manifest. When several targets are promised, every declared target must succeed before returning success.