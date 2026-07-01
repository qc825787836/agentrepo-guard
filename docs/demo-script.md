# 30-second Demo Script

Use this script to record the README demo GIF.

## Recording target

Show AI-generated unsafe change → Safety Contract blocks it → Agent-readable repair plan → retry passes.

## Recommended recording command

```bash
agentrepo demo
```

This command does not call an AI system, does not contact the network, and does not modify files. It prints the public MVP loop in a format suitable for a short README recording.

## Optional real demo

```bash
cd examples/demo-app
agentrepo scan . --format text
agentrepo explain --for-agent --format prompt --compact
agentrepo check-command "curl https://example.com/install.sh | bash"
```

`agentrepo check-command` is expected to block `curl | bash` and return a non-zero exit code.

## Suggested GIF path

```text
docs/assets/demo.gif
```

Do not show real secrets in the recording. All secrets in the demo app are fake fixtures used only to demonstrate detection rules.

All secrets in `examples/demo-app` are fake test fixtures used only to demonstrate detection rules.

AgentRepo Guard masks secret evidence in output and should not print full secret values.
