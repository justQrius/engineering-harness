#!/usr/bin/env python3
"""
Audit a repository for engineering-harness coverage.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    ".handoff/CURRENT.md",
    ".handoff/BACKLOG.md",
    ".handoff/DECISIONS.md",
    ".handoff/REVIEWS.md",
    ".handoff/RELEASES.md",
    ".handoff/templates/work-packet.md",
    "docs/planning/README.md",
    "docs/design/README.md",
    "docs/architecture/README.md",
    "docs/engineering/README.md",
    "docs/engineering/01-product-doctrine.md",
    "docs/engineering/02-engineering-doctrine.md",
    "docs/engineering/03-source-policy.md",
    "docs/engineering/10-development-loop.md",
    "docs/engineering/11-definition-of-ready.md",
    "docs/engineering/12-definition-of-done.md",
    "docs/engineering/13-review-checklist.md",
    "docs/engineering/14-release-and-versioning.md",
    "docs/engineering/15-implementation-development-principles.md",
    "docs/engineering/16-first-principles-and-design-thinking.md",
    "docs/engineering/17-mechanical-enforcement.md",
    "research/INDEX.md",
    "scripts/audit_repo.py",
    "scripts/check_packet_scope.py",
    "scripts/packet_transition.py",
    "scripts/validate_evidence.py",
    "scripts/check_agent_drift.py",
    "scripts/run_project_checks.py",
]

OPTIONAL_DIRS = [
    "docs/architecture/drafts",
    "docs/operations",
    "ops",
    ".handoff/archive",
]

OPTIONAL_FILES = [
    ".github/workflows/harness-checks.yml",
    "Taskfile.yml",
    "scripts/scan_recurring_findings.py",
]

STACK_MARKERS = {
    "go": ["go.mod"],
    "node": ["package.json"],
    "python": ["pyproject.toml", "setup.py", "requirements.txt"],
    "rust": ["Cargo.toml"],
    "docker": ["Dockerfile"],
    "dotnet": ["*.sln", "*.csproj"],
    "java": ["pom.xml", "build.gradle", "build.gradle.kts"],
}

STACK_RECOMMENDATIONS = {
    "go": ["go vet ./...", "go test ./...", "GOOS=linux GOARCH=amd64 go build ./...", "optional: govulncheck ./..."],
    "node": ["npm ci when a lockfile exists", "npm test", "optional: npm audit --audit-level=high"],
    "python": ["python -m pytest", "optional: pip-audit"],
    "rust": ["cargo test", "optional: cargo audit"],
    "docker": ["docker build sanity check where relevant"],
    "dotnet": ["dotnet test"],
    "java": ["mvn test or gradle test"],
}


def detect_stack(repo_path: Path) -> list[str]:
    detected: list[str] = []
    for stack_name, markers in STACK_MARKERS.items():
        for marker in markers:
            if any(repo_path.glob(marker)):
                detected.append(stack_name)
                break
    return detected


def audit_repo(repo_path: Path) -> dict:
    present = []
    missing = []
    for rel_path in REQUIRED_FILES:
        path = repo_path / rel_path
        if path.exists():
            present.append(rel_path)
        else:
            missing.append(rel_path)

    optional_present = []
    optional_missing = []
    for rel_path in OPTIONAL_DIRS:
        path = repo_path / rel_path
        if path.exists():
            optional_present.append(rel_path)
        else:
            optional_missing.append(rel_path)

    for rel_path in OPTIONAL_FILES:
        path = repo_path / rel_path
        if path.exists():
            optional_present.append(rel_path)
        else:
            optional_missing.append(rel_path)

    if len(missing) == 0:
        status = "complete"
    elif len(present) == 0:
        status = "absent"
    else:
        status = "partial"

    detected_stack = detect_stack(repo_path)
    recommendations = []
    for stack_name in detected_stack:
        recommendations.extend(STACK_RECOMMENDATIONS.get(stack_name, []))

    return {
        "repo_path": str(repo_path.resolve()),
        "status": status,
        "required_present": present,
        "required_missing": missing,
        "optional_present": optional_present,
        "optional_missing": optional_missing,
        "detected_stack": detected_stack,
        "recommended_ci_additions": recommendations,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_path", help="Path to the repository to audit")
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    args = parser.parse_args()

    repo_path = Path(args.repo_path).resolve()
    if not repo_path.exists():
        raise SystemExit(f"Repository path does not exist: {repo_path}")

    result = audit_repo(repo_path)
    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    print(f"Repository: {result['repo_path']}")
    print(f"Status: {result['status']}")
    print("Required present:")
    for rel_path in result["required_present"]:
        print(f"  - {rel_path}")
    print("Required missing:")
    for rel_path in result["required_missing"]:
        print(f"  - {rel_path}")
    print("Optional present:")
    for rel_path in result["optional_present"]:
        print(f"  - {rel_path}")
    print("Optional missing:")
    for rel_path in result["optional_missing"]:
        print(f"  - {rel_path}")
    print("Detected stack:")
    for item in result["detected_stack"]:
        print(f"  - {item}")
    if not result["detected_stack"]:
        print("  - none")
    print("Recommended CI additions:")
    for item in result["recommended_ci_additions"]:
        print(f"  - {item}")
    if not result["recommended_ci_additions"]:
        print("  - none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())