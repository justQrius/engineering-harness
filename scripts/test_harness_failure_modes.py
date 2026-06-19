#!/usr/bin/env python3
"""Regression tests for harness failure-mode ergonomics."""

from __future__ import annotations

import importlib.util
import subprocess
import tempfile
from pathlib import Path


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def bootstrap_repo(skill_root: Path, repo_root: Path) -> None:
    bootstrap = load_module(skill_root / "scripts" / "bootstrap_harness.py", "bootstrap_harness_failure_modes")
    bootstrap.copy_templates(skill_root / "assets" / "templates", repo_root, "Failure Mode Repo", force=True)


def test_invalid_utf8_is_reported(skill_root: Path) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_root = Path(temp_dir) / "utf8-repo"
        repo_root.mkdir(parents=True, exist_ok=True)
        bootstrap_repo(skill_root, repo_root)
        (repo_root / ".handoff" / "CURRENT.md").write_bytes(b"# Current Work Packet\n\x97\n")

        audit = load_module(repo_root / "scripts" / "audit_repo.py", "audit_repo_invalid_utf8")
        result = audit.audit_repo(repo_root)
        issues = "\n".join(result["issues"])
        if "not valid UTF-8" not in issues or "byte" not in issues:
            raise SystemExit(f"Expected invalid UTF-8 issue, got: {result['issues']}")


def test_scope_check_tolerates_non_git_repo(skill_root: Path) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_root = Path(temp_dir) / "non-git-repo"
        repo_root.mkdir(parents=True, exist_ok=True)
        bootstrap_repo(skill_root, repo_root)

        checker = load_module(repo_root / "scripts" / "check_packet_scope.py", "check_packet_scope_non_git")
        result = checker.check_scope(repo_root)
        warnings = "\n".join(result["warnings"])
        if result["issues"]:
            raise SystemExit(f"Expected no issues for non-git repo, got: {result['issues']}")
        if "Not a git worktree" not in warnings:
            raise SystemExit(f"Expected non-git warning, got: {result['warnings']}")


def main() -> int:
    skill_root = Path(__file__).resolve().parent.parent
    test_invalid_utf8_is_reported(skill_root)
    test_scope_check_tolerates_non_git_repo(skill_root)
    print("Harness failure-mode tests: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
