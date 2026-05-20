#!/usr/bin/env python3
"""Typed brain schema and validation helpers.

This layer validates records before they are written into the append-only brain
event ledger or emitted as GBrain-syncable markdown.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Any


SCHEMA_VERSION = "2026-05-20.v1"

SLUG_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.:/-]*$")
NODE_TYPES = {
    "Source",
    "Entity",
    "Claim",
    "Decision",
    "Task",
    "Project",
    "ExecutionTrace",
    "Agent",
    "Capability",
    "RoutingRule",
    "ContextHandoff",
}

ENTITY_SUBTYPES = {
    "person",
    "company",
    "product",
    "concept",
    "project",
    "agent",
    "source",
    "system",
    "repository",
    "workflow",
    "architecture",
}
TASK_STATUSES = {"todo", "doing", "blocked", "review", "done", "cancelled"}
PROJECT_STATUSES = {"planned", "active", "blocked", "paused", "done", "archived"}
TRACE_STATUSES = {"queued", "running", "completed", "failed", "cancelled"}


@dataclass(frozen=True)
class TypeSpec:
    required: tuple[str, ...]
    enum_fields: dict[str, set[str]]
    ref_fields: tuple[str, ...]


TYPE_SPECS: dict[str, TypeSpec] = {
    "Source": TypeSpec(
        required=("id", "title", "source_type", "created_at", "source_links"),
        enum_fields={},
        ref_fields=(),
    ),
    "Entity": TypeSpec(
        required=("id", "name", "subtype", "created_at", "source_links"),
        enum_fields={"subtype": ENTITY_SUBTYPES},
        ref_fields=(),
    ),
    "Claim": TypeSpec(
        required=("id", "entity", "claim", "confidence", "created_at", "source_links"),
        enum_fields={},
        ref_fields=("entity",),
    ),
    "Decision": TypeSpec(
        required=("id", "decision", "made_by", "decided_at", "rationale", "created_at", "source_links"),
        enum_fields={},
        ref_fields=("made_by", "supersedes", "superseded_by"),
    ),
    "Task": TypeSpec(
        required=("id", "title", "owner", "status", "project", "created_at", "source_links"),
        enum_fields={"status": TASK_STATUSES},
        ref_fields=("owner", "project", "blockers"),
    ),
    "Project": TypeSpec(
        required=("id", "title", "owner", "status", "created_at", "source_links"),
        enum_fields={"status": PROJECT_STATUSES},
        ref_fields=("owner", "next_hop"),
    ),
    "ExecutionTrace": TypeSpec(
        required=("id", "agent", "run_type", "status", "started_at", "created_at", "source_links"),
        enum_fields={"status": TRACE_STATUSES},
        ref_fields=("agent", "input_refs", "output_refs"),
    ),
    "Agent": TypeSpec(
        required=("id", "name", "runtime", "owner", "created_at", "source_links"),
        enum_fields={},
        ref_fields=("owner",),
    ),
    "Capability": TypeSpec(
        required=("id", "agent", "name", "input_modes", "output_modes", "created_at", "source_links"),
        enum_fields={},
        ref_fields=("agent",),
    ),
    "RoutingRule": TypeSpec(
        required=("id", "trigger", "target", "action", "created_at", "source_links"),
        enum_fields={},
        ref_fields=("target",),
    ),
    "ContextHandoff": TypeSpec(
        required=(
            "id",
            "from_agent",
            "to_agent",
            "summary",
            "context_refs",
            "transferred_at",
            "created_at",
            "source_links",
        ),
        enum_fields={},
        ref_fields=("from_agent", "to_agent", "context_refs"),
    ),
}


class ValidationError(ValueError):
    """Raised when a typed brain record is invalid."""


def validate_record(record: dict[str, Any], known_ids: set[str] | None = None) -> None:
    """Validate a typed brain record.

    known_ids is optional. When provided, typed references must resolve to a
    known record id, while external source_links may be URLs or file refs.
    """

    errors: list[str] = []
    node_type = record.get("type")
    if node_type not in NODE_TYPES:
        errors.append(f"type must be one of {sorted(NODE_TYPES)}")
    spec = TYPE_SPECS.get(str(node_type))
    if spec is None:
        raise ValidationError("; ".join(errors))

    for field in spec.required:
        if is_missing(record.get(field)):
            errors.append(f"missing required field: {field}")

    record_id = record.get("id")
    if not isinstance(record_id, str) or not SLUG_RE.match(record_id):
        errors.append("id must be a slug-like string")

    for field in ("created_at", "decided_at", "started_at", "ended_at", "transferred_at"):
        if field in record and not is_iso_datetime_or_date(record[field]):
            errors.append(f"{field} must be ISO 8601 date or datetime")

    source_links = record.get("source_links")
    if not isinstance(source_links, list) or not source_links:
        errors.append("source_links must be a non-empty list")
    elif any(not isinstance(link, str) or not link.strip() for link in source_links):
        errors.append("source_links entries must be non-empty strings")

    confidence = record.get("confidence")
    if confidence is not None and not is_number_between(confidence, 0, 1):
        errors.append("confidence must be a number between 0 and 1")

    for field, allowed in spec.enum_fields.items():
        value = record.get(field)
        if value is not None and value not in allowed:
            errors.append(f"{field} must be one of {sorted(allowed)}")

    for field in ("input_modes", "output_modes", "context_refs"):
        if field in record and not is_non_empty_string_list(record[field]):
            errors.append(f"{field} must be a non-empty list of strings")

    for field in spec.ref_fields:
        if field not in record or known_ids is None:
            continue
        refs = listify(record[field])
        missing = [ref for ref in refs if ref not in known_ids and ref != record_id]
        if missing:
            errors.append(f"{field} references unknown ids: {', '.join(missing)}")

    if errors:
        raise ValidationError("; ".join(errors))


def known_ids_from_jsonl(lines: list[str]) -> set[str]:
    import json

    ids: set[str] = set()
    for line in lines:
        if not line.strip():
            continue
        data = json.loads(line)
        if isinstance(data.get("record"), dict) and isinstance(data["record"].get("id"), str):
            ids.add(data["record"]["id"])
    return ids


def is_missing(value: Any) -> bool:
    return value is None or value == "" or value == []


def is_number_between(value: Any, minimum: float, maximum: float) -> bool:
    return isinstance(value, (int, float)) and minimum <= float(value) <= maximum


def is_non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item for item in value)


def is_iso_datetime_or_date(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    normalized = value.replace("Z", "+00:00")
    try:
        datetime.fromisoformat(normalized)
        return True
    except ValueError:
        return False


def listify(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    if isinstance(value, str):
        return [value]
    return []
