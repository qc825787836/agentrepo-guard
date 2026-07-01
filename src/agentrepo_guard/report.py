from __future__ import annotations

import json
from typing import List

from agentrepo_guard.advice import SEVERITY_ORDER, build_agent_advice, decision_from_findings, render_agent_prompt
from agentrepo_guard.models import Finding


def human_report(findings: List[Finding]) -> str:
    if not findings:
        return "OK AI Agent Safety: ALLOW\n\nNo contract violations found."

    decision = decision_from_findings(findings)
    header = {
        "block": "X AI Agent Safety: BLOCK",
        "ask": "! AI Agent Safety: ASK USER",
        "review": "! AI Agent Safety: REVIEW",
        "allow": "OK AI Agent Safety: ALLOW",
    }[decision]

    lines = [header, "", f"{len(findings)} contract violation(s) found:", ""]
    for finding in sorted(findings, key=lambda f: SEVERITY_ORDER.get(f.severity, 9)):
        loc = finding.file
        if finding.line:
            loc += f":{finding.line}"
        lines.extend([
            f"[{finding.severity}] {finding.id}",
            f"  file: {loc}",
            f"  reason: {finding.reason}",
            f"  fix: {finding.fix}",
        ])
        if finding.evidence:
            lines.append(f"  evidence: {finding.evidence}")
        lines.append("")

    lines.extend([
        "Suggested agent action:",
        "  agentrepo explain --for-agent --format prompt --compact",
    ])
    return "\n".join(lines)


def markdown_report(findings: List[Finding]) -> str:
    decision = decision_from_findings(findings)
    if not findings:
        return "# AgentRepo Guard Scan Report\n\n**Decision:** allow\n\nNo contract violations found."

    lines = [
        "# AgentRepo Guard Scan Report",
        "",
        f"**Decision:** {decision}",
        "",
        f"Found {len(findings)} contract violation(s).",
        "",
    ]
    for finding in sorted(findings, key=lambda f: SEVERITY_ORDER.get(f.severity, 9)):
        loc = finding.file
        if finding.line:
            loc += f":{finding.line}"
        lines.extend([
            f"- **[{finding.severity}] {finding.id}**",
            f"  - File: `{loc}`",
            f"  - Reason: {finding.reason}",
            f"  - Fix: {finding.fix}",
        ])
        if finding.evidence:
            lines.append(f"  - Evidence: `{finding.evidence}`")
    return "\n".join(lines)


def agent_json(findings: List[Finding], compact: bool = False) -> str:
    advice = build_agent_advice(findings, compact=compact)
    return json.dumps(advice, indent=2, ensure_ascii=False)


def agent_prompt(findings: List[Finding], compact: bool = False) -> str:
    advice = build_agent_advice(findings, compact=compact)
    return render_agent_prompt(advice, compact=compact)
