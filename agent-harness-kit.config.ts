import { defineHarness } from '@cardor/agent-harness-kit';

export default defineHarness({
  project: {
    name: 'everything-copilot',
    description: 'GitHub Copilot-first workflow workspace with AHK orchestration, GitNexus impact analysis, and Graphify semantic memory.',
    docsPath: './.github',
  },
  provider: 'claude-code',
  agents: {
    lead: {
      instructionsPath: null,
      context: 'Use the authoritative PLAN and orchestrator workflow as the strategic source of truth.',
    },
    explorer: {
      instructionsPath: null,
      context: 'Explore the workspace before changes and stay anchored to the docs, prompts, skills, scripts, and MCP configuration surfaces.',
      allowedPaths: ['./.github', './scripts', './tools', './README.md', './pyproject.toml', './.vscode'],
    },
    builder: {
      instructionsPath: null,
      context: 'Implement approved changes while keeping PLAN and README aligned with the actual workspace state.',
      writablePaths: ['./'],
    },
    reviewer: {
      instructionsPath: null,
      context: 'Validate behavior with focused checks and make sure README and PLAN match the implemented system.',
    },
    custom: [],
  },
  storage: {
    dir: '.harness',
    tasks: {
      adapter: 'local',
    },
    sections: {
      toolsUsed: true,
      filesModified: true,
      result: true,
      blockers: true,
      nextSteps: true,
    },
    markdownFallback: {
      enabled: true,
      path: '.harness/current.md',
    },
  },
  database: {
    type: 'sqlite',
    path: '.harness/harness.db',
  },
  health: {
    scriptPath: './health.sh',
    required: true,
  },
  tools: {
    mcp: {
      enabled: true,
      port: 3742,
    },
    scripts: {
      enabled: false,
      outputDir: './.harness/scripts',
    },
  },
});