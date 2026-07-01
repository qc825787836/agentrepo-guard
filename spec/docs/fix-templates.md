# Fix Templates

Fix templates are human-authored repair hints in `.agent-guard.yml`.

AgentRepo Guard can translate findings into runtime `agent_tasks` such as:

- Remove a real `.env` file from a commit.
- Replace live secrets with environment variables.
- Remove or verify suspicious dependencies.
- Remove remote shell execution from install hooks.
- Ask for human review before modifying `.agent-guard.yml`.

Templates should be short, specific, and safe for an agent to follow without exposing real secrets.

Example:

```yaml
fix_templates:
  secret_detected:
    instruction: "Remove hardcoded secrets and replace them with environment variables."
    preferred_fix:
      - "Use the language-appropriate environment variable accessor."
      - "Add placeholders to .env.example."
      - "Do not commit real .env files."
```
