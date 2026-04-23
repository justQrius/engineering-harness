#!/usr/bin/env python3
"""
Advance the active packet through legal states and keep durable logs in sync.
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path


LEGAL_TRANSITIONS = {
    "draft": {"approved"},
    "approved": {"in-progress", "review-requested", "done"},
    "in-progress": {"review-requested", "approved"},
    "review-requested": {"review-complete", "approved", "in-progress"},
    "review-complete": {"approved", "done"},
    "done": set(),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def parse_header_value(text: str, field: str) -> str:
    match = re.search(rf"^- {re.escape(field)}:\s*(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def normalize_status(status: str) -> str:
    return status.strip().lower()


def next_review_id(reviews_text: str) -> str:
    matches = [int(value) for value in re.findall(r"### R(\d+)\b", reviews_text)]
    return f"R{(max(matches) + 1 if matches else 1):03d}"


def next_release_id(releases_text: str) -> str:
    matches = [int(value) for value in re.findall(r"### REL-(\d+)\b", releases_text)]
    return f"REL-{(max(matches) + 1 if matches else 1):03d}"


def update_current(current_text: str, new_status: str, timestamp: str) -> str:
    current_text = re.sub(
        r"(^- Status:\s*).+$",
        lambda match: f"{match.group(1)}{new_status}",
        current_text,
        count=1,
        flags=re.MULTILINE,
    )
    current_text = re.sub(
        r"(^- Updated:\s*).+$",
        lambda match: f"{match.group(1)}{timestamp}",
        current_text,
        count=1,
        flags=re.MULTILINE,
    )
    return current_text


def update_backlog(backlog_text: str, packet_id: str, new_status: str, timestamp: str) -> str:
    pattern = re.compile(
        rf"(^- `{re.escape(packet_id)}`.+?\n)(\s+Status:\s*)(.+)$",
        flags=re.MULTILINE,
    )
    return pattern.sub(rf"\1\2{new_status} as of {timestamp[:10]} UTC", backlog_text, count=1)


def ensure_review_stub(reviews_text: str, packet_id: str, timestamp: str) -> str:
    if packet_id in reviews_text:
        return reviews_text
    review_id = next_review_id(reviews_text)
    stub = (
        f"\n### {review_id} - {packet_id} review ({timestamp})\n\n"
        f"- Packet: `{packet_id}`\n"
        f"- Reviewer: `TBD`\n"
        f"- Review type: `implementation or framing review`\n"
        f"- Outcome: `pending`\n"
        f"- Key findings:\n"
        f"  - add findings here\n"
        f"- Required follow-up:\n"
        f"  - add follow-up here\n"
    )
    return reviews_text.rstrip() + "\n" + stub


def ensure_release_stub(releases_text: str, packet_id: str, title: str, timestamp: str) -> str:
    if packet_id in releases_text:
        return releases_text
    release_id = next_release_id(releases_text)
    stub = (
        f"\n### {release_id} - {title} ({timestamp})\n\n"
        f"- Version or identifier: `{packet_id}`\n"
        f"- Scope:\n"
        f"  - summarize deployable scope here\n"
        f"- Risk:\n"
        f"  - summarize operational risk here\n"
        f"- Deploy notes:\n"
        f"  - add deploy notes here\n"
        f"- Rollback notes:\n"
        f"  - add rollback notes here\n"
        f"- Follow-up:\n"
        f"  - add follow-up here\n"
    )
    return releases_text.rstrip() + "\n" + stub


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("new_status", help="Target packet status")
    parser.add_argument("repo_path", nargs="?", default=".", help="Path to the repository")
    args = parser.parse_args()

    repo_root = Path(args.repo_path).resolve()
    current_path = repo_root / ".handoff" / "CURRENT.md"
    backlog_path = repo_root / ".handoff" / "BACKLOG.md"
    reviews_path = repo_root / ".handoff" / "REVIEWS.md"
    releases_path = repo_root / ".handoff" / "RELEASES.md"

    current_text = load_text(current_path)
    backlog_text = load_text(backlog_path)
    reviews_text = load_text(reviews_path)
    releases_text = load_text(releases_path)

    packet_id = parse_header_value(current_text, "Packet ID")
    title = parse_header_value(current_text, "Title")
    current_status = normalize_status(parse_header_value(current_text, "Status"))
    new_status = normalize_status(args.new_status)
    if new_status not in LEGAL_TRANSITIONS:
        raise SystemExit(f"Unsupported packet status: {args.new_status}")
    if new_status not in LEGAL_TRANSITIONS.get(current_status, set()):
        raise SystemExit(f"Illegal packet transition: {current_status} -> {new_status}")

    timestamp = utc_now()
    write_text(current_path, update_current(current_text, new_status, timestamp))
    write_text(backlog_path, update_backlog(backlog_text, packet_id, new_status, timestamp))

    if new_status == "review-requested":
        write_text(reviews_path, ensure_review_stub(reviews_text, packet_id, timestamp))
    if new_status == "done":
        write_text(releases_path, ensure_release_stub(releases_text, packet_id, title, timestamp))

    print(f"Packet {packet_id} transitioned {current_status} -> {new_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())