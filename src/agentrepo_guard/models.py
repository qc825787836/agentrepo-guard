from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional


@dataclass
class Finding:
    id: str
    severity: str
    file: str
    reason: str
    fix: str
    line: Optional[int] = None
    evidence: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["file"] = str(data["file"]).replace("\\", "/")
        return data


@dataclass
class AgentAdvice:
    decision: str
    violations: List[Finding]

    def to_dict(self) -> Dict[str, Any]:
        summary = {
            "block": "Commit blocked by .agent-guard.yml. Fix all critical and high-risk violations before retrying.",
            "ask": "Commit requires human review by .agent-guard.yml. Resolve high-risk violations or ask the user before continuing.",
            "review": "Commit should be reviewed against .agent-guard.yml before continuing.",
            "allow": "No Safety Contract violations found.",
        }.get(self.decision, "Review Safety Contract findings before continuing.")
        return {
            "schema": "agentrepo.guard/advice/v0.2",
            "decision": self.decision,
            "summary": summary,
            "retry_after_fix": "Run agentrepo guard --staged again.",
            "violations": [finding.to_dict() for finding in self.violations],
            "agent_tasks": [],
        }
