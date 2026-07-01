# Pre-commit Integration

Use AgentRepo Guard as a commit-time safety belt for AI-generated changes.

## Local hook

```yaml
repos:
  - repo: local
    hooks:
      - id: agentrepo-guard
        name: AgentRepo Guard
        entry: agentrepo guard --staged
        language: system
        pass_filenames: false
```

You can generate this starter config with:

```bash
agentrepo init --pre-commit
```

If `.pre-commit-config.yaml` already exists, AgentRepo Guard will not overwrite it unless you pass `--force`.

## Future remote hook

After public release, projects can point pre-commit at the repository directly:

```yaml
repos:
  - repo: https://github.com/YOUR_NAME/agentrepo-guard
    rev: v0.3.2
    hooks:
      - id: agentrepo-guard
```

Replace `YOUR_NAME` and `rev` after public release.
