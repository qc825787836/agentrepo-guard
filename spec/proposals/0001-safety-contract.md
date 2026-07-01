# Proposal 0001: Safety Contract for AI Coding Agents

## Summary

Define `.agent-guard.yml` as a repository-level safety contract for AI coding agents.

## Goals

- Provide a shared format for agent permissions.
- Encode blocked commands, APIs, paths, and package sources.
- Map risk levels to agent behavior.
- Provide machine-consumable fix templates.

## Non-goals

- Replace SAST, secret scanning, or dependency scanning.
- Define a universal sandbox format.
- Guarantee that all agents will comply.
