#!/usr/bin/env python3
"""
Warn when AGENTS.md and CLAUDE.md drift structurally or in repo invariants.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_headers(text: str) -> list[str]:
    headers = re.findall(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE)
    normalized = []
    for header in headers:
        if header.startswith("Rules for "):
            normalized.append("Rules for Agent")
        else:
            normalized.append(header)
    return normalized


def extract_section_lines(text: str, section_name: str) -> list[str]:
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == f"## {section_name}":
            start = index + 1
            break
    if start is None:
        return []

    end = len(lines)
    for index in range(start, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return [line.rstrip() for line in lines[start:end] if line.strip()]


def check_agent_drift(repo_root: Path) -> dict:
    issues: list[str] = []
    warnings: list[str] = []

    agents_path = repo_root / "AGENTS.md"
    claude_path = repo_root / "CLAUDE.md"
    for path in [agents_path, claude_path]:
        if not path.exists():
            issues.append(f"Missing required file: {path.name}")

    if issues:
        return {"issues": issues, "warnings": warnings}

    agents_text = load_text(agents_path)
    claude_text = load_text(claude_path)

    agents_headers = extract_headers(agents_text)
    claude_headers = extract_headers(claude_text)
    if agents_headers != claude_headers:
        warnings.append("AGENTS.md and CLAUDE.md differ in section headers")

    agents_invariants = extract_section_lines(agents_text, "Current Repo Invariants")
    claude_invariants = extract_section_lines(claude_text, "Current Repo Invariants")
    if agents_invariants != claude_invariants:
        warnings.append("AGENTS.md and CLAUDE.md differ in Current Repo Invariants")

    return {"issues": issues, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_path", nargs="?", default=".", help="Path to the repository")
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    args = parser.parse_args()

    repo_root = Path(args.repo_path).resolve()
    result = check_agent_drift(repo_root)
    status = "pass" if not result["issues"] else "fail"

    if args.json:
        print(json.dumps({"status": status, **result}, indent=2))
        return 0 if status == "pass" else 1

    print(f"Repository: {repo_root}")
    print(f"Status: {status}")
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