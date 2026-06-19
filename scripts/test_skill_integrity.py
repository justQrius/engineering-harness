#!/usr/bin/env python3
"""
Verify that the engineering-harness skill is internally consistent.
"""

from __future__ import annotations

import importlib.util
import re
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


def assert_exists(path: Path, label: str) -> None:
    if not path.exists():
        raise SystemExit(f"{label} missing: {path}")


def main() -> int:
    skill_root = Path(__file__).resolve().parent.parent
    template_root = skill_root / "assets" / "templates"

    audit_harness_module = load_module(skill_root / "scripts" / "audit_harness.py", "audit_harness")
    bootstrap_module = load_module(skill_root / "scripts" / "bootstrap_harness.py", "bootstrap_harness")

    for rel_path in audit_harness_module.REQUIRED_FILES:
        assert_exists(template_root / rel_path, "Template for required file")

    skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    for rel_path in re.findall(r"`scripts/([A-Za-z0-9_.-]+)`", skill_text):
        assert_exists(skill_root / "scripts" / rel_path, "Referenced script")
    for rel_path in re.findall(r"`references/([A-Za-z0-9_.-]+)`", skill_text):
        assert_exists(skill_root / "references" / rel_path, "Referenced reference doc")

    with tempfile.TemporaryDirectory() as temp_dir:
        repo_root = Path(temp_dir) / "integrity-repo"
        repo_root.mkdir(parents=True, exist_ok=True)
        bootstrap_module.copy_templates(template_root, repo_root, "Integrity Repo", force=True)

        audit_result = audit_harness_module.audit_repo(repo_root)
        if audit_result["required_missing"]:
            raise SystemExit(f"Bootstrapped repo missing required files: {audit_result['required_missing']}")

    subprocess.run(
        ["python", str(skill_root / "scripts" / "test_template_audit_contract.py")],
        check=True,
    )
    subprocess.run(
        ["python", str(skill_root / "scripts" / "test_harness_failure_modes.py")],
        check=True,
    )

    print("Engineering-harness skill integrity: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())