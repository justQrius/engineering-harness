#!/usr/bin/env python3
"""Project the typed brain JSONL ledger into markdown and SQLite views."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
import sys
from typing import Any


EDGE_FIELDS = (
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
    "superseded_by",
)


@dataclass(frozen=True)
class Edge:
    from_node: str
    edge_type: str
    to_node: str
    recorded_at: str


def main() -> int:
    parser = argparse.ArgumentParser(description="Project typed brain ledger")
    parser.add_argument("--ledger", type=Path, default=Path.home() / ".gbrain" / "typed" / "events.jsonl")
    parser.add_argument(
        "--projections-dir",
        type=Path,
        default=Path.home() / "KnowledgeBase" / "TypedBrain" / "projections",
    )
    parser.add_argument(
        "--sqlite",
        type=Path,
        default=Path.home() / ".gbrain" / "typed" / "brain.db",
    )
    args = parser.parse_args()

    try:
        events = load_events(args.ledger)
        records = latest_records(events)
        edges = collect_edges(events)
        args.projections_dir.mkdir(parents=True, exist_ok=True)
        write_summary(args.projections_dir / "summary.md", events, records)
        write_entities(args.projections_dir / "entities.md", records)
        write_relationships(args.projections_dir / "relationships.md", edges)
        write_tasks(args.projections_dir / "tasks.md", records)
        write_sqlite(args.sqlite, events, records, edges)
        print(f"projected events={len(events)} records={len(records)} edges={len(edges)}")
        print(f"wrote projections={args.projections_dir}")
        print(f"wrote sqlite={args.sqlite}")
        return 0
    except (OSError, json.JSONDecodeError, sqlite3.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def load_events(ledger: Path) -> list[dict[str, Any]]:
    if not ledger.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in ledger.read_text(encoding="utf-8").splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def latest_records(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for event in events:
        record = event.get("record")
        if isinstance(record, dict) and isinstance(record.get("id"), str):
            records[record["id"]] = record
    return records


def collect_edges(events_or_records: list[dict[str, Any]] | dict[str, dict[str, Any]]) -> list[Edge]:
    edges: list[Edge] = []
    if isinstance(events_or_records, dict):
        items = [("", record) for record in events_or_records.values()]
    else:
        items = [(str(event.get("recorded_at", "")), event.get("record")) for event in events_or_records]
    seen: set[tuple[str, str, str, str]] = set()
    for recorded_at, record in items:
        if not isinstance(record, dict) or not isinstance(record.get("id"), str):
            continue
        record_id = record["id"]
        for field in EDGE_FIELDS:
            if field not in record:
                continue
            for ref in listify(record[field]):
                edge = Edge(record_id, field, ref, recorded_at)
                key = (edge.from_node, edge.edge_type, edge.to_node, edge.recorded_at)
                if key not in seen:
                    seen.add(key)
                    edges.append(edge)
        for source in listify(record.get("source_links")):
            edge = Edge(record_id, "source", source, recorded_at)
            key = (edge.from_node, edge.edge_type, edge.to_node, edge.recorded_at)
            if key not in seen:
                seen.add(key)
                edges.append(edge)
    return edges


def write_summary(path: Path, events: list[dict[str, Any]], records: dict[str, dict[str, Any]]) -> None:
    counts = Counter(record["type"] for record in records.values())
    lines = [
        "---",
        'type: "typed_projection"',
        'projection: "summary"',
        "---",
        "",
        "# Typed Brain Summary",
        "",
        f"- Events: {len(events)}",
        f"- Current records: {len(records)}",
        "",
        "## Counts By Type",
        "",
    ]
    for node_type, count in sorted(counts.items()):
        lines.append(f"- {node_type}: {count}")
    lines.extend(["", "## Latest Records", ""])
    for event in events[-20:]:
        record = event["record"]
        lines.append(f"- {event['recorded_at']} - {record['type']} - `{record['id']}` - {title_for(record)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_entities(path: Path, records: dict[str, dict[str, Any]]) -> None:
    claims_by_entity: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records.values():
        if record["type"] == "Claim":
            claims_by_entity[str(record.get("entity", ""))].append(record)

    lines = [
        "---",
        'type: "typed_projection"',
        'projection: "entities"',
        "---",
        "",
        "# Typed Brain Entities",
        "",
    ]
    for record in sorted(records.values(), key=lambda item: item["id"]):
        if record["type"] != "Entity":
            continue
        lines.append(f"## {record.get('name', record['id'])}")
        lines.append("")
        lines.append(f"- ID: `{record['id']}`")
        lines.append(f"- Subtype: {record.get('subtype', '')}")
        for claim in claims_by_entity.get(record["id"], []):
            lines.append(f"- Claim: {claim.get('claim', claim['id'])}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_relationships(path: Path, edges: list[Edge]) -> None:
    lines = [
        "---",
        'type: "typed_projection"',
        'projection: "relationships"',
        "---",
        "",
        "# Typed Brain Relationships",
        "",
    ]
    for edge in sorted(edges, key=lambda item: (item.from_node, item.edge_type, item.to_node)):
        lines.append(f"- `{edge.from_node}` --{edge.edge_type}--> `{edge.to_node}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_tasks(path: Path, records: dict[str, dict[str, Any]]) -> None:
    projects = {record["id"]: record for record in records.values() if record["type"] == "Project"}
    tasks_by_project: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records.values():
        if record["type"] == "Task":
            tasks_by_project[str(record.get("project", ""))].append(record)

    lines = [
        "---",
        'type: "typed_projection"',
        'projection: "tasks"',
        "---",
        "",
        "# Typed Brain Tasks",
        "",
    ]
    for project_id, tasks in sorted(tasks_by_project.items()):
        project_title = projects.get(project_id, {}).get("title", project_id)
        lines.append(f"## {project_title}")
        lines.append("")
        for task in sorted(tasks, key=lambda item: (item.get("status", ""), item["id"])):
            lines.append(f"- [{task.get('status', '')}] `{task['id']}` - {task.get('title', '')}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_sqlite(path: Path, events: list[dict[str, Any]], records: dict[str, dict[str, Any]], edges: list[Edge]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute("DROP TABLE IF EXISTS events")
        conn.execute("DROP TABLE IF EXISTS records")
        conn.execute("DROP TABLE IF EXISTS nodes")
        conn.execute("DROP TABLE IF EXISTS edges")
        conn.execute(
            """
            CREATE TABLE events (
              event_id TEXT PRIMARY KEY,
              schema_version TEXT NOT NULL,
              recorded_at TEXT NOT NULL,
              record_id TEXT NOT NULL,
              record_type TEXT NOT NULL,
              payload_json TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE records (
              id TEXT PRIMARY KEY,
              type TEXT NOT NULL,
              title TEXT NOT NULL,
              created_at TEXT NOT NULL,
              payload_json TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE nodes (
              id TEXT PRIMARY KEY,
              type TEXT NOT NULL,
              subtype TEXT NOT NULL,
              created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE edges (
              from_node TEXT NOT NULL,
              edge_type TEXT NOT NULL,
              to_node TEXT NOT NULL,
              recorded_at TEXT NOT NULL
            )
            """
        )
        conn.executemany(
            "INSERT INTO events VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    event["event_id"],
                    event["schema_version"],
                    event["recorded_at"],
                    event["record"]["id"],
                    event["record"]["type"],
                    json.dumps(event, sort_keys=True),
                )
                for event in events
            ],
        )
        conn.executemany(
            "INSERT INTO records VALUES (?, ?, ?, ?, ?)",
            [
                (
                    record["id"],
                    record["type"],
                    title_for(record),
                    record["created_at"],
                    json.dumps(record, sort_keys=True),
                )
                for record in records.values()
            ],
        )
        conn.executemany(
            "INSERT INTO nodes VALUES (?, ?, ?, ?)",
            [
                (
                    record["id"],
                    record["type"],
                    subtype_for(record),
                    record["created_at"],
                )
                for record in records.values()
            ],
        )
        conn.executemany(
            "INSERT INTO edges VALUES (?, ?, ?, ?)",
            [(edge.from_node, edge.edge_type, edge.to_node, edge.recorded_at) for edge in edges],
        )
        conn.execute("CREATE INDEX idx_records_type ON records(type)")
        conn.execute("CREATE INDEX idx_nodes_type ON nodes(type)")
        conn.execute("CREATE INDEX idx_nodes_subtype ON nodes(subtype)")
        conn.execute("CREATE INDEX idx_nodes_created_at ON nodes(created_at)")
        conn.execute("CREATE INDEX idx_edges_from_node ON edges(from_node)")
        conn.execute("CREATE INDEX idx_edges_to_node ON edges(to_node)")
        conn.execute("CREATE INDEX idx_edges_edge_type ON edges(edge_type)")
        conn.execute("CREATE INDEX idx_edges_recorded_at ON edges(recorded_at)")


def title_for(record: dict[str, Any]) -> str:
    return str(record.get("title") or record.get("name") or record.get("decision") or record.get("claim") or record["id"])


def subtype_for(record: dict[str, Any]) -> str:
    if isinstance(record.get("subtype"), str):
        return record["subtype"]
    if isinstance(record.get("status"), str):
        return record["status"]
    if isinstance(record.get("source_type"), str):
        return record["source_type"]
    if isinstance(record.get("run_type"), str):
        return record["run_type"]
    return ""


def listify(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    if isinstance(value, str):
        return [value]
    return []


if __name__ == "__main__":
    raise SystemExit(main())
