# Karpathy LLM OS Principles

Source: Andrej Karpathy -- Intro to LLMs (Nov 2023), YC AI Startup School (Jun 2025),
2025 Year in Review (Dec 2025), karpathy.bearblog.dev
Supplemented by: Lilian Weng, "LLM Powered Autonomous Agents" (Jun 2023)

## The LLM OS Architecture

```
+------------------------------------------+
|              LLM (CPU/Kernel)            |
|  - Reasoning, planning, orchestration   |
+------------------------------------------+
     |              |              |
[Context Window]  [KV Cache]  [Weights]
(RAM/working mem) (CPU cache) (ROM/long-term)
     |              |              |
+--------+    +----------+   +-----------+
|External|    |Tool Calls|   |Multiproc  |
|Storage |    |(I/O devs)|   |(agents)   |
|VectorDB|    |Browser   |   |Parallel   |
|Files   |    |Python    |   |LLM calls  |
|DBs     |    |APIs/bash |   |           |
+--------+    +----------+   +-----------+
```

## Memory Taxonomy (Karpathy + Weng synthesis)

| Speed    | Type        | Implementation                          |
|----------|-------------|------------------------------------------|
| Fastest  | In-weights  | Model parameters (baked-in knowledge)    |
|          | In-cache    | KV cache (ephemeral, session-scoped)     |
|          | In-context  | Context window = working memory          |
| Slowest  | External    | Files, DB, vector store = persistent     |

- **Episodic**: What happened? -> append-only event log, scored by recency+importance+relevance
- **Semantic**: What is true? -> model weights + RAG over knowledge base
- **Procedural**: How to do X? -> system prompts, SKILL.md files, fine-tuned workflows
- **Working**: What now? -> context window (finite, wiped each session)

## Autonomy Slider

```
HUMAN CONTROLLED <---------------------> FULLY AUTONOMOUS

Level 0: Human does everything, LLM is a lookup tool
Level 1: LLM suggests, human accepts/rejects each change
Level 2: LLM executes scoped tasks, human reviews diffs
Level 3: LLM executes multi-step workflows, human reviews checkpoints
Level 4: LLM runs autonomously with human monitoring only

Rule: Never jump levels without establishing trust at current level.
Rule: Always have a fast human-review loop.
Rule: Keep chunk size small -- large diffs create unverifiable surface area.
```

## Top 10 Actionable Principles

1. **Agency over Intelligence**: An agent that acts in small reversible steps and corrects
   is more valuable than one that reasons perfectly but acts slowly.

2. **Context is Working Memory -- Engineer It**: Every LLM call must receive a precisely
   curated context window. Build explicit context assembly logic.

3. **External Persistent Memory is Mandatory**: Context windows reset each session.
   Without an external memory store, every session starts blind.

4. **Autonomy Slider -- Start Partial**: Build human-in-the-loop first. Slide toward
   autonomy only as reliability is proven. Never ship full autonomy before trust is earned.

5. **Keep AI on a Leash -- Small Chunks**: Constrain output size. Scope tasks tightly.
   Verify each incremental step. Overactive agents create more bugs than they fix.

6. **Structured Tool Calls with Typed Schemas**: All tool invocations must use JSON schemas.
   Free-form tool calls are a primary failure mode. Validate tool output before injecting
   into next context.

7. **Make Everything LLM-Readable**: APIs, docs, and data sources consumed by agents must
   be in Markdown or structured JSON, not HTML or GUI-first formats.

8. **Orchestrate Specialist Agents via DAGs**: Complex tasks decompose into a DAG of
   specialist LLM calls. The orchestrator plans and routes; specialists execute.

9. **Prompt Injection is the Primary Security Threat**: Any external data entering the
   context window is a potential attack vector. Treat tool outputs as untrusted.

10. **Build for Agents Explicitly**: Software infrastructure designed for humans (GUIs,
    HTML, session cookies) does not work for agents. Provide programmatic access,
    machine-readable state, and action-oriented endpoints.

## ReAct Loop (canonical tool-use pattern)

```
Thought: I need to find X. I will search for it.
Action: browser_search(query="X")
Observation: [search results]
Thought: The results show Y. I can now compute Z.
Action: python_execute(code="compute_z(Y)")
Observation: Z = 42
Thought: I have the answer.
Final Answer: Z is 42
```

Key: Each Thought-Action-Observation triplet is one context-injected step.
Failure modes: hallucinated tool calls, infinite loops, context overflow.
