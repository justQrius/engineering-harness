#!/usr/bin/env python3
"""
Run stack-aware project checks for the current repository.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
from pathlib import Path


def has_any(repo_root: Path, *patterns: str) -> bool:
    return any(any(repo_root.glob(pattern)) for pattern in patterns)


def run(repo_root: Path, *command: str, env: dict[str, str] | None = None) -> None:
    print(f"+ {' '.join(command)}")
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    subprocess.run(command, cwd=repo_root, check=True, env=merged_env)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_path", nargs="?", default=".", help="Path to the repository")
    args = parser.parse_args()

    repo_root = Path(args.repo_path).resolve()

    if has_any(repo_root, "go.mod"):
        run(repo_root, "go", "vet", "./...")
        run(repo_root, "go", "test", "./...")
        with tempfile.TemporaryDirectory() as temp_dir:
            target = str(Path(temp_dir) / "agentd-linux-amd64")
            run(
                repo_root,
                "go",
                "build",
                "-o",
                target,
                "./cmd/agentd",
                env={"GOOS": "linux", "GOARCH": "amd64"},
            )

    if has_any(repo_root, "package.json"):
        run(repo_root, "npm", "test")

    if has_any(repo_root, "pyproject.toml", "setup.py"):
        run(repo_root, "python", "-m", "pytest")

    if has_any(repo_root, "Cargo.toml"):
        run(repo_root, "cargo", "test")

    print("Project checks: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())