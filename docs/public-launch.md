# Public Launch Notes

AgentRepo Guard is experimental. Launch copy should be clear about what exists today and avoid promising full security coverage.

## GitHub repo description

A Safety Contract CLI that turns repository security rules into repair plans AI coding agents can follow.

## Topics / tags

- ai-agent
- coding-agent
- security
- devsecops
- pre-commit
- sast
- prompt-injection
- supply-chain-security
- agents-md

## Show HN title draft

Show HN: AgentRepo Guard - a Safety Contract for AI coding agents

## Short launch copy

AgentRepo Guard is an experimental CLI for AI coding agent workflows.

It turns repository safety rules into a machine-readable `.agent-guard.yml`, blocks risky staged changes with `agentrepo guard --staged`, and generates repair instructions with `agentrepo explain --for-agent --format prompt --compact`.

It is not a replacement for Semgrep, TruffleHog, Gitleaks, OSV-Scanner, or pre-commit. It is a coordination layer that makes security rules and AI-specific checks consumable by coding agents.

## Reddit / Discord / GitHub Discussions draft

I am working on AgentRepo Guard, an experimental open-source CLI for AI coding agent safety loops.

The idea is simple:

```text
AI-generated change -> Safety Contract blocks it -> agent repair plan -> retry passes
```

The current MVP supports:

- `.agent-guard.yml` safety contracts
- `agentrepo guard --staged`
- JSON and prompt repair advice for agents
- pre-commit and instruction-file integrations
- a local demo app with fake secret fixtures

The spec is experimental and breaking changes are expected before v1.0. I would especially like feedback on the contract shape, false positives, and AI-agent-specific rules worth adding.

## Release notes draft

# v0.3.2 — Public MVP

AgentRepo Guard is an experimental Safety Contract for AI coding agents.

This release includes:

- `.agent-guard.yml` experimental spec
- CLI reference implementation
- agent-readable repair plans
- `agentrepo demo`
- pre-commit integration docs
- instruction-file generation for AGENTS.md, Copilot, Aider, and Cursor
- fake unsafe demo app
- release verification script

This is not a replacement for Semgrep, TruffleHog, Gitleaks, OSV-Scanner, or pre-commit. It is a coordination layer that makes existing security tools and AI-specific rules consumable by coding agents through a unified Safety Contract.

Breaking changes are expected before v1.0.

## Suggested first GitHub issues

Create these after the repository is public:

### 1. Add a new AI-specific unsafe pattern fixture

Labels: `good first issue`, `rule-request`

Goal: add one small fixture that demonstrates an AI-specific unsafe pattern.

Examples:

- prompt injection in project docs
- unsafe auto-run setup instruction
- suspicious dependency added by an AI agent
- environment variable exfiltration instruction

### 2. Add a `.agent-guard.yml` example for another language

Labels: `good first issue`, `docs`

Candidates:

- Go
- Rust
- Java
- Ruby

Goal: add one small example under `spec/examples/`.

### 3. Improve generated instruction-file guidance

Labels: `good first issue`, `integration`

Goal: improve generated guidance for one of:

- AGENTS.md
- GitHub Copilot instructions
- Aider conventions
- Cursor rules

Do not intentionally add typos or broken docs just to create easy issues.

## Messaging guardrails

- Do say the spec is experimental.
- Do say it complements existing security tools.
- Do not claim full SAST, secret scanning, or dependency vulnerability coverage.
- Do not imply the project is already published to PyPI, GitHub Marketplace, or any hosted service.
- Do not promise MCP, GitHub Action, or hosted features until they exist.
