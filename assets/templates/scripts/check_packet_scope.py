#!/usr/bin/env python3
"""
Inspect the current git diff for obvious packet and harness hygiene violations.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
from pathlib import Path


APPROVED_STATUS_PREFIXES = [
    "approved",
    "in-progress",
    "review-requested",
    "review-complete",
    "done",
]

DURABLE_LOG_PATHS = {
    ".handoff/CURRENT.md",
    ".handoff/DECISIONS.md",
    ".handoff/REVIEWS.md",
    ".handoff/RELEASES.md",
}

HARNESS_PATH_PREFIXES = (
    ".handoff/",
    "docs/engineering/",
    ".github/workflows/",
    "scripts/",
)

HARNESS_SINGLE_FILES = {
    "AGENTS.md",
    "CLAUDE.md",
}


def run_git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout




def is_git_worktree(repo_root: Path) -> bool:
    try:
        output = run_git(repo_root, "rev-parse", "--is-inside-work-tree")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    return output.strip().lower() == "true"

def parse_changed_files(repo_root: Path) -> list[str]:
    output = run_git(repo_root, "status", "--porcelain")
    changed: list[str] = []
    for line in output.splitlines():
        if len(line) < 4:
            continue
        path_text = line[3:]
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        changed.append(path_text.replace("\\", "/"))
    return changed


def parse_status_and_packet_id(text: str) -> tuple[str, str]:
    status = ""
    packet_id = ""
    for line in text.splitlines():
        if line.startswith("- Status:"):
            status = line.split(":", 1)[1].strip()
        elif line.startswith("- Packet ID:"):
            packet_id = line.split(":", 1)[1].strip()
    return status, packet_id


def parse_affected_file_patterns(text: str) -> list[str]:
    lines = text.splitlines()
    in_affected = False
    in_files = False
    patterns: list[str] = []

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped == "## Affected Areas":
            in_affected = True
            in_files = False
            continue
        if in_affected and stripped.startswith("## "):
            break
        if not in_affected:
            continue

        if stripped == "- Files:":
            in_files = True
            continue
        if stripped.startswith("- Systems:") or stripped.startswith("- Trust boundaries:"):
            in_files = False
            continue
        if in_files and stripped.startswith("- "):
            value = stripped[2:].strip().strip("`")
            if value:
                patterns.append(value.replace("\\", "/"))

    return patterns


def status_allows_nontrivial_work(status: str) -> bool:
    normalized = status.lower().strip()
    return any(normalized.startswith(prefix) for prefix in APPROVED_STATUS_PREFIXES)


def is_harness_path(path_text: str) -> bool:
    return path_text in HARNESS_SINGLE_FILES or path_text.startswith(HARNESS_PATH_PREFIXES)


def is_declared_affected_path(path_text: str, patterns: list[str]) -> bool:
    normalized = path_text.replace("\\", "/")
    for pattern in patterns:
        if fnmatch.fnmatch(normalized, pattern):
            return True
    return False


def check_scope(repo_root: Path) -> dict:
    issues: list[str] = []
    warnings: list[str] = []

    current_path = repo_root / ".handoff" / "CURRENT.md"
    if not current_path.exists():
        return {"issues": ["Missing .handoff/CURRENT.md"], "warnings": warnings}

    if not is_git_worktree(repo_root):
        warnings.append("Not a git worktree; skipping diff-aware packet scope check")
        return {"issues": issues, "warnings": warnings, "changed_files": []}

    changed_files = parse_changed_files(repo_root)
    if not changed_files:
        return {"issues": issues, "warnings": warnings, "changed_files": changed_files}

    current_text = current_path.read_text(encoding="utf-8")
    status, packet_id = parse_status_and_packet_id(current_text)
    declared_affected_files = parse_affected_file_patterns(current_text)

    if not packet_id:
        issues.append("CURRENT.md is missing Packet ID")

    if not status:
        issues.append("CURRENT.md is missing Status")

    nontrivial_changes = [path for path in changed_files if not path.endswith(".md") or path.startswith(("scripts/", ".github/"))]
    if nontrivial_changes and not status_allows_nontrivial_work(status):
        issues.append(
            "Implementation-like changes are present, but the active packet is not in an approved working state"
        )

    harness_changes = [path for path in changed_files if is_harness_path(path)]
    if harness_changes and not DURABLE_LOG_PATHS.intersection(changed_files):
        issues.append(
            "Harness changes are present without any durable log updates in CURRENT.md, DECISIONS.md, REVIEWS.md, or RELEASES.md"
        )

    if ".handoff/CURRENT.md" not in changed_files and harness_changes:
        warnings.append("Harness changes are present without a CURRENT.md note update")

    if packet_id and status.lower().startswith("review") and ".handoff/REVIEWS.md" not in changed_files:
        warnings.append(f"Packet {packet_id} is in review state and current changes do not touch REVIEWS.md")

    undeclared_paths = []
    for path in changed_files:
        if is_harness_path(path):
            continue
        if path in DURABLE_LOG_PATHS:
            continue
        if is_declared_affected_path(path, declared_affected_files):
            continue
        undeclared_paths.append(path)
    for path in undeclared_paths:
        warnings.append(f"Changed file is not declared under Affected Areas -> Files: {path}")

    return {"issues": issues, "warnings": warnings, "changed_files": changed_files}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_path", nargs="?", default=".", help="Path to the repository")
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    args = parser.parse_args()

    repo_root = Path(args.repo_path).resolve()
    result = check_scope(repo_root)
    status = "pass" if not result["issues"] else "fail"

    if args.json:
        print(json.dumps({"status": status, **result}, indent=2))
        return 0 if status == "pass" else 1

    print(f"Repository: {repo_root}")
    print(f"Status: {status}")
    print("Changed files:")
    for item in result.get("changed_files", []):
        print(f"  - {item}")
    if not result.get("changed_files"):
        print("  - none")
    print("Issues:")
    for item in result["issues"]:
        print(f"  - {item}")
    if not result["issues"]:
        print("  - none")
    print("Warnings:")
    for item in result["warnings"]:
        print(f"  - {item}")
    if not result["warnings"]:
        print("  - none")
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())