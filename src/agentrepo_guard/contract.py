from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

PROFILES = {"permissive", "moderate", "strict", "critical"}

PROFILE_PERMISSIONS = {
    "permissive": {
        "read_files": "allow",
        "edit_files": "allow",
        "run_shell": "ask",
        "install_dependencies": "ask",
        "network_access": "ask",
        "access_secrets": "deny",
        "modify_ci": "ask",
        "modify_agent_guard": "deny",
    },
    "moderate": {
        "read_files": "allow",
        "edit_files": "allow",
        "run_shell": "ask",
        "install_dependencies": "ask",
        "network_access": "ask",
        "access_secrets": "deny",
        "modify_ci": "ask",
        "modify_agent_guard": "deny",
    },
    "strict": {
        "read_files": "allow",
        "edit_files": "ask",
        "run_shell": "ask",
        "install_dependencies": "ask",
        "network_access": "deny",
        "access_secrets": "deny",
        "modify_ci": "ask",
        "modify_agent_guard": "deny",
    },
    "critical": {
        "read_files": "ask",
        "edit_files": "ask",
        "run_shell": "deny",
        "install_dependencies": "deny",
        "network_access": "deny",
        "access_secrets": "deny",
        "modify_ci": "deny",
        "modify_agent_guard": "deny",
    },
}


def default_contract_text(profile: str = "moderate") -> str:
    if profile not in PROFILES:
        raise ValueError(f"Unsupported profile: {profile}")
    permissions = PROFILE_PERMISSIONS[profile]
    permission_lines = "\n".join(f"  {key}: {value}" for key, value in permissions.items())
    return f"""version: "0.3"
profile: {profile}

description: "Safety contract for AI coding agents working in this repository."

agent_permissions:
{permission_lines}

allowed_sources:
  package_registries:
    npm:
      - "https://registry.npmjs.org"
    pypi:
      - "https://pypi.org/simple"
  git_hosts:
    - "https://github.com"

blocked_patterns:
  commands:
    - "curl * | bash"
    - "wget * | sh"
    - "rm -rf /"
  apis:
    - "eval"
    - "exec"
    - "child_process.exec"
    - "subprocess.Popen"
  paths:
    - ".env"
    - ".env.*"
    - "~/.ssh/*"
    - "~/.aws/*"
    - "~/.config/gcloud/*"

risk_matrix:
  critical:
    action: block
    agent_behavior: "stop and request human review"
  high:
    action: ask
    agent_behavior: "explain risk and ask before continuing"
  moderate:
    action: review
    agent_behavior: "prefer safe alternative"
  low:
    action: allow
    agent_behavior: "continue with note"

fix_templates:
  secret_detected:
    instruction: "Remove hardcoded secrets and replace them with environment variables."
    preferred_fix:
      - "Move secret to .env.local"
      - "Add placeholder to .env.example"
      - "Ensure .env* is ignored by git"

  hallucinated_dependency:
    instruction: "Verify the dependency exists in the allowed registry before adding it."
    preferred_fix:
      - "Check package registry"
      - "Prefer established packages"
      - "Ask user before adding unknown dependencies"

  unsafe_remote_execution:
    instruction: "Do not execute remote scripts directly."
    preferred_fix:
      - "Download the script separately"
      - "Verify checksum"
      - "Ask user before execution"
"""


DEFAULT_CONTRACT = default_contract_text()


def write_default_contract(repo: Path, profile: str = "moderate", force: bool = False) -> Path:
    path = repo / ".agent-guard.yml"
    if force or not path.exists():
        path.write_text(default_contract_text(profile), encoding="utf-8")
    return path


def load_contract(repo: Path) -> Dict[str, Any]:
    path = repo / ".agent-guard.yml"
    if not path.exists():
        return yaml.safe_load(DEFAULT_CONTRACT)
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
