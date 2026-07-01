# Contributing

AgentRepo Guard focuses on AI-coding-agent-specific risks, not generic SAST coverage.

Useful contributions include:

- AI-specific rules.
- False-positive fixtures.
- Prompt injection samples.
- Hallucinated dependency examples.
- Instruction-file templates.
- Spec proposals.
- Documentation improvements.

## Good first contributions

- Add a new fixture under `examples/fixtures/`.
- Add a new AI-specific rule.
- Improve an existing fix template.
- Add an integration note for an AI coding tool.
- Report a false positive.

## Rule contribution format

When proposing a rule, include a small fixture, severity, and an agent-friendly fix instruction.

```yaml
id: NO_EVAL_IN_AGENT_GENERATED_SCRIPT
severity: high
pattern: "eval\\("
message: "AI-generated scripts should avoid eval."
fix: "Use JSON.parse or a dedicated parser instead."
```

## Pull requests

Please keep changes focused. If behavior changes, update `tests/test_cli_smoke.py` or add an equivalent small test.

Do not include real secrets in fixtures, issues, pull requests, logs, or screenshots. Use clearly fake values.
