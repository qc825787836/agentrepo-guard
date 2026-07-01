# Integration Guide

AgentRepo Guard works best as a lightweight safety loop:

```text
AI-generated change -> pre-commit guard -> agent repair advice -> retry
```

## Pre-commit

Use `agentrepo guard --staged` as a local pre-commit hook so unsafe staged changes stop before commit.

```bash
agentrepo init --pre-commit
```

## Instruction files

Existing AI coding agents already read instruction files. AgentRepo Guard can generate those files from `.agent-guard.yml`:

```bash
agentrepo init --instructions agents-md,copilot,aider,cursor
```

Instruction files are derived guidance. They should not conflict with the human-maintained contract.
