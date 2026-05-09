---
name: deep-research
description: "Multi-source deep research workflow. Searches the web, synthesizes findings, and delivers cited reports with source attribution. Use when: thorough research on any topic with evidence and citations is needed. Best with firecrawl or exa MCP; falls back to fetch_webpage tool. Derived from Everything Claude Code (https://github.com/affaan-m/everything-claude-code)."
---

# Deep Research

Produce thorough, cited research reports from multiple web sources.

## MCP Requirements (Optional but Recommended)

- **firecrawl** -- `firecrawl_search`, `firecrawl_scrape`, `firecrawl_crawl`
- **exa** -- `web_search_exa`, `web_search_advanced_exa`, `crawling_exa`

Without these MCPs, use the `fetch_webpage` tool with multiple URLs in parallel.

## When to Activate

- User asks to research any topic in depth
- Competitive analysis, technology evaluation, or market sizing
- Any question requiring synthesis from multiple sources
- User says "research", "deep dive", "investigate", or "what's the current state of"

## Workflow

### Step 1: Understand the Goal

Ask 1-2 quick clarifying questions:
- "What's your goal -- learning, making a decision, or writing something?"
- "Any specific angle or depth you want?"

If the user says "just research it" -- skip ahead with reasonable defaults.

### Step 2: Plan the Research

Break the topic into 3-5 research sub-questions.

Example:
- Topic: "Impact of AI on software development"
  - What AI tools are widely adopted today?
  - What productivity gains have been measured?
  - What are the main risks and limitations?
  - What companies/products are leading this space?
  - What is the market size and growth trajectory?

### Step 3: Execute Multi-Source Search

For EACH sub-question, search using available tools:

**With firecrawl MCP:**
```
firecrawl_search(query: "<sub-question keywords>", limit: 8)
```

**With exa MCP:**
```
web_search_exa(query: "<sub-question keywords>", numResults: 8)
web_search_advanced_exa(query: "<keywords>", numResults: 5, startPublishedDate: "2025-01-01")
```

**Without MCPs (fallback):**
```
fetch_webpage(urls: ["<url1>", "<url2>", ...], query: "<sub-question>")
```

**Search strategy:**
- Use 2-3 different keyword variations per sub-question
- Mix general and news-focused queries
- Aim for 15-30 unique sources total
- Prioritize: academic, official, reputable news > blogs > forums

### Step 4: Deep-Read Key Sources

For the most promising URLs, fetch full content:

**With firecrawl:** `firecrawl_scrape(url: "<url>")`
**With exa:** `crawling_exa(url: "<url>", tokensNum: 5000)`
**Fallback:** `fetch_webpage(urls: ["<url>"], query: "<sub-question>")`

Read 3-5 key sources in full for depth. Do not rely only on search snippets.

### Step 5: Synthesize and Write Report

```markdown
# [Topic]: Research Report
*Generated: [date] | Sources: [N] | Confidence: [High/Medium/Low]*

## Executive Summary
[3-5 sentence overview of key findings]

## 1. [First Major Theme]
[Findings with inline citations]
- Key point ([Source Name](url))
- Supporting data ([Source Name](url))

## 2. [Second Major Theme]
...

## Key Takeaways
- [Actionable insight 1]
- [Actionable insight 2]
- [Actionable insight 3]

## Sources
1. [Title](url) -- [one-line summary]
2. ...

## Methodology
Searched [N] queries. Analyzed [M] sources.
Sub-questions investigated: [list]
```

### Step 6: Deliver

- **Short topics**: Post the full report in chat
- **Long reports**: Post executive summary + key takeaways, save full report to a file

## Parallel Research with Subagents

For broad topics, launch research subagents in parallel:

```
1. Subagent 1: Research sub-questions 1-2
2. Subagent 2: Research sub-questions 3-4
3. Subagent 3: Research sub-question 5 + cross-cutting themes
```

Each subagent searches, reads sources, and returns findings. The main session
synthesizes into the final report.

## Quality Rules

<research-rules>
1. **Every claim needs a source.** No unsourced assertions.
2. **Cross-reference.** If only one source says it, flag as unverified.
3. **Recency matters.** Prefer sources from the last 12 months.
4. **Acknowledge gaps.** If you could not find good info on a sub-question, say so.
5. **No hallucination.** If you don't know, say "insufficient data found."
6. **Separate fact from inference.** Label estimates, projections, and opinions clearly.
</research-rules>
