#!/usr/bin/env python3
"""
Bootstrap the engineering harness into a repository by copying starter templates.

In init mode: create all harness files (skip existing unless --force).
In retrofit mode: create missing files, then merge key sections into existing
files that lack them (CLAUDE.md, AGENTS.md).
"""

from __future__ import annotations

import argparse
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


# Sections that should be merged into existing files during retrofit.
# Each entry: (file_path, section_heading, section_content)
# The section_heading is used to detect if the section already exists.
# section_content is the full markdown block to append.

KB_SECTION = """\
## Cross-Project Knowledge Base

The Knowledge Base at `D:/Projects/KnowledgeBase` is a persistent, compounding
intelligence layer shared across all projects. Use GBrain
(operations: query, search, sync, extract, stats, capture) to search for prior art
before research and to capture durable learnings at session end.

| Operation | Command (from any project) | When |
|-----------|---------------------------|------|
| **Query** | `gbrain query "question"` or `gbrain search "topic"` | Before research — check what's already known |
| **Capture** | Create `Raw/Sessions/`, wiki pages, update `index.md` and `log.md` | After significant work — capture durable findings |
| **Sync** | `gbrain sync` then `gbrain embed --stale` | When pages have been added or edited |
| **Extract** | `gbrain extract all` | After sync, periodically |
| **Stats** | `gbrain stats` | At session start to check KB health |

Only promote learnings that would be useful in a different repo. Repo-specific
decisions stay in `.handoff/DECISIONS.md`.
"""

MERGE_SECTIONS = [
    # (relative_path, section_heading, section_content)
    ("CLAUDE.md", "Cross-Project Knowledge Base", KB_SECTION),
    ("AGENTS.md", "Cross-Project Knowledge Base", KB_SECTION),
]

# Inline replacements for retrofit: patterns to find in existing files and
# their KB-aware replacements. Only applied if the pattern exists and the
# KB reference is missing.
INLINE_REPLACEMENTS = [
    # (file_glob, search_pattern, replacement)
    # Each pattern targets old /kb slash commands or missing KB references.
    # Only applied if the pattern exists AND KB script-style references are absent.

    # Development Loop Step 2 — check prior art (old: no KB reference)
    (
        "*.md",
        r"Check prior art: research/, docs/, decisions",
        "Check prior art: query the Knowledge Base, research/, docs/, decisions",
    ),
    # Development Loop Step 10 — fold learning back (old: /kb session)
    (
        "*.md",
        r"capture with `/kb session`",
        "capture durable learnings via the Knowledge Base (see Cross-Project Knowledge Base section)",
    ),
    # Session-End Checklist — old: /kb session
    (
        "*.md",
        r"capture with `/kb session`",
        "capture via the Knowledge Base (see Cross-Project Knowledge Base section)",
    ),
]


def substitute_placeholders(text: str, project_name: str) -> str:
    today_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return (
        text.replace("{{PROJECT_NAME}}", project_name)
        .replace("{{TODAY_UTC}}", today_utc)
    )


def copy_templates(template_root: Path, repo_root: Path, project_name: str, force: bool) -> list[str]:
    written = []
    for source in template_root.rglob("*"):
        if source.is_dir():
            continue
        relative = source.relative_to(template_root)
        target = repo_root / relative
        if target.exists() and not force:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        content = source.read_text(encoding="utf-8")
        target.write_text(substitute_placeholders(content, project_name), encoding="utf-8")
        written.append(str(relative).replace("\\", "/"))
    return written


def has_section(file_path: Path, heading: str) -> bool:
    """Check if a markdown file contains a section with the given heading."""
    if not file_path.exists():
        return False
    content = file_path.read_text(encoding="utf-8")
    # Match ## Heading or ## Heading (with any trailing text on the line)
    pattern = re.compile(r"^##\s+" + re.escape(heading), re.MULTILINE)
    return bool(pattern.search(content))


def merge_section(file_path: Path, heading: str, section_content: str) -> bool:
    """Append a section to a file if the heading doesn't already exist.

    Returns True if the section was merged, False if it already existed.
    """
    if has_section(file_path, heading):
        return False

    content = file_path.read_text(encoding="utf-8")

    # Ensure there's a blank line before the new section
    if not content.endswith("\n"):
        content += "\n"
    if not content.endswith("\n\n"):
        content += "\n"

    content += section_content.rstrip() + "\n"
    file_path.write_text(content, encoding="utf-8")
    return True


def has_kb_reference(file_path: Path, pattern: str) -> bool:
    """Check if a file contains a specific text pattern."""
    if not file_path.exists():
        return False
    content = file_path.read_text(encoding="utf-8")
    return pattern in content


def apply_inline_replacements(repo_root: Path) -> list[str]:
    """Apply inline KB-aware replacements to existing files.

    Only replaces if the pattern exists AND the KB reference is missing.
    Returns list of changes made.
    """
    changes = []
    for file_glob, search_pattern, replacement in INLINE_REPLACEMENTS:
        for file_path in repo_root.glob(file_glob):
            if file_path.is_dir():
                continue
            # Only process top-level md files (AGENTS.md, CLAUDE.md)
            if file_path.parent != repo_root:
                continue
            content = file_path.read_text(encoding="utf-8")

            # Check if the search pattern exists
            if not re.search(search_pattern, content):
                continue

            # Check if KB reference already exists (skip if it does)
            kb_markers = ["Knowledge Base", "gbrain", "gbrain query"]
            if any(marker in content for marker in kb_markers):
                # The line already has a KB reference — don't double up
                # But check if it's the old /kb command style that needs updating
                if "/kb " in content and "gbrain" not in content:
                    # Has /kb commands but not script-style references — needs update
                    pass
                else:
                    continue  # Already has KB references, skip

            new_content = re.sub(search_pattern, replacement, content)
            if new_content != content:
                file_path.write_text(new_content, encoding="utf-8")
                changes.append(f"{file_path.name}: updated inline KB reference")
    return changes


def merge_missing_sections(repo_root: Path) -> tuple[list[str], list[str]]:
    """Merge KB sections into existing files that lack them.

    Returns (merged, skipped) lists of file descriptions.
    """
    merged = []
    skipped = []
    for rel_path, heading, section_content in MERGE_SECTIONS:
        file_path = repo_root / rel_path
        if not file_path.exists():
            skipped.append(f"{rel_path}: file does not exist (will be scaffolded)")
            continue
        if merge_section(file_path, heading, section_content):
            merged.append(f"{rel_path}: added '{heading}' section")
        else:
            skipped.append(f"{rel_path}: '{heading}' section already present")
    return merged, skipped


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bootstrap the engineering harness into a repository.",
        epilog="In retrofit mode, missing files are scaffolded and key sections "
               "are merged into existing files (CLAUDE.md, AGENTS.md). "
               "In init mode, all harness files are created (existing files "
               "are skipped unless --force is set).",
    )
    parser.add_argument("repo_path", help="Path to the target repository")
    parser.add_argument("--project-name", required=True, help="Human-readable project name")
    parser.add_argument(
        "--mode",
        choices=["init", "retrofit"],
        default="retrofit",
        help="Bootstrap mode. Retrofit merges sections into existing files; "
             "init only creates missing files.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    repo_root = Path(args.repo_path).resolve()
    repo_root.mkdir(parents=True, exist_ok=True)

    script_dir = Path(__file__).resolve().parent
    template_root = script_dir.parent / "assets" / "templates"

    # Step 1: Copy templates (scaffold missing files)
    written = copy_templates(template_root, repo_root, args.project_name, args.force)

    print(f"Repository: {repo_root}")
    print(f"Mode: {args.mode}")
    print(f"Force overwrite: {'yes' if args.force else 'no'}")
    print()
    print("Files written:")
    for rel_path in written:
        print(f"  - {rel_path}")
    if not written:
        print("  - none (all files already exist)")

    # Step 2: In retrofit mode, merge key sections into existing files
    if args.mode == "retrofit":
        print()
        print("Merging sections into existing files:")

        # Apply inline replacements FIRST (before adding the KB section,
        # so old /kb references get updated before detection logic sees
        # "Knowledge Base" text from the appended section)
        inline_changes = apply_inline_replacements(repo_root)
        for item in inline_changes:
            print(f"  + {item}")

        # Then merge standalone sections (KB section, etc.)
        merged, skipped = merge_missing_sections(repo_root)
        for item in merged:
            print(f"  + {item}")
        for item in skipped:
            print(f"  = {item}")

        if not merged and not inline_changes:
            print("  - nothing to merge (all sections already present)")

    print()
    print("Next steps:")
    if args.mode == "init":
        print("  1. Fill project layout, runtime, trust-boundary, and deployment specifics")
        print("  2. Create the first backlog or current packet if work is ready")
        print("  3. Assign agent roles in the collaboration table")
    else:
        print("  1. Compare existing docs against the harness baseline")
        print("  2. Merge real local truth into the harness docs")
        print("  3. Add a retrofit packet if the migration itself is substantial")
    print("  4. Run: python scripts/audit_repo.py (from within the repo)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())