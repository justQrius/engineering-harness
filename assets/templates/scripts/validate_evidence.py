#!/usr/bin/env python3
"""
Validate that an evidence bundle exists and is complete enough for review.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate_evidence(bundle_path: Path, manifest_path: Path | None) -> dict:
    issues: list[str] = []
    warnings: list[str] = []
    checked_files: list[str] = []

    if not bundle_path.exists():
        issues.append(f"Evidence bundle does not exist: {bundle_path}")
        return {"issues": issues, "warnings": warnings, "checked_files": checked_files}
    if not bundle_path.is_dir():
        issues.append(f"Evidence bundle is not a directory: {bundle_path}")
        return {"issues": issues, "warnings": warnings, "checked_files": checked_files}

    bundle_files = sorted(path for path in bundle_path.rglob("*") if path.is_file())
    if not bundle_files:
        issues.append("Evidence bundle is empty")
        return {"issues": issues, "warnings": warnings, "checked_files": checked_files}

    if manifest_path is None:
        candidate = bundle_path / "evidence-manifest.txt"
        if candidate.exists():
            manifest_path = candidate

    if manifest_path and manifest_path.exists():
        manifest_entries = [
            line.strip()
            for line in manifest_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        for rel_path in manifest_entries:
            target = bundle_path / rel_path
            checked_files.append(rel_path)
            if not target.exists():
                issues.append(f"Manifest entry missing from bundle: {rel_path}")
            elif target.stat().st_size == 0:
                issues.append(f"Manifest entry is empty: {rel_path}")
    else:
        for file_path in bundle_files:
            rel_path = file_path.relative_to(bundle_path).as_posix()
            checked_files.append(rel_path)
            if file_path.stat().st_size == 0:
                issues.append(f"Evidence file is empty: {rel_path}")

    return {"issues": issues, "warnings": warnings, "checked_files": checked_files}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle_path", help="Path to the evidence bundle directory")
    parser.add_argument("--manifest", help="Optional explicit manifest path")
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    args = parser.parse_args()

    bundle_path = Path(args.bundle_path).resolve()
    manifest_path = Path(args.manifest).resolve() if args.manifest else None
    result = validate_evidence(bundle_path, manifest_path)
    status = "pass" if not result["issues"] else "fail"

    if args.json:
        print(json.dumps({"status": status, **result}, indent=2))
        return 0 if status == "pass" else 1

    print(f"Bundle: {bundle_path}")
    print(f"Status: {status}")
    print("Checked files:")
    for item in result["checked_files"]:
        print(f"  - {item}")
    if not result["checked_files"]:
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