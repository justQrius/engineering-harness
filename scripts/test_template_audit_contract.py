#!/usr/bin/env python3
"""
Verify that the packet template and audit script agree on required structure.
"""

from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def render_current_from_template(template_text: str) -> str:
    replacements = {
        "- Packet ID:": "- Packet ID: PKT-TEST",
        "- Title:": "- Title: Template contract test packet",
        "- Status: draft | approved | in-progress | review-requested | review-complete | done": "- Status: draft",
        "- Gate:": "- Gate: Template contract validation only.",
        "- Owner:": "- Owner: test-owner",
        "- Driver agent:": "- Driver agent: Codex",
        "- Reviewer agent:": "- Reviewer agent: Claude Code",
        "- Parallel support agent:": "- Parallel support agent: OpenCode",
        "- Support scope:": "- Support scope: template contract self-test only",
        "- Research/design support:": "- Research/design support: none",
        "- Created:": "- Created: 2026-01-01T00:00:00Z",
        "- Updated:": "- Updated: 2026-01-01T00:00:00Z",
        "What problem are we solving?": "Validate that the packet template satisfies the audit contract.",
        "Whose job are we helping, and what outcome are they trying to achieve?": "Harness maintainers need a packet template that passes the repo audit without manual repair.",
        "Which product or doctrine goals does this work serve?": "This keeps the engineering harness self-consistent.",
        "What do we believe this change will improve?": "Template and audit drift will be caught before repos are bootstrapped.",
        "What user-facing outcome should improve, and what workflow or UX constraint must\nremain true?": "Harness authors should be able to trust scaffolded packets; the template must remain concise and complete.",
        "What must remain true even if implementation details change?": "The packet template must satisfy the audit's required structure.",
        "What key assumptions does this slice need to validate or invalidate?": "- The template still contains every required section and marker.",
        "What is the smallest slice that delivers value and teaches something important?": "Render one filled packet from the template and run the audit against it.",
        "What is included in this iteration?": "- template contract validation only",
        "What is intentionally deferred?": "- broader repo bootstrap tests",
        "- Files:": "- Files:\n  - .handoff/CURRENT.md\n  - .handoff/REVIEWS.md\n  - .handoff/templates/work-packet.md",
        "- Systems:": "- Systems:\n  - packet template validation",
        "- Trust boundaries:": "- Trust boundaries:\n  - harness maintainer to audit script",
        "- Relevant `research/` docs:": "- Relevant `research/` docs:\n  - none",
        "- Relevant `docs/planning/` docs:": "- Relevant `docs/planning/` docs:\n  - none",
        "- Relevant `docs/design/` docs:": "- Relevant `docs/design/` docs:\n  - none",
        "- Relevant `docs/architecture/` docs:": "- Relevant `docs/architecture/` docs:\n  - none",
        "- Relevant `docs/engineering/` docs:": "- Relevant `docs/engineering/` docs:\n  - docs/engineering/17-mechanical-enforcement.md",
        "- Relevant local code:": "- Relevant local code:\n  - scripts/audit_repo.py",
        "- Official docs:": "- Official docs:\n  - none",
        "- Reference implementations / repos / examples:": "- Reference implementations / repos / examples:\n  - none",
        "- Other supporting sources:": "- Other supporting sources:\n  - none",
        "## Acceptance Criteria\n\n- ": "## Acceptance Criteria\n\n- the template renders a packet that passes `scripts/audit_repo.py`\n",
        "- Tests to add or update:": "- Tests to add or update:\n  - scripts/test_template_audit_contract.py",
        "- Evals or scenarios to add or run:": "- Evals or scenarios to add or run:\n  - render one filled packet from the template",
        "- Integration or boundary checks:": "- Integration or boundary checks:\n  - python scripts/audit_repo.py .",
        "- Manual smoke checks:": "- Manual smoke checks:\n  - inspect the rendered CURRENT.md",
        "- Runtime or infrastructure impact:": "- Runtime or infrastructure impact:\n  - none",
        "- Config or secret impact:": "- Config or secret impact:\n  - none",
        "- Observability impact:": "- Observability impact:\n  - audit output only",
        "How do we back this out if needed?": "Restore the previous packet template and rerun the contract test.",
        "- add real timestamped notes only when they exist": "- [Test][2026-01-01T00:00:00Z] Contract test packet rendered from template.",
        "- list expected evidence artifacts here when review depends on a real bundle": "- none",
    }
    rendered = template_text
    for source, target in replacements.items():
        rendered = rendered.replace(source, target)
    return rendered


def main() -> int:
    skill_root = Path(__file__).resolve().parent.parent
    template_root = skill_root / "assets" / "templates"
    bootstrap_module = load_module(skill_root / "scripts" / "bootstrap_harness.py", "bootstrap_harness")

    with tempfile.TemporaryDirectory() as temp_dir:
        repo_root = Path(temp_dir) / "contract-repo"
        repo_root.mkdir(parents=True, exist_ok=True)
        bootstrap_module.copy_templates(template_root, repo_root, "Template Contract Repo", force=True)

        template_path = repo_root / ".handoff" / "templates" / "work-packet.md"
        current_path = repo_root / ".handoff" / "CURRENT.md"
        current_path.write_text(render_current_from_template(template_path.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")

        audit_module = load_module(repo_root / "scripts" / "audit_repo.py", "repo_audit")
        result = audit_module.audit_repo(repo_root)
        if result["issues"]:
            raise SystemExit(f"Template/audit contract failed: {result['issues']}")

    print("Template/audit contract test: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())