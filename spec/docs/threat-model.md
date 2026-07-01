# Threat Model

Agent Guard focuses on risks introduced or amplified by AI coding agents:

- Repository text that gives instructions to agents.
- Install scripts that agents may run automatically.
- Hallucinated dependencies inserted by agents.
- Hardcoded secrets generated during code creation.
- Agent attempts to weaken or delete safety contracts.
- CI changes that expand permissions after large agent-authored patches.

Non-goals for v0.3:

- Full SAST replacement.
- Full dependency vulnerability scanning.
- Malware sandboxing.
- Guaranteed supply-chain risk detection.
- Hosted policy enforcement.
