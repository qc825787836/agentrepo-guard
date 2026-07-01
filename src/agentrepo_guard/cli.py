from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agentrepo_guard import __version__
from agentrepo_guard.contract import PROFILES, load_contract, write_default_contract
from agentrepo_guard.decision import check_command as decide_command
from agentrepo_guard.gitutils import is_git_repo, staged_files
from agentrepo_guard.instructions import instruction_path, write_instructions
from agentrepo_guard.report import agent_json, agent_prompt, decision_from_findings, human_report, markdown_report
from agentrepo_guard.rules.core import scan_paths, scan_repo

INSTRUCTION_TARGETS = {"agents-md", "copilot", "aider", "cursor"}

PRE_COMMIT_CONFIG = """repos:
  - repo: local
    hooks:
      - id: agentrepo-guard
        name: AgentRepo Guard
        entry: agentrepo guard --staged
        language: system
        pass_filenames: false
"""


def cmd_init(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    contract_path = repo / ".agent-guard.yml"
    existed = contract_path.exists()
    if existed and not args.force:
        print(".agent-guard.yml already exists. Use --force to overwrite.")
    else:
        path = write_default_contract(repo, profile=args.profile, force=args.force)
        action = "Updated" if existed else "Created"
        print(f"{action} {_rel_display(path, repo)}")

    contract = load_contract(repo)
    if args.pre_commit:
        _write_pre_commit_config(repo, force=args.force)
    if args.instructions:
        for target in _parse_instruction_targets(args.instructions):
            path = instruction_path(repo, target)
            if path.exists() and not args.force:
                print(f"{_rel_display(path, repo)} already exists. Use --force to overwrite.")
                continue
            written = write_instructions(repo, target, contract, force=args.force)
            print(f"Wrote {_rel_display(written, repo)}")
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    findings = scan_repo(repo)
    if args.format == "json":
        print(agent_json(findings))
    elif args.format == "markdown":
        print(markdown_report(findings))
    else:
        print(human_report(findings))
    return 1 if decision_from_findings(findings) == "block" and args.fail_on_block else 0


def cmd_guard(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    if args.staged:
        if not is_git_repo(repo):
            print("Not inside a git repository. Use agentrepo scan . instead.", file=sys.stderr)
            return 2
        files = staged_files(repo)
        findings = scan_paths(repo, files, staged=True)
    else:
        findings = scan_repo(repo)
    print(human_report(findings))
    decision = decision_from_findings(findings)
    return 1 if decision in {"block", "ask"} else 0


def cmd_explain(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    if args.staged and is_git_repo(repo):
        findings = scan_paths(repo, staged_files(repo), staged=True)
    else:
        findings = scan_repo(repo)
    if args.for_agent:
        if args.format == "prompt":
            print(agent_prompt(findings, compact=args.compact))
        else:
            print(agent_json(findings, compact=args.compact))
    else:
        print(human_report(findings))
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    print("""AgentRepo Guard demo: Safety Contract for AI coding agents

Scenario:
  An AI coding agent added a payment integration.

The change contains:
  X hardcoded Stripe live key
  X suspicious dependency: leftpad-helper
  X postinstall script: curl ... | bash

pre-commit runs:
  agentrepo guard --staged

Result:
  X Commit blocked by .agent-guard.yml

The agent asks for a repair plan:
  agentrepo explain --for-agent --format prompt --compact

Repair plan:
  1. Replace live secrets with environment variables.
  2. Remove .env from commit.
  3. Remove or verify leftpad-helper.
  4. Remove remote shell execution from postinstall.

After the agent fixes the code:
  OK AI Agent Safety: ALLOW""")
    return 0


def cmd_generate_instructions(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    contract = load_contract(repo)
    path = write_instructions(repo, args.target, contract)
    print(f"Wrote {_rel_display(path, repo)}")
    return 0


def cmd_check_command(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    contract = load_contract(repo)
    result = decide_command(args.command, contract)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result.get("decision") == "block" else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentrepo",
        description="AgentRepo Guard: a Safety Contract CLI for AI coding agents.",
        epilog="Typical loop: agentrepo guard --staged -> agentrepo explain --for-agent --format prompt --compact -> retry.",
    )
    parser.add_argument("--repo", default=".", help="Repository path")
    parser.add_argument("--version", action="version", version=f"agentrepo-guard {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create .agent-guard.yml and optional agent integrations")
    p_init.add_argument("--force", action="store_true", help="Overwrite generated files when they already exist")
    p_init.add_argument("--profile", choices=sorted(PROFILES), default="moderate", help="Safety profile to write")
    p_init.add_argument("--pre-commit", action="store_true", help="Create a local pre-commit config")
    p_init.add_argument("--instructions", help="Comma-separated instruction targets: agents-md,copilot,aider,cursor")
    p_init.set_defaults(func=cmd_init)

    p_scan = sub.add_parser("scan", help="Scan repository")
    p_scan.add_argument("path", nargs="?", default=".")
    p_scan.add_argument("--format", choices=["text", "json", "markdown"], default="text")
    p_scan.add_argument("--fail-on-block", action="store_true")
    p_scan.set_defaults(func=lambda args: cmd_scan(_with_repo(args, args.path)))

    p_guard = sub.add_parser("guard", help="Guard current repo or staged changes")
    p_guard.add_argument("--staged", action="store_true", help="Scan staged files only")
    p_guard.set_defaults(func=cmd_guard)

    p_explain = sub.add_parser("explain", help="Explain findings for humans or agents")
    p_explain.add_argument("--for-agent", action="store_true")
    p_explain.add_argument("--staged", action="store_true")
    p_explain.add_argument("--format", choices=["json", "prompt"], default="json")
    p_explain.add_argument("--compact", action="store_true", help="Emit shorter agent repair advice")
    p_explain.set_defaults(func=cmd_explain)

    p_gen = sub.add_parser("generate-instructions", help="Generate agent instruction files")
    p_gen.add_argument("--for", dest="target", required=True, choices=["agents-md", "copilot", "aider", "cursor"])
    p_gen.set_defaults(func=cmd_generate_instructions)

    p_check = sub.add_parser("check-command", help="Check a shell command against .agent-guard.yml")
    p_check.add_argument("command")
    p_check.set_defaults(func=cmd_check_command)

    p_demo = sub.add_parser("demo", help="Print the 30-second AgentRepo Guard demo flow")
    p_demo.set_defaults(func=cmd_demo)

    return parser


def _with_repo(args: argparse.Namespace, path: str) -> argparse.Namespace:
    args.repo = path
    return args


def _parse_instruction_targets(value: str) -> list[str]:
    targets = [item.strip() for item in value.split(",") if item.strip()]
    invalid = [target for target in targets if target not in INSTRUCTION_TARGETS]
    if invalid:
        raise SystemExit(f"Unsupported instruction target(s): {', '.join(invalid)}")
    return targets


def _write_pre_commit_config(repo: Path, force: bool = False) -> Path:
    path = repo / ".pre-commit-config.yaml"
    if path.exists() and not force:
        print(".pre-commit-config.yaml already exists. Copy integrations/pre-commit/example.pre-commit-config.yaml and merge manually.")
        return path
    path.write_text(PRE_COMMIT_CONFIG, encoding="utf-8")
    print(f"Wrote {_rel_display(path, repo)}")
    return path


def _rel_display(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
