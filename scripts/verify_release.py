from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".toml"}
SKIP_PARTS = {"__pycache__", ".git", ".venv", "venv", "build", "dist"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify AgentRepo Guard is ready for public release.")
    parser.add_argument("--skip-smoke", action="store_true", help="Skip tests/test_cli_smoke.py to avoid recursion.")
    args = parser.parse_args()

    try:
        check_required_files()
        check_readme()
        check_spec_readme()
        check_public_refs()
        run([sys.executable, "-m", "compileall", "-q", "src", "tests"])
        if not args.skip_smoke:
            run([sys.executable, "tests/test_cli_smoke.py"])
        run_agentrepo(["--version"])
        run_agentrepo(["demo"])
    except VerificationError as exc:
        print(f"Release verification failed: {exc}", file=sys.stderr)
        return 1

    print("Release verification passed.")
    return 0


class VerificationError(Exception):
    pass


def check_required_files() -> None:
    required = [
        "README.md",
        "LICENSE",
        "pyproject.toml",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "spec/README.md",
        "spec/schema/agent-guard.schema.json",
        "docs/release-checklist.md",
        "docs/demo-script.md",
        "docs/public-launch.md",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    if missing:
        raise VerificationError("missing required file(s): " + ", ".join(missing))


def check_readme() -> None:
    text = read_text(ROOT / "README.md")
    require_contains(
        text,
        [
            "A Safety Contract for AI coding agents",
            "Not another SAST tool",
            "How this is different",
            "Current scope",
            "Not yet supported",
            ".agent-guard.yml",
            "Experimental spec",
        ],
        "README.md",
    )
    require_absent(text, forbidden_public_refs()[:4], "README.md")
    check_fake_fixture_notice()
    require_contains(
        read_text(ROOT / "docs" / "public-launch.md"),
        ["Release notes draft", "Suggested first GitHub issues"],
        "docs/public-launch.md",
    )
    require_contains(
        read_text(ROOT / "docs" / "release-checklist.md"),
        ["Real git / pre-commit verification"],
        "docs/release-checklist.md",
    )


def check_spec_readme() -> None:
    text = read_text(ROOT / "spec" / "README.md")
    require_contains(text, [".agent-guard.yml", "experimental", "Breaking changes"], "spec/README.md")


def check_fake_fixture_notice() -> None:
    combined = "\n".join(
        [
            read_text(ROOT / "README.md"),
            read_text(ROOT / "SECURITY.md"),
            read_text(ROOT / "examples" / "demo-app" / "README.md"),
        ]
    )
    require_contains(combined, ["fake test fixtures"], "README.md/SECURITY.md/examples/demo-app/README.md")


def check_public_refs() -> None:
    forbidden = forbidden_public_refs()
    hits: list[str] = []
    for path in iter_public_text_files():
        text = read_text(path)
        for item in forbidden:
            if item in text:
                hits.append(f"{path.relative_to(ROOT).as_posix()}: contains {item}")
    if hits:
        raise VerificationError("public repo reference check failed: " + "; ".join(hits))


def run(command: Sequence[str]) -> None:
    env = release_env()
    result = subprocess.run(
        list(command),
        cwd=str(ROOT),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise VerificationError(
            f"command failed ({' '.join(command)}):\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def run_agentrepo(args: Sequence[str]) -> None:
    executable = shutil.which("agentrepo")
    if executable:
        command = [executable, *args]
    else:
        command = [sys.executable, "-m", "agentrepo_guard.cli", *args]
    run(command)


def release_env() -> dict[str, str]:
    env = os.environ.copy()
    src = str(ROOT / "src")
    env["PYTHONPATH"] = src + os.pathsep + env.get("PYTHONPATH", "")
    return env


def require_contains(text: str, expected: Iterable[str], label: str) -> None:
    missing = [item for item in expected if item not in text]
    if missing:
        raise VerificationError(f"{label} missing expected text: " + ", ".join(missing))


def require_absent(text: str, forbidden: Iterable[str], label: str) -> None:
    present = [item for item in forbidden if item in text]
    if present:
        raise VerificationError(f"{label} contains forbidden text: " + ", ".join(present))


def iter_public_text_files() -> Iterable[Path]:
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def forbidden_public_refs() -> list[str]:
    return [
        "agentrepo-guard-" + "starter",
        "../agent-guard-" + "spec",
        "C:" + "/Users/",
        "C:" + "\\Users\\",
        "\u5f3a\u8d85",
        "local " + "workspace",
    ]


if __name__ == "__main__":
    raise SystemExit(main())
