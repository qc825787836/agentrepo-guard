# Git Pre-commit Demo

Use this guide to test the real staged-files flow with Git and the optional pre-commit integration.

The demo app contains fake fixtures only. All secrets in `examples/demo-app` are fake test fixtures used only to demonstrate detection rules.

AgentRepo Guard masks secret evidence in output and should not print full secret values.

`agentrepo guard --staged` is expected to block the demo app. Blocking is success in this scenario.

## Windows PowerShell

```powershell
cd agentrepo-guard
python -m pip install -e .

cd examples\demo-app
git init
git add .
agentrepo init --force --profile strict --pre-commit --instructions agents-md
git add .
agentrepo guard --staged
agentrepo explain --for-agent --format prompt --compact
```

## Unix shell

```bash
cd agentrepo-guard
python -m pip install -e .

cd examples/demo-app
git init
git add .
agentrepo init --force --profile strict --pre-commit --instructions agents-md
git add .
agentrepo guard --staged || true
agentrepo explain --for-agent --format prompt --compact || true
```

If `pre-commit` is installed, you can continue with:

```bash
pre-commit install
git commit -m "demo unsafe agent change"
```

The commit should be intercepted. That block is the expected outcome for the unsafe demo fixtures.
