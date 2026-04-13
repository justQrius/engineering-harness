#!/usr/bin/env python3
"""
Surface repeated review findings so they can be promoted into guardrails.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


STOPWORDS = {
    "the", "and", "for", "that", "with", "this", "from", "into", "when", "then",
    "have", "has", "had", "are", "was", "were", "but", "not", "still", "only",
    "now", "after", "before", "their", "they", "them", "into", "does", "did",
    "across", "under", "over", "than", "just", "will", "would", "should",
}


def normalize_signature(line: str) -> str:
    tokens = re.findall(r"[a-z0-9]+", line.lower())
    meaningful = [token for token in tokens if token not in STOPWORDS and len(token) > 2]
    if not meaningful:
        return ""
    return " ".join(sorted(set(meaningful[:5])))


def scan_recurring_findings(reviews_path: Path) -> dict:
    issues: list[str] = []
    warnings: list[str] = []
    clusters: dict[str, list[str]] = defaultdict(list)

    if not reviews_path.exists():
        issues.append(f"Missing review log: {reviews_path}")
        return {"issues": issues, "warnings": warnings, "clusters": {}}

    in_key_findings = False
    for raw_line in reviews_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if stripped == "- Key findings:":
            in_key_findings = True
            continue
        if in_key_findings and stripped.startswith("- Required follow-up:"):
            in_key_findings = False
            continue
        if in_key_findings and stripped.startswith("- "):
            signature = normalize_signature(stripped[2:])
            if signature:
                clusters[signature].append(stripped[2:])

    recurring = {key: value for key, value in clusters.items() if len(value) >= 2}
    if not recurring:
        warnings.append("No recurring findings detected")

    return {"issues": issues, "warnings": warnings, "clusters": recurring}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("reviews_path", nargs="?", default=".handoff/REVIEWS.md", help="Path to REVIEWS.md")
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    args = parser.parse_args()

    reviews_path = Path(args.reviews_path).resolve()
    result = scan_recurring_findings(reviews_path)

    if args.json:
        print(json.dumps(result, indent=2))
        return 0 if not result["issues"] else 1

    print(f"Reviews: {reviews_path}")
    print("Recurring clusters:")
    if result["clusters"]:
        for signature, findings in result["clusters"].items():
            print(f"  - {signature}")
            for finding in findings:
                print(f"      * {finding}")
    else:
        print("  - none")
    print("Warnings:")
    for item in result["warnings"]:
        print(f"  - {item}")
    if not result["warnings"]:
        print("  - none")
    return 0 if not result["issues"] else 1


if __name__ == "__main__":
    raise SystemExit(main())