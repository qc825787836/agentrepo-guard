# Security Policy

AgentRepo Guard is an experimental security tool for AI coding agent workflows.

It does not guarantee that every secret, unsafe command, malicious dependency, or risky instruction will be detected. Use it as a coordination layer alongside human review and existing security tools.

## Reporting security issues

Do not submit real secrets, tokens, private repository contents, or exploit payloads in public issues.

When reporting a security issue:

- Redact secrets and credentials.
- Use minimal reproductions where possible.
- Replace real tokens with fake fixtures.
- Describe the expected safe behavior.

All secrets in `examples/demo-app` are fake test fixtures used only to demonstrate detection rules.

AgentRepo Guard masks secret evidence in output and should not print full secret values.

AgentRepo Guard does not upload repository contents in the current CLI implementation.
