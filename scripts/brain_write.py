#!/usr/bin/env python3
"""Validate and append typed brain records.

The writer produces two append-only artifacts:
1. JSONL event ledger, suitable for deterministic projections.
2. Markdown event page, suitable for GBrain sync/search/link extraction.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from uuid import uuid4

from brain_schema import SCHEMA_VERSION, ValidationError, known_ids_from_jsonl, validate_record


def main() -> int:
    parser = argparse.ArgumentParser(description="Typed brain validator/writer")
    sub = parser.add_subparsers(dest="command", required=True)

    validate_parser = sub.add_parser("validate", help="Validate one JSON record")
    validate_parser.add_argument("record", type=Path)
    validate_parser.add_argument("--ledger", type=Path)

    write_parser = sub.add_parser("write", help="Append one valid JSON record")
    write_parser.add_argument("record", type=Path)
    write_parser.add_argument("--ledger", type=Path, default=Path.home() / ".gbrain" / "typed" / "events.jsonl")
    write_parser.add_argument(
        "--pages-dir",
        type=Path,
        default=Path.home() / "KnowledgeBase" / "TypedBrain" / "events",
    )

    args = parser.parse_args()
    try:
        if args.command == "validate":
            record = load_record(args.record)
            validate_record(record, load_known_ids(args.ledger))
            print("valid")
            return 0
        if args.command == "write":
            record = load_record(args.record)
            known_ids = load_known_ids(args.ledger)
            validate_record(record, known_ids)
            event = build_event(record)
            append_event(args.ledger, event)
            page = write_markdown_event(args.pages_dir, event)
            print(f"wrote ledger={args.ledger}")
            print(f"wrote page={page}")
            return 0
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 2


def load_record(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValidationError("record JSON must be an object")
    return data


def load_known_ids(path: Path | None) -> set[str] | None:
    if path is None:
        return None
    if not path.exists():
        return set()
    return known_ids_from_jsonl(path.read_text(encoding="utf-8").splitlines())


def build_event(record: dict) -> dict:
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "schema_version": SCHEMA_VERSION,
        "event_id": str(uuid4()),
        "recorded_at": now,
        "record": record,
    }


def append_event(ledger: Path, event: dict) -> None:
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")


def write_markdown_event(pages_dir: Path, event: dict) -> Path:
    pages_dir.mkdir(parents=True, exist_ok=True)
    record = event["record"]
    stamp = event["recorded_at"].replace(":", "").replace("-", "")
    filename = f"{stamp}-{record['type'].lower()}-{slug_filename(record['id'])}-{event['event_id']}.md"
    path = pages_dir / filename
    path.write_text(render_markdown_event(event), encoding="utf-8")
    return path


def render_markdown_event(event: dict) -> str:
    record = event["record"]
    title = record.get("title") or record.get("name") or record.get("decision") or record["id"]
    frontmatter = {
        "type": "typed_event",
        "typed_node_type": record["type"],
        "typed_id": record["id"],
        "schema_version": event["schema_version"],
        "event_id": event["event_id"],
        "recorded_at": event["recorded_at"],
        "source_links": record["source_links"],
    }
    summary = summarize_record(record)
    lines = ["---"]
    for key, value in frontmatter.items():
        lines.append(f"{key}: {yaml_scalar(value)}")
    lines.extend(
        [
            "---",
            "",
            f"# {record['type']}: {title}",
            "",
            "## Summary",
            "",
            summary,
            "",
            "## Timeline Event",
            "",
            f"- Recorded at: {event['recorded_at']}",
            f"- Created at: {record['created_at']}",
            f"- Node type: {record['type']}",
            f"- Typed id: {record['id']}",
        ]
    )
    for source in record.get("source_links", []):
        lines.append(f"- Source: {source}")
    lines.extend(["", "## Record", "", "```json"])
    lines.append(json.dumps(record, indent=2, sort_keys=True))
    lines.extend(["```", "", "## Required Edges", ""])
    for edge in summarize_edges(record):
        lines.append(f"- {edge}")
    lines.append("")
    return "\n".join(lines)


def summarize_record(record: dict) -> str:
    if record["type"] == "Claim":
        return str(record.get("claim", record["id"]))
    if record["type"] == "Decision":
        return str(record.get("decision", record["id"]))
    if record["type"] == "Task":
        return f"{record.get('title', record['id'])} ({record.get('status', 'unknown')})"
    if record["type"] == "Project":
        return f"{record.get('title', record['id'])} ({record.get('status', 'unknown')})"
    if record["type"] == "ExecutionTrace":
        return f"{record.get('run_type', record['id'])} ({record.get('status', 'unknown')})"
    return str(record.get("title") or record.get("name") or record["id"])


def summarize_edges(record: dict) -> list[str]:
    edges: list[str] = []
    for key in (
        "entity",
        "made_by",
        "owner",
        "project",
        "agent",
        "target",
        "from_agent",
        "to_agent",
        "next_hop",
        "context_refs",
        "input_refs",
        "output_refs",
        "blockers",
        "supersedes",
    ):
        if key in record:
            edges.append(f"{key}: {record[key]}")
    for source in record.get("source_links", []):
        edges.append(f"source: {source}")
    return edges


def yaml_scalar(value: object) -> str:
    if isinstance(value, list):
        return "[" + ", ".join(json.dumps(item) for item in value) + "]"
    return json.dumps(value)


def slug_filename(value: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in "-_." else "-" for ch in value)
    return safe.strip("-") or "record"


if __name__ == "__main__":
    raise SystemExit(main())
