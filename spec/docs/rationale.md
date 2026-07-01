# Rationale

`.agent-guard.yml` is intended to be small, readable, portable, and human-reviewable.

It is not a scanner report. It is a repository-level safety contract that can be checked by CLI tools, pre-commit hooks, future automation, and coding agents.

The reference implementation may generate findings and runtime advice, but the contract itself should remain stable enough for humans to review and agents to consume.

## Goals

- Provide a shared format for agent permissions.
- Encode blocked commands, APIs, paths, and package sources.
- Map risk levels to expected agent behavior.
- Provide fix templates that can become machine-consumable repair tasks.

## Non-goals

- Replace SAST, secret scanning, or dependency scanning.
- Define a universal sandbox format.
- Guarantee that all agents will comply.
- Act as a hosted policy service.
