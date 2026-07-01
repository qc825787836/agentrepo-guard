from __future__ import annotations

import fnmatch
from typing import Any, Dict, List


def check_command(command: str, contract: Dict[str, Any]) -> Dict[str, Any]:
    blocked_commands: List[str] = (((contract.get("blocked_patterns") or {}).get("commands")) or [])
    for pattern in blocked_commands:
        if fnmatch.fnmatch(command, pattern) or pattern.replace("*", "") in command:
            return {
                "decision": "block",
                "reason": f"Command matches blocked pattern: {pattern}",
                "safe_alternative": "Ask the user for confirmation and avoid remote script execution.",
            }

    permissions = contract.get("agent_permissions", {}) or {}
    if permissions.get("run_shell") == "deny":
        return {
            "decision": "block",
            "reason": "Shell execution is denied by .agent-guard.yml",
        }
    if permissions.get("run_shell") == "ask":
        return {
            "decision": "ask",
            "reason": "Shell execution requires user confirmation by .agent-guard.yml",
        }
    return {"decision": "allow", "reason": "Command is not blocked by the current contract."}
