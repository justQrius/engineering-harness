#!/usr/bin/env python3
"""Query the typed brain SQLite projection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
import sys
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser(description="Query typed brain SQLite projections")
    parser.add_argument("--db", type=Path, default=Path.home() / ".gbrain" / "typed" / "brain.db")
    parser.add_argument("--type", dest="node_type", help="Filter nodes by typed node type")
    parser.add_argument("--edge-type", help="Filter edges by edge type")
    parser.add_argument("--node-id", help="Show a node and its outgoing 1-hop edges")
    parser.add_argument("--depth", type=int, default=1, help="Traversal depth from --node-id")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = parser.parse_args()

    if args.depth < 1:
        parser.error("--depth must be >= 1")
    try:
        with sqlite3.connect(args.db) as conn:
            conn.row_factory = sqlite3.Row
            if args.node_id:
                result = query_traversal(conn, args.node_id, args.depth, args.edge_type)
            elif args.edge_type:
                result = {"edges": query_edges(conn, args.edge_type)}
            else:
                result = {"nodes": query_nodes(conn, args.node_type)}
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print_text(result)
        return 0
    except (OSError, sqlite3.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def query_nodes(conn: sqlite3.Connection, node_type: str | None = None) -> list[dict[str, Any]]:
    sql = "SELECT id, type, subtype, created_at FROM nodes"
    params: list[str] = []
    if node_type:
        sql += " WHERE type = ?"
        params.append(node_type)
    sql += " ORDER BY created_at, id"
    return rows(conn.execute(sql, params))


def query_edges(conn: sqlite3.Connection, edge_type: str | None = None) -> list[dict[str, Any]]:
    sql = "SELECT from_node, edge_type, to_node, recorded_at FROM edges"
    params: list[str] = []
    if edge_type:
        sql += " WHERE edge_type = ?"
        params.append(edge_type)
    sql += " ORDER BY from_node, edge_type, to_node"
    return rows(conn.execute(sql, params))


def query_traversal(
    conn: sqlite3.Connection,
    node_id: str,
    depth: int,
    edge_type: str | None = None,
) -> dict[str, Any]:
    start = conn.execute(
        "SELECT id, type, subtype, created_at FROM nodes WHERE id = ?",
        (node_id,),
    ).fetchone()
    edge_filter = "AND e.edge_type = ?" if edge_type else ""
    params: list[Any] = [node_id]
    if edge_type:
        params.append(edge_type)
    params.append(depth)
    sql = f"""
    WITH RECURSIVE walk(root, from_node, edge_type, to_node, recorded_at, depth, path) AS (
      SELECT e.from_node, e.from_node, e.edge_type, e.to_node, e.recorded_at, 1,
             e.from_node || '->' || e.to_node
      FROM edges e
      WHERE e.from_node = ? {edge_filter}
      UNION ALL
      SELECT walk.root, e.from_node, e.edge_type, e.to_node, e.recorded_at, walk.depth + 1,
             walk.path || '->' || e.to_node
      FROM walk
      JOIN edges e ON e.from_node = walk.to_node
      WHERE walk.depth < ? {edge_filter}
        AND instr(walk.path, e.to_node) = 0
    )
    SELECT from_node, edge_type, to_node, recorded_at, depth, path
    FROM walk
    ORDER BY depth, from_node, edge_type, to_node
    """
    if edge_type:
        params.append(edge_type)
    return {
        "node": dict(start) if start else None,
        "edges": rows(conn.execute(sql, params)),
    }


def rows(cursor: sqlite3.Cursor) -> list[dict[str, Any]]:
    return [dict(row) for row in cursor.fetchall()]


def print_text(result: dict[str, Any]) -> None:
    if "node" in result:
        node = result["node"]
        print(f"node: {node['id']} ({node['type']}/{node['subtype']})" if node else "node: <missing>")
    for node in result.get("nodes", []):
        subtype = f"/{node['subtype']}" if node["subtype"] else ""
        print(f"{node['id']}\t{node['type']}{subtype}\t{node['created_at']}")
    for edge in result.get("edges", []):
        depth = f"\tdepth={edge['depth']}" if "depth" in edge else ""
        print(f"{edge['from_node']} --{edge['edge_type']}--> {edge['to_node']}{depth}")


if __name__ == "__main__":
    raise SystemExit(main())
