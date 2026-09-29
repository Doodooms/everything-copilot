---
kind: research_input
status: triaged
disposition: research_required
derived_work: []
---

> **Design/research input — not an approved implementation plan.**

How to Stop Claude Code From Reading Your API Keys, SSH Keys, and Passwords (Exact Deny Rules)
Most people have no deny rules at all.
The ones who do have basic rules that miss 2 out of 3 ways secrets actually leak.
One security researcher found that deny rules are silently bypassed when commands contain more than 50 subcommands. No warning or log entry.
Here's the config that blocks all of them 👇
The 3 ways your secrets leak (most deny rules only block 1)
Leak 1: Direct file readClaude opens .env and reads it. This is the obvious one. A basic Read(**/.env*) deny rule blocks it.
Leak 2: Grep and searchClaude runs grep -r "STRIPE" . looking for a function name. The search hits your .env file. Your Stripe key appears in the grep output. The deny rule for Read never fired because Claude used Grep, not Read.
Leak 3: Runtime output captureClaude runs your tests. A failed HTTP request logs the full Authorization: Bearer sk-live-abc123... header. Claude captures all command output. Your secrets are now in the conversation without Claude ever opening a secret file.
Most deny rules only block Leak 1.
The critical vulnerability most people don't know about
In April 2026, security researchers at Adversa AI discovered that Claude Code's deny rules are silently bypassed when a command contains more than 50 subcommands.
An attacker's CLAUDE.md with 50+ build steps (normal for a monorepo) can hide a curl command at position 51 that exfiltrates your SSH keys. The deny rule for Bash(curl *) never fires. No warning, no log entry.
Anthropic has patched this in newer versions, but the lesson is clear: deny rules are a soft control, not a hard boundary. Layer your defenses.
Tier 1: Block direct file reads
Every rule below goes into ~/.claude/settings.json (global, protects every project) or .claude/settings.json (project-specific, shared with team via git).
The minimum every project needs:
json
{
  "permissions": {
    "deny": [
      "Read(**/.env*)",
      "Read(**/.dev.vars*)",
      "Read(**/*.pem)",
      "Read(**/*.key)",
      "Read(**/*.p12)",
      "Read(**/secrets/**)",
      "Read(**/credentials/**)",
      "Read(**/config/database.yml)",
      "Read(**/config/credentials.json)",
      "Read(**/.npmrc)",
      "Read(**/.pypirc)"
    ]
  }
}
This blocks Claude from opening these files directly. But it doesn't block Grep, Bash commands that output secrets, or environment variable access.
Tier 2: Block home directory secrets
These files live outside your project but Claude can read them because it inherits your user permissions:
json
{
  "permissions": {
    "deny": [
      "Read(**/.ssh/**)",
      "Read(**/.aws/**)",
      "Read(**/.azure/**)",
      "Read(**/.gcloud/**)",
      "Read(**/.docker/config.json)",
      "Read(**/.kube/config)",
      "Read(**/.gnupg/**)",
      "Read(**/.netrc)"
    ]
  }
}
Your SSH private keys, AWS credentials, Docker registry auth, Kubernetes cluster access, GPG keys, all blocked. One leaked SSH key = full access to your servers, GitHub repos, and CI/CD pipelines.
Tier 3: Block network exfiltration
Even if Claude reads a secret, it can't send it anywhere if you block outbound commands:
json
{
  "permissions": {
    "deny": [
      "Bash(curl *)",
      "Bash(wget *)",
      "Bash(nc *)",
      "Bash(ssh *)",
      "Bash(scp *)",
      "Bash(rsync *)",
      "Bash(ftp *)"
    ]
  }
}
Blocks curl, wget, netcat, ssh, scp, and rsync. If you need curl for your workflow (API testing), allow specific domains only:
json
{
  "permissions": {
    "allow": [
      "Bash(curl https://api.your-app.com/*)"
    ],
    "deny": [
      "Bash(curl *)"
    ]
  }
}
Allow fires first for your specific domain. Deny catches everything else.
Tier 4: Block destructive commands
Not secrets, but equally dangerous:
json
{
  "permissions": {
    "deny": [
      "Bash(rm -rf *)",
      "Bash(sudo *)",
      "Bash(chmod *)",
      "Bash(chown *)",
      "Bash(git push --force*)",
      "Bash(git reset --hard*)",
      "Bash(npm publish*)",
      "Bash(docker *)"
    ]
  }
}
Claude can't delete your project, escalate privileges, force push, or publish packages.
Tier 5: Block secret writes
Claude shouldn't just not read secrets, it shouldn't write them either:
json
{
  "permissions": {
    "deny": [
      "Write(**/.env*)",
      "Write(**/secrets/**)",
      "Write(**/.ssh/**)",
      "Write(**/.aws/**)",
      "Write(.github/workflows/*)",
      "Write(package-lock.json)"
    ]
  }
}
Blocks Claude from creating .env files, modifying CI/CD workflows (supply chain attack vector), or changing package-lock.json (dependency confusion).
The defense-in-depth checklist
Deny rules are one layer. Here's the full stack:
Layer 1: Deny rules in settings.json
→ Blocks direct access to sensitive files and commands

Layer 2: .env.test with dummy values
→ Tests run with fake credentials, real ones never enter Claude's context

Layer 3: Pre-commit hook scanning for secrets
→ Catches leaked credentials before they reach git

Layer 4: Environment variables via secret manager
→ Secrets stored in Vault/1Password, not plaintext files

Layer 5: Short transcript retention
→ Set CLAUDE_CODE_SKIP_PROMPT_HISTORY=1
→ Secrets that enter conversation don't persist

Layer 6: Container isolation (for sensitive projects)
→ Mount /dev/null over .env
→ Claude physically can't see the file
Each layer catches what the previous one missed.
The full settings.json (copy-paste ready)
json
{
  "permissions": {
    "allow": [
      "Read", "Glob", "Grep", "LS", "Edit", "MultiEdit",
      "Write(src/**)", "Write(tests/**)", "Write(docs/**)",
      "Bash(npm run *)", "Bash(npm test *)", "Bash(npx tsc *)",
      "Bash(npx prettier *)", "Bash(npx eslint *)",
      "Bash(git status)", "Bash(git diff *)", "Bash(git log *)",
      "Bash(git add *)", "Bash(git commit *)"
    ],
    "deny": [
      "Read(**/.env*)",
      "Read(**/.dev.vars*)",
      "Read(**/*.pem)",
      "Read(**/*.key)",
      "Read(**/*.p12)",
      "Read(**/secrets/**)",
      "Read(**/credentials/**)",
      "Read(**/.npmrc)",
      "Read(**/.pypirc)",
      "Read(**/.ssh/**)",
      "Read(**/.aws/**)",
      "Read(**/.azure/**)",
      "Read(**/.gcloud/**)",
      "Read(**/.docker/config.json)",
      "Read(**/.kube/config)",
      "Read(**/.gnupg/**)",
      "Write(**/.env*)",
      "Write(**/secrets/**)",
      "Write(**/.ssh/**)",
      "Write(.github/workflows/*)",
      "Write(package-lock.json)",
      "Bash(rm -rf *)",
      "Bash(sudo *)",
      "Bash(chmod *)",
      "Bash(chown *)",
      "Bash(curl *)",
      "Bash(wget *)",
      "Bash(nc *)",
      "Bash(ssh *)",
      "Bash(scp *)",
      "Bash(git push --force*)",
      "Bash(git reset --hard*)",
      "Bash(npm publish*)",
      "Bash(docker *)"
    ],
    "defaultMode": "acceptEdits"
  }
}
The before and after
BEFORE:

- No deny rules, or basic .env-only rules
- Claude reads ~/.ssh/id_rsa without you knowing
- Grep searches return secrets in output
- Test failures print auth headers into conversation
- curl commands can exfiltrate anything Claude has seen

AFTER:

- 5-tier deny rules blocking files, home dir, network, writes, and destructive commands
- Claude can read your code, write your code, run your tests
- Claude cannot read secrets, send data externally, or delete files
- Pre-commit hooks catch anything that slips through
- Transcript history disabled so secrets don't persist
