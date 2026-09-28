# WebMCP — Structured Web Execution Backend for the Control-Plane

## Status

Exploratory idea.

Do not implement before the current Control-Plane → Gateway → backend execution path is proven in runtime.

The purpose of this document is to preserve the architectural ideas around WebMCP for later evaluation.

---

# 1. What WebMCP is

WebMCP is an emerging Web Platform proposal that allows websites to expose structured tools directly to browser-based agents.

Instead of forcing an agent to infer actions from:

- screenshots;
- DOM inspection;
- accessibility trees;
- arbitrary click/type/navigation loops;

the website can explicitly expose callable tools representing meaningful actions.

Conceptually:

```text
Website
    ↓
WebMCP tool registration
    ↓
Browser exposes typed tools
    ↓
Agent invokes structured action
```

Example:

```text
search_products(query)
add_to_cart(product_id)
submit_form(...)
book_slot(...)
```

instead of:

```text
inspect DOM
→ reason
→ click
→ inspect
→ type
→ inspect
→ click
→ ...
```

WebMCP is therefore best understood as a structured execution interface attached to a browser/page context.

It is not merely "another MCP server."

---

# 2. Main architectural value

The strongest potential value is not convenience.

It is the reduction of reasoning complexity required from the harness.

Without WebMCP, generic browser interaction often requires:

```text
visual understanding
+
DOM understanding
+
interaction planning
+
state tracking
+
repeated observation
```

With WebMCP, the problem can become:

```text
discover a small set of typed tools
→ choose the right tool
→ provide structured arguments
→ consume structured result
```

This can reduce:

- token consumption;
- model reasoning requirements;
- number of interaction steps;
- fragility caused by layout changes;
- ambiguity in action selection;
- dependence on screenshots;
- dependence on arbitrary DOM structure.

This directly matches the Control-Plane objective of reducing required harness intelligence by increasing architectural structure.

---

# 3. Relationship with MCP

WebMCP should not be treated as a replacement for the existing MCP Gateway.

The two operate at different levels.

Traditional MCP / backend tool path:

```text
Control-Plane
    ↓
Gateway
    ↓
MCP server / API / backend
```

WebMCP path:

```text
Control-Plane
    ↓
Web execution backend
    ↓
Browser
    ↓
Current website/page
    ↓
WebMCP tools
```

A possible future architecture:

```text
                     Control-Plane
                           │
                   capability routing
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
      MCP Gateway      Web Backend        Codex
          │                │
          ▼                ▼
      MCP Servers       Browser
                           │
                           ▼
                        WebMCP
```

The Gateway may eventually mediate WebMCP access as well, but this should not be assumed before testing a real implementation.

---

# 4. WebMCP as an intermediate execution layer

A useful long-term capability hierarchy for Web operations is:

```text
HIGH STRUCTURE
LOW REQUIRED INTELLIGENCE

native API
    ↓
MCP
    ↓
WebMCP
    ↓
DOM / accessibility automation
    ↓
visual Computer Use

LOW STRUCTURE
HIGH REQUIRED INTELLIGENCE
```

This is not a fixed routing order.

The Control-Plane should eventually choose based on:

- observed reliability;
- authorization;
- cost;
- latency;
- required capabilities;
- available context;
- execution constraints.

But WebMCP introduces a highly useful middle layer between structured APIs and generic browser automation.

---

# 5. Potential routing model

A Task may require:

```text
required_capability:
    reservation.create
```

The Control-Plane may discover:

```text
Backend A
type: MCP
capability: reservation.create
status: observed

Backend B
type: WebMCP
capability: reservation.create
status: observed

Backend C
type: generic browser
capability: browser.interact
status: observed
```

Routing should then select the cheapest sufficient and authorized execution path.

Possible decision factors:

```text
capability match
+
authorization
+
historical success
+
token cost
+
latency
+
interaction count
+
execution reliability
+
required human confirmation
```

This fits naturally with future capability-based routing.

---

# 6. Relationship with System One routing

WebMCP is especially interesting in relation to low-cost "System One" routing.

Generic browser automation gives the model a large action space:

```text
hundreds of DOM elements
+
visual interpretation
+
navigation state
+
multiple possible interaction strategies
```

WebMCP can reduce that to:

```text
5–20 typed tools
```

The decision problem changes from:

```text
"Understand this arbitrary interface
and figure out how to accomplish X."
```

to:

```text
"Which of these typed actions satisfies X?"
```

The second problem can potentially be handled by:

- smaller models;
- cheap classifiers;
- lightweight semantic routers;
- deterministic matching;
- System One components.

This suggests an important future direction:

> Reduce required model intelligence by reducing execution ambiguity.

This may have greater long-term leverage than simply switching to cheaper LLMs.

---

# 7. Security model

WebMCP tool discovery must never imply authorization.

Core invariant:

```text
DISCOVERED != AUTHORIZED
```

A website may expose:

```text
delete_account()
transfer_money(...)
publish(...)
send_message(...)
```

but tool visibility alone must not permit execution.

Possible flow:

```text
WebMCP discovery
    ↓
CapabilityObservation
    ↓
Control-Plane ResourceGrant
    ↓
AuthorizationDecision
    ↓
Attempt
    ↓
execution
```

The Control-Plane must remain authoritative.

---

# 8. Declared safety metadata is not policy

WebMCP supports tool metadata/annotations indicating properties such as:

```text
read-only
consequential
```

These are useful as evidence.

They are not authoritative security decisions.

Correct interpretation:

```text
website declares tool read-only
→ documented/declared property
```

Not:

```text
website declares tool read-only
→ automatically safe
```

The architecture should preserve the distinction:

```text
declared
documented
inferred
observed
authorized
```

---

# 9. Prompt injection and untrusted tool descriptions

Tool manifests/descriptions and outputs must be considered untrusted data.

Threat classes include:

```text
malicious tool description
malicious argument descriptions
malicious tool output
third-party content embedded in result
cross-origin injected content
```

A browser-based backend must therefore treat WebMCP metadata similarly to external MCP tool metadata:

```text
untrusted input
→ normalization
→ policy
→ authorization
→ execution
```

Never allow website-provided text to redefine Control-Plane policy.

---

# 10. Reuse of authenticated browser sessions

A major WebMCP benefit is that execution occurs within an existing browser context.

Conceptually:

```text
User browser session
    ↓
authenticated website
    ↓
WebMCP tool
    ↓
agent execution
```

Potentially useful for:

- SaaS applications;
- e-commerce;
- dashboards;
- booking websites;
- internal enterprise tools;
- authenticated web administration;
- user-specific portals.

This can avoid recreating authentication inside every MCP server.

However, it increases the importance of authorization, because the browser session may already have broad privileges.

---

# 11. Capability observations

A future Control-Plane representation could look like:

```text
CapabilityObservation {
    backend_id,
    origin,
    capability,
    status,
    evidence_ref,
    observed_at,
    observed_against_version
}
```

Example:

```text
backend_id:
    chrome-webmcp

origin:
    example.com

capability:
    booking.create

status:
    observed
```

Important:

```text
observed capability
!=
authorized capability
```

Observations describe what a backend appears able to do.

ResourceGrants describe what a Task is permitted to do.

---

# 12. Execution evidence

A WebMCP Attempt should eventually generate deterministic evidence similar to other backends:

```text
Attempt
├── origin
├── page/context identifier
├── WebMCP tool
├── arguments hash
├── result reference
├── authorization decision
├── execution timestamp
├── tool metadata version
└── outcome
```

Avoid storing large page content unnecessarily.

Prefer durable references and provenance.

---

# 13. Relationship with Plugin Factory

There may eventually be opportunities to project canonical capability definitions into WebMCP.

Possible future shape:

```text
canonical tool definition
        │
        ▼
Plugin Factory
   ┌────┼─────────────┐
   ▼    ▼             ▼
 MCP  WebMCP       harness projection
```

However, do not introduce a universal tool abstraction prematurely.

Important semantic differences may exist between:

```text
server-side tool
```

and:

```text
page-contextual browser action
```

Examples:

```text
repository.read_file
```

versus:

```text
add_current_product_to_cart
```

They differ in:

- lifecycle;
- authentication;
- context;
- state;
- trust boundary;
- execution location.

Validate one real WebMCP backend before generalizing the Plugin Factory model.

---

# 14. Potential relevance to NutriSolver

For applications controlled by us, WebMCP could eventually provide an agent-accessible interface without forcing all interactions through UI automation.

Possible NutriSolver examples:

```text
create_plan(...)
add_food(...)
list_plans(...)
load_recipe(...)
publish_recipe(...)
```

For browser-first V0–V2, this could be especially interesting because it preserves browser-local application behavior.

However:

- private nutrition information must remain private by default;
- WebMCP exposure must not silently increase discoverability;
- no implicit recommendation behavior should be introduced;
- tools must respect the same explicit quantity semantics as the UI.

No implementation should be started until the underlying product architecture requires it.

---

# 15. Potential backend abstraction

Do not create this abstraction yet, but a future backend could conceptually expose:

```text
WebExecutionBackend
```

with capabilities such as:

```text
web.tool.discover
web.tool.invoke
web.page.navigate
web.session.use
```

Then individual implementations could include:

```text
webmcp.chrome
browser.dom
browser.computer_use
```

Only introduce this after validating one real implementation.

---

# 16. Experimental plan for later

A future experiment should be small and controlled.

Example:

```text
WEBMCP_BACKEND_EXPERIMENT
```

Goal:

Compare execution of one deterministic browser task using:

```text
A. WebMCP
B. DOM/accessibility automation
C. visual Computer Use
```

Measure:

```text
success rate
token usage
model calls
tool calls
latency
retries
human interventions
failure modes
```

Do not evaluate only whether WebMCP works.

Evaluate whether it actually reduces execution complexity.

---

# 17. Important architectural invariants

Preserve:

```text
WebMCP discovery != authorization
```

```text
declared tool safety != observed safety
```

```text
browser session access != permission to use all session capabilities
```

```text
WebMCP capability belongs to backend/execution context,
not permanently to Task
```

```text
runtime evidence > static schema
```

```text
fallback execution must be explicit
```

If WebMCP is unavailable and generic browser automation is used:

```text
execution_mode = fallback
```

Do not report the fallback as native WebMCP support.

---

# 18. Recommended timing

Do not implement now.

Current higher-priority sequence:

```text
Control-Plane durable model
→ authorization
→ Gateway enforcement
→ GitHub runtime proof
→ Control-Plane / Gateway integration
→ first real multi-harness execution
```

After those are proven, WebMCP becomes a good candidate for a new execution backend experiment.

---

# 19. Main idea to retain

WebMCP matters because it can reduce the amount of intelligence required to operate the Web.

The long-term Control-Plane should not merely answer:

```text
"Should this task run in Work or Codex?"
```

It should increasingly answer:

```text
"What is the cheapest, safest, sufficiently structured,
observed and authorized representation of this action?"
```

Possible answer:

```text
API
MCP
WebMCP
DOM automation
Computer Use
```

The harness then remains a property of the Attempt rather than the center of the architecture.