# Agent Guard Spec

`.agent-guard.yml` is an experimental Safety Contract format for AI coding agents.

It tells coding agents what they may read, edit, install, execute, commit, and how they should repair violations before continuing.

> Experimental spec. Breaking changes are expected before v1.0.

## Why this exists

AI coding agents changed the threat model of repositories. A README, an install script, a package name, or an instruction file can now influence an agent that may read files, run commands, install dependencies, edit code, and create commits.

Traditional tools report problems to humans. Agent Guard defines a contract and runtime advice shape that agents can consume directly.

## File model

```text
.agent-guard.yml           # human-maintained safety contract
.agent-guard.lock.json     # optional generated scan/advice cache, planned, not required in v0.3.x
```

`agentrepo explain --for-agent` produces runtime advice from scan findings. Runtime advice helps agents repair a change, but it is not the contract and should not be committed as a replacement for `.agent-guard.yml`.

The current v0.3.x reference CLI does not implement `.agent-guard.lock.json`. The lock file is a planned cache format, not part of the required workflow.

AgentRepo Guard CLI is the reference implementation for this experimental spec. The CLI is not the spec itself; `spec/README.md` and `spec/schema/agent-guard.schema.json` are the public spec entry points.

## Relationship to scanners

Agent Guard is not a replacement for Semgrep, TruffleHog, Gitleaks, OSV-Scanner, or pre-commit.

It is a coordination layer that makes existing security tools and AI-specific rules consumable by coding agents through a unified Safety Contract.

## Core sections

- `version`: Contract format version.
- `profile`: One of `permissive`, `moderate`, `strict`, or `critical`.
- `agent_permissions`: What agents may do directly, ask about, or avoid.
- `allowed_sources`: Package registries and source hosts expected by the repository.
- `blocked_patterns`: Commands, APIs, and paths that are unsafe for agent workflows.
- `risk_matrix`: How each severity maps to agent behavior.
- `fix_templates`: Repair guidance that can be translated into agent tasks.

## Examples

- [Minimal](examples/minimal.yml)
- [Strict](examples/strict.yml)
- [Node project](examples/node-project.yml)
- [Python project](examples/python-project.yml)

## Docs

- [Rationale](docs/rationale.md)
- [Threat model](docs/threat-model.md)
- [Agent behavior](docs/agent-behavior.md)
- [Fix templates](docs/fix-templates.md)
- [Integration guide](docs/integration-guide.md)
- [Proposal 0001: Safety Contract](proposals/0001-safety-contract.md)

## Roadmap

- Optional `.agent-guard.lock.json` for generated scan or advice caches.
- More precise rule metadata and fix-template references.
- Compatibility notes for AI coding tools that consume instruction files.
- A stable v1.0 contract once community feedback settles the field names.
