from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List


def run_git(args: List[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        return ""
    return result.stdout


def staged_files(repo: Path) -> List[Path]:
    output = run_git(["diff", "--cached", "--name-only", "--diff-filter=ACMR"], repo)
    return [repo / line.strip() for line in output.splitlines() if line.strip()]


def staged_diff(repo: Path) -> str:
    return run_git(["diff", "--cached", "--unified=0"], repo)


def is_git_repo(repo: Path) -> bool:
    output = run_git(["rev-parse", "--is-inside-work-tree"], repo)
    return output.strip() == "true"
