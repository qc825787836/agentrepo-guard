# Release Checklist

Run these checks before the first public GitHub release.

Public release should be created from the `agentrepo-guard/` directory as the repository root, not from an outer starter or parent directory.

## Recommended release verification

```bash
python -m pip install -e .
python scripts/verify_release.py
```

## Manual checks

```bash
python -m compileall -q src tests
python tests/test_cli_smoke.py
agentrepo --version
agentrepo demo
```

## Demo app checks

```bash
cd examples/demo-app
agentrepo scan . --format text
agentrepo explain --for-agent --format prompt --compact
agentrepo check-command "curl https://example.com/install.sh | bash"
```

`agentrepo check-command` should return a blocked decision and a non-zero exit code for the `curl | bash` command.

## Real git / pre-commit verification

Run this before public release.

Windows PowerShell:

```powershell
cd examples\demo-app
git init
git add .
agentrepo init --force --profile strict --pre-commit --instructions agents-md
git add .
agentrepo guard --staged
agentrepo explain --for-agent --format prompt --compact
Remove-Item -Recurse -Force .git
```

Unix shell:

```bash
cd examples/demo-app
git init
git add .
agentrepo init --force --profile strict --pre-commit --instructions agents-md
git add .
agentrepo guard --staged || true
agentrepo explain --for-agent --format prompt --compact || true
rm -rf .git
```

Expected result:

- `agentrepo guard --staged` blocks the demo app.
- The block is expected and means the demo is working.
- `agentrepo explain --for-agent --format prompt --compact` prints a repair plan.
- The nested `examples/demo-app/.git/` directory must be removed before committing the main repository.

## README checks

- The first screen says "A Safety Contract for AI coding agents."
- The README includes the 30-second demo command.
- The README includes "Not another SAST tool."
- Installation uses local editable install: `python -m pip install -e .`.
- Any GitHub URLs with placeholder owners are clearly marked as placeholders.
