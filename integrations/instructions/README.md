# Instruction File Integrations

AgentRepo Guard can translate `.agent-guard.yml` into instruction files that existing coding agents already read.

Supported targets:

- `AGENTS.md`
- `.github/copilot-instructions.md`
- `AGENT_GUARD_CONVENTIONS.md`
- `.cursor/rules/agent-guard.md`

Generate them with:

```bash
agentrepo init --instructions agents-md,copilot,aider,cursor
```

This is the lowest-friction integration path. It does not require an agent to natively understand `.agent-guard.yml`.

These instruction files are derived from the human-maintained contract. If an instruction file conflicts with `.agent-guard.yml`, the contract should win.
