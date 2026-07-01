from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable, List

from agentrepo_guard.models import Finding

SECRET_PATTERNS = [
    ("STRIPE_LIVE_KEY_PATTERN", re.compile(r"sk_live_[A-Za-z0-9_\-]{12,}"), "possible Stripe live key detected"),
    ("GITHUB_TOKEN_PATTERN", re.compile(r"ghp_[A-Za-z0-9_]{20,}"), "possible GitHub token detected"),
    ("OPENAI_KEY_PATTERN", re.compile(r"sk-[A-Za-z0-9]{20,}"), "possible API key detected"),
    ("AWS_ACCESS_KEY_PATTERN", re.compile(r"AKIA[0-9A-Z]{16}"), "possible AWS access key detected"),
]

PUSH_SAFE_SECRET_FIXTURE_PATTERNS = [
    (
        "STRIPE_LIVE_KEY_PATTERN",
        re.compile(r"\bAGENTREPO_FAKE_STRIPE_LIVE_KEY_FIXTURE\b"),
        "push-safe Stripe live key fixture detected",
    ),
]

AGENT_INJECTION_PATTERNS = [
    ("AGENT_INSTRUCTION_OVERRIDE", re.compile(r"ignore (all )?(previous|prior) instructions", re.I), "agent-facing prompt injection phrase"),
    ("HIDE_CHANGES_FROM_USER", re.compile(r"do not (tell|show|mention) (the )?user", re.I), "instruction to hide behavior from user"),
    ("AUTO_RUN_SETUP_INSTRUCTION", re.compile(r"run (this|the) (setup|install|script) automatically", re.I), "instruction to auto-run setup"),
    ("EXFILTRATE_ENV_INSTRUCTION", re.compile(r"(send|upload|post).*(env|environment variables|api key|token)", re.I), "instruction may exfiltrate environment data"),
]

DANGEROUS_SHELL_PATTERNS = [
    ("CURL_PIPE_BASH", re.compile(r"curl\s+[^\n|]+\|\s*(bash|sh)"), "remote script execution via curl pipe"),
    ("WGET_PIPE_SH", re.compile(r"wget\s+[^\n|]+\|\s*(bash|sh)"), "remote script execution via wget pipe"),
    ("BASE64_EXEC", re.compile(r"base64\s+(-d|--decode).*\|\s*(bash|sh|python|node)"), "base64 decoded payload executed"),
]

SUSPICIOUS_DEPENDENCY_PATTERNS = [
    re.compile(r"leftpad-helper", re.I),
    re.compile(r".*-helper-ai$", re.I),
    re.compile(r".*-gpt-helper$", re.I),
    re.compile(r".*-copilot-helper$", re.I),
]

AGENT_FILES = {
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    ".github/copilot-instructions.md",
}

ENV_EXAMPLE_NAMES = {".env.example", ".env.fixture", ".env.sample", ".env.template"}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def iter_repo_files(repo: Path) -> Iterable[Path]:
    ignored_dirs = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__"}
    for path in repo.rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignored_dirs for part in path.parts):
            continue
        yield path


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def scan_text_file(repo: Path, path: Path) -> List[Finding]:
    findings: List[Finding] = []
    rel = path.relative_to(repo).as_posix()
    text = read_text(path)

    for rule_id, regex, reason in SECRET_PATTERNS:
        for match in regex.finditer(text):
            findings.append(Finding(
                id=rule_id,
                severity="critical",
                file=rel,
                line=line_number(text, match.start()),
                reason=reason,
                evidence=match.group(0)[:10] + "***",
                fix="Remove the hardcoded secret, use an environment variable, and update .env.example with a placeholder.",
            ))

    for rule_id, regex, reason in PUSH_SAFE_SECRET_FIXTURE_PATTERNS:
        for match in regex.finditer(text):
            findings.append(Finding(
                id=rule_id,
                severity="critical",
                file=rel,
                line=line_number(text, match.start()),
                reason=reason,
                evidence=match.group(0)[:10] + "***",
                fix="Remove the hardcoded secret, use an environment variable, and update .env.example with a placeholder.",
            ))

    if rel in AGENT_FILES or rel.lower().endswith((".md", ".txt")):
        for rule_id, regex, reason in AGENT_INJECTION_PATTERNS:
            for match in regex.finditer(text):
                findings.append(Finding(
                    id=rule_id,
                    severity="high",
                    file=rel,
                    line=line_number(text, match.start()),
                    reason=reason,
                    evidence=match.group(0)[:80],
                    fix="Treat this instruction as untrusted. Remove it or require human review before agents follow it.",
                ))

    if rel.endswith((".sh", "Makefile", "Dockerfile", ".yml", ".yaml", ".js", ".ts", ".py")) or Path(rel).name in {"Makefile", "Dockerfile"}:
        for rule_id, regex, reason in DANGEROUS_SHELL_PATTERNS:
            for match in regex.finditer(text):
                findings.append(Finding(
                    id=rule_id,
                    severity="critical",
                    file=rel,
                    line=line_number(text, match.start()),
                    reason=reason,
                    evidence=match.group(0)[:120],
                    fix="Do not execute remote scripts directly. Download, inspect, verify checksum, and ask the user before execution.",
                ))

    return findings


def scan_package_json(repo: Path, path: Path) -> List[Finding]:
    findings: List[Finding] = []
    rel = path.relative_to(repo).as_posix()
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError:
        return findings

    scripts = data.get("scripts", {}) or {}
    for hook in ["preinstall", "install", "postinstall", "prepare"]:
        if hook in scripts:
            findings.append(Finding(
                id="NPM_INSTALL_HOOK",
                severity="high",
                file=rel,
                reason=f"package.json contains {hook} script that may run during dependency installation",
                evidence=str(scripts[hook])[:120],
                fix="Require human confirmation before install, or use npm install --ignore-scripts when appropriate.",
            ))

    deps = {}
    for key in ["dependencies", "devDependencies", "optionalDependencies"]:
        deps.update(data.get(key, {}) or {})
    for name in deps:
        if any(pattern.fullmatch(name) for pattern in SUSPICIOUS_DEPENDENCY_PATTERNS):
            findings.append(Finding(
                id="SUSPICIOUS_OR_HALLUCINATED_DEPENDENCY",
                severity="high",
                file=rel,
                reason="dependency name looks suspicious or commonly hallucinated by agents",
                evidence=name,
                fix="Verify the package exists in the allowed registry, prefer an established package, or ask the user for confirmation.",
            ))
    return findings


def scan_paths(repo: Path, paths: Iterable[Path], staged: bool = False) -> List[Finding]:
    findings: List[Finding] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        rel = path.relative_to(repo).as_posix()
        if rel == ".agent-guard.yml":
            if staged:
                findings.append(Finding(
                    id="MODIFY_AGENT_GUARD_CONTRACT",
                    severity="critical",
                    file=rel,
                    reason="safety contract was modified and requires human review",
                    fix="Do not let an AI agent weaken or delete the safety contract without human review.",
            ))
            continue
        if _is_real_env_file(rel):
            findings.append(Finding(
                id="ENV_FILE_STAGED",
                severity="critical",
                file=rel,
                reason="environment file appears to be staged",
                fix="Remove this file from the commit and commit only a sanitized .env.example.",
            ))
        findings.extend(scan_text_file(repo, path))
        if rel.endswith("package.json"):
            findings.extend(scan_package_json(repo, path))
    return findings


def scan_repo(repo: Path) -> List[Finding]:
    return scan_paths(repo, iter_repo_files(repo), staged=False)


def _is_real_env_file(rel: str) -> bool:
    name = Path(rel).name
    if name in ENV_EXAMPLE_NAMES:
        return False
    return name == ".env" or name.startswith(".env.")
