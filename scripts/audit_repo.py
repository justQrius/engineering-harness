#!/usr/bin/env python3
"""
Validate the active packet and core repo-operating structure.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED_HEADER_FIELDS = [
    "Packet ID",
    "Title",
    "Status",
    "Gate",
    "Owner",
    "Driver agent",
    "Reviewer agent",
    "Created",
    "Updated",
]

REQUIRED_PACKET_SECTIONS = [
    "Problem",
    "User / Job To Be Done",
    "Vision Link",
    "Hypothesis",
    "User Outcome / UX Constraint",
    "Root Constraint / Invariant",
    "Assumptions To Test",
    "Smallest Learning Slice",
    "Thin-Slice Scope",
    "Out Of Scope",
    "Affected Areas",
    "References",
    "Acceptance Criteria",
    "Tests And Evals",
    "Deployment Impact",
    "Rollback Plan",
]

REQUIRED_TEST_MARKERS = [
    "- Tests to add or update:",
    "- Evals or scenarios to add or run:",
    "- Integration or boundary checks:",
    "- Manual smoke checks:",
]

REQUIRED_REFERENCE_MARKERS = [
    "### Internal",
    "### External",
    "- Official docs:",
    "- Reference implementations / repos / examples:",
]

ALLOWED_STATUS_PREFIXES = [
    "draft",
    "approved",
    "in-progress",
    "review-requested",
    "review-complete",
    "done",
]


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_header_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    in_header = False
    for line in text.splitlines():
        if line.strip() == "## Header":
            in_header = True
            continue
        if in_header and line.startswith("## "):
            break
        if in_header and line.startswith("- ") and ":" in line:
            key, value = line[2:].split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def has_section(text: str, section_name: str) -> bool:
    pattern = rf"^## {re.escape(section_name)}\s*$"
    return re.search(pattern, text, flags=re.MULTILINE) is not None


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
    return lines[start:end]


def extract_current_repo_invariants(text: str) -> list[str]:
    return [line.rstrip() for line in extract_section_lines(text, "Current Repo Invariants") if line.strip()]


def status_is_allowed(status: str) -> bool:
    normalized = status.strip().lower()
    return any(normalized.startswith(prefix) for prefix in ALLOWED_STATUS_PREFIXES)


def audit_repo(repo_root: Path) -> dict:
    issues: list[str] = []
    warnings: list[str] = []

    current_path = repo_root / ".handoff" / "CURRENT.md"
    reviews_path = repo_root / ".handoff" / "REVIEWS.md"
    releases_path = repo_root / ".handoff" / "RELEASES.md"
    template_path = repo_root / ".handoff" / "templates" / "work-packet.md"
    agents_path = repo_root / "AGENTS.md"
    claude_path = repo_root / "CLAUDE.md"

    for path in [current_path, reviews_path, releases_path, template_path]:
        if not path.exists():
            issues.append(f"Missing required file: {path.relative_to(repo_root).as_posix()}")

    if issues:
        return {"issues": issues, "warnings": warnings}

    current_text = load_text(current_path)
    reviews_text = load_text(reviews_path)
    releases_text = load_text(releases_path)
    template_text = load_text(template_path)
    header_fields = parse_header_fields(current_text)

    for field in REQUIRED_HEADER_FIELDS:
        if not header_fields.get(field):
            issues.append(f"CURRENT.md missing header field: {field}")

    status = header_fields.get("Status", "")
    if status and not status_is_allowed(status):
        issues.append(f"CURRENT.md has unsupported status value: {status}")

    packet_id = header_fields.get("Packet ID", "")
    if packet_id and packet_id not in reviews_text and status.lower().startswith("review"):
        issues.append(f"Packet {packet_id} is in review state but has no matching review log entry")
    if packet_id and status.lower().startswith("done") and packet_id not in releases_text:
        warnings.append(f"Packet {packet_id} is done but does not appear in RELEASES.md")

    for section in REQUIRED_PACKET_SECTIONS:
        if not has_section(current_text, section):
            issues.append(f"CURRENT.md missing section: {section}")

    for marker in REQUIRED_TEST_MARKERS:
        if marker not in current_text:
            issues.append(f"CURRENT.md missing test/eval marker: {marker}")

    for marker in REQUIRED_REFERENCE_MARKERS:
        if marker not in current_text:
            issues.append(f"CURRENT.md missing references marker: {marker}")

    for section in [
        "User / Job To Be Done",
        "User Outcome / UX Constraint",
        "Root Constraint / Invariant",
        "Assumptions To Test",
        "Smallest Learning Slice",
    ]:
        if not has_section(template_text, section):
            issues.append(f"work-packet template missing section: {section}")

    if "[2026-" in template_text:
        warnings.append("work-packet template appears to contain dated placeholder note entries")

    if agents_path.exists() and claude_path.exists():
        agents_invariants = extract_current_repo_invariants(load_text(agents_path))
        claude_invariants = extract_current_repo_invariants(load_text(claude_path))
        if agents_invariants != claude_invariants:
            warnings.append("AGENTS.md and CLAUDE.md differ in Current Repo Invariants")

    return {"issues": issues, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_path", nargs="?", default=".", help="Path to the repository to audit")
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    args = parser.parse_args()

    repo_root = Path(args.repo_path).resolve()
    result = audit_repo(repo_root)
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