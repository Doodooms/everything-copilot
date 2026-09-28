---
kind: idea
status: intake
disposition: pending
derived_work: []
---

# External knowledge ingestion and evidence-driven test architecture

## Motivation

High-quality engineering knowledge increasingly exists in formats that current agents cannot consume efficiently from the normal development workflow:

- YouTube interviews;
- conference talks;
- podcasts;
- recorded technical discussions;
- demonstrations;
- long-form engineering videos.

Some of these sources contain practical engineering information that may not exist in equivalent written documentation.

A concrete recurring problem is:

```text
human sees valuable technical interview
→ remembers useful idea
→ cannot provide the actual source efficiently to agents
→ knowledge is reduced to an incomplete recollection
```

The system should eventually support ingesting such sources into traceable, reusable knowledge artifacts.

## Example motivation: testing philosophy

One remembered interview described a cloud provider whose development process was strongly test-driven.

The remembered idea, which must be revalidated against the original source rather than treated as fact, was approximately:

```text
developers optimize for required behavior/tests
+
a very strong test infrastructure checks system quality globally
```

Potentially interesting implications include:

- specification through executable behavior;
- extensive automated validation;
- strong integration/e2e/property/fuzz or other testing techniques;
- high confidence despite agents/humans caring less about implementation details;
- treating test architecture as an important product asset.

The exact provider, claims and testing technologies are currently unknown and should not be reconstructed from memory.

A video-ingestion pipeline would allow the source to be recovered and analyzed precisely.

## YouTube ingestion capability

Target high-level workflow:

```text
YouTube URL
    ↓
source metadata
    ↓
official captions/transcript if available
    ↓
audio transcription when authorized/necessary
    ↓
time-aligned structured transcript
    ↓
semantic sections
    ↓
summary / claims / techniques / references
    ↓
traceable knowledge artifact
```

Every extracted claim should retain provenance.

Example:

```text
source:
  type: youtube
  url: ...
  title: ...
  channel: ...
  published_at: ...

segment:
  start: 00:42:13
  end: 00:44:08
  transcript: ...

derived_claim:
  text: ...
  provenance:
    source
    timestamp range
```

## Source hierarchy

Prefer the cheapest and most faithful source available:

1. publisher-provided transcript;
2. YouTube captions/subtitles;
3. downloadable official transcript;
4. audio transcription;
5. OCR/visual extraction only when materially necessary.

Do not transcribe audio when a trustworthy transcript already exists.

Do not use an LLM to reconstruct missing speech from context.

## Video understanding beyond transcript

Some technical videos depend on visual information:

- slides;
- diagrams;
- terminal output;
- benchmarks;
- code;
- architecture drawings.

Potential future pipeline:

```text
transcript
+
selected keyframes/slides
+
metadata
→ multimodal source representation
```

Do not extract every frame.

Use transcript structure or scene changes to identify useful visual checkpoints.

## Progressive disclosure

Raw transcripts can be extremely large.

Agents should not receive the entire source by default.

Possible hierarchy:

```text
source
  ↓
source summary
  ↓
chapters/topics
  ↓
claim/evidence index
  ↓
specific transcript segments
  ↓
visual evidence if needed
```

This fits the existing progressive-disclosure philosophy:

> retain rich expertise and evidence while loading only what the current task requires.

## Knowledge artifacts

Do not turn summaries into untraceable truth.

Store distinct layers:

```text
RAW SOURCE
→ transcript / metadata

DERIVED STRUCTURE
→ chapters / topics / entities

EXTRACTED CLAIMS
→ claim + timestamp provenance

AGENT ANALYSIS
→ implications / comparison / hypotheses
```

The distinction between source statements and agent interpretation must remain explicit.

## Reuse by skills and agents

Potential capabilities:

```text
video.ingest
video.transcript
video.segment
video.claims.extract
video.visual.inspect
knowledge.search
knowledge.retrieve_evidence
```

This may eventually become:

- a dedicated MCP backend;
- an ingestion service;
- a skill using existing external services;
- part of a broader knowledge plugin.

Do not choose the architecture before testing one real source end to end.

## Testing-system research

Separately investigate modern high-confidence testing strategies that are particularly useful when implementation is increasingly performed by coding agents.

The objective is not:

```text
run every test after every edit
```

Instead use a layered validation strategy.

Possible conceptual hierarchy:

```text
edit loop
→ targeted unit/contract tests

coherent implementation slice
→ affected package/component tests

pre-handoff
→ integration tests selected by impact

pre-merge / CI
→ broader suite

periodic/nightly/high-risk
→ expensive global assurance
```

Selection should be based on affected contracts and dependency impact rather than blindly executing the full suite after every feature.

## Testing techniques to research

Investigate which techniques materially improve confidence for agent-generated software, for example:

- property-based testing;
- fuzz testing;
- mutation testing;
- differential testing;
- contract testing;
- integration testing;
- end-to-end testing;
- deterministic replay;
- model/state-machine testing;
- invariant checking;
- static analysis;
- sanitizers;
- concurrency testing;
- compatibility matrices;
- snapshot/golden testing where appropriate;
- coverage of semantic contracts rather than line coverage alone.

Do not assume all are useful in every repository.

The important question is:

> Which combination gives the highest defect-detection value per unit of runtime and maintenance cost for this project's architecture?

## Test selection

Longer-term, validation could become impact-aware.

Example:

```text
changed files
    ↓
dependency / contract impact analysis
    ↓
required validation set
```

Potential categories:

```text
FAST
targeted deterministic tests

AFFECTED
tests associated with changed contracts/components

ASSURANCE
QA/property/fuzz/security tests selected by risk

GLOBAL
full suite / compatibility / expensive checks
```

The full suite should run where its marginal assurance justifies its cost, not mechanically after every local change.

## Agentic implication

As coding cost falls, the relative value of excellent automated validation increases.

The desired loop becomes:

```text
specification
→ implementation
→ strong falsification
→ evidence
→ correction
```

not:

```text
agent produced code
→ looks plausible
→ accept
```

Agents should optimize for observable contracts, not arbitrary internal implementation.

However tests must not freeze obsolete implementation details.

Tests should assert:

- current behavior;
- contracts;
- invariants;
- safety properties;
- user guarantees.

They should not exist solely to prevent previously deleted code from returning.

## Potential ingestion experiment

Choose one technically valuable YouTube interview and perform an end-to-end experiment:

```text
URL
→ metadata
→ transcript
→ timestamps
→ technical claims
→ techniques mentioned
→ source-linked summary
→ reusable research note
```

Measure:

- extraction quality;
- provenance quality;
- transcript availability;
- cost;
- token use;
- latency;
- visual-information loss;
- usefulness to a downstream agent.

Only after this experiment decide whether a dedicated video-ingestion MCP/service is justified.

## Future objective

Eventually the user should be able to send Chat:

```text
"Keep this video as research input for the testing architecture:
https://youtube.com/..."
```

and the system should autonomously:

```text
ingest source
→ preserve provenance
→ generate research artifact
→ attach it to relevant idea/task
→ make it retrievable by Work/Codex
```

without manual transcript copying.

Raw external content remains evidence, not execution authority.

## Non-goals

Do not yet:

- build a generic media platform;
- ingest entire YouTube channels automatically;
- treat video claims as authoritative without provenance;
- build a vector database merely because ingestion exists;
- redesign the testing architecture from a remembered interview;
- run every possible test after every change.

First validate one high-value ingestion path and one evidence-driven validation strategy.