#!/usr/bin/env python3

from pathlib import Path
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "brain_write.py"
PROJECTOR = ROOT / "scripts" / "brain_projections.py"
QUERY = ROOT / "scripts" / "brain_query.py"
EXAMPLES = ROOT / "examples" / "brain"
sys.path.insert(0, str(ROOT / "scripts"))
SEED_EXAMPLES = (
    "source_session.json",
    "entity_gbrain.json",
    "entity_brain_architecture_project.json",
    "entity_shaktisinh.json",
    "agent_codex.json",
    "decision_typed_schema_before_graph_db.json",
    "project_brain_implementation.json",
    "task_phase_1_typed_spine.json",
    "task_phase_2_temporal_workflows.json",
    "task_phase_3_state_machines.json",
    "task_phase_4_query_accelerator.json",
)


class BrainSchemaTests(unittest.TestCase):
    def run_cmd(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_valid_source_passes_validation(self) -> None:
        result = self.run_cmd("validate", str(EXAMPLES / "source_session.json"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("valid", result.stdout)

    def test_invalid_claim_is_rejected(self) -> None:
        result = self.run_cmd("validate", str(EXAMPLES / "invalid_claim_missing_entity.json"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing required field: entity", result.stderr)

    def test_write_appends_ledger_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ledger = tmp_path / "events.jsonl"
            pages = tmp_path / "pages"
            for name in ("source_session.json", "entity_gbrain.json", "claim_gbrain_existing_schema.json"):
                result = self.run_cmd("write", str(EXAMPLES / name), "--ledger", str(ledger), "--pages-dir", str(pages))
                self.assertEqual(result.returncode, 0, result.stderr)

            lines = ledger.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 3)
            records = [json.loads(line)["record"] for line in lines]
            self.assertEqual(records[-1]["type"], "Claim")
            self.assertEqual(len(list(pages.glob("*.md"))), 3)

    def test_seed_examples_project_to_markdown_and_sqlite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ledger = tmp_path / "events.jsonl"
            pages = tmp_path / "pages"
            projections = tmp_path / "projections"
            sqlite = tmp_path / "projection.sqlite"
            for name in SEED_EXAMPLES:
                result = self.run_cmd("write", str(EXAMPLES / name), "--ledger", str(ledger), "--pages-dir", str(pages))
                self.assertEqual(result.returncode, 0, f"{name}: {result.stderr}")

            result = subprocess.run(
                [
                    sys.executable,
                    str(PROJECTOR),
                    "--ledger",
                    str(ledger),
                    "--projections-dir",
                    str(projections),
                    "--sqlite",
                    str(sqlite),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((projections / "summary.md").exists())
            self.assertTrue((projections / "relationships.md").exists())
            self.assertTrue(sqlite.exists())
            with sqlite3.connect(sqlite) as conn:
                node_count = conn.execute("SELECT count(*) FROM nodes").fetchone()[0]
                edge_count = conn.execute("SELECT count(*) FROM edges").fetchone()[0]
                self.assertEqual(node_count, len(SEED_EXAMPLES))
                self.assertGreater(edge_count, 0)
                indexes = {row[1] for row in conn.execute("PRAGMA index_list(nodes)").fetchall()}
                self.assertIn("idx_nodes_type", indexes)
                self.assertIn("idx_nodes_subtype", indexes)

            query = subprocess.run(
                [
                    sys.executable,
                    str(QUERY),
                    "--db",
                    str(sqlite),
                    "--node-id",
                    "task/brain-phase-4-query-accelerator",
                    "--depth",
                    "2",
                    "--json",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(query.returncode, 0, query.stderr)
            data = json.loads(query.stdout)
            self.assertEqual(data["node"]["id"], "task/brain-phase-4-query-accelerator")
            self.assertTrue(any(edge["to_node"] == "project/brain-implementation" for edge in data["edges"]))

    def test_state_machines_enforce_roles_guards_and_timestamps(self) -> None:
        from brain_state_machines import ApprovalStateMachine, StateMachineError, TaskStateMachine

        approval = ApprovalStateMachine()
        self.assertFalse(approval.can_transition("approved", "owner", {"review_ref": "review/1"}))
        approval.transition("review", role="author", actor="agent/codex", context={"artifact_ref": "draft/1"})
        with self.assertRaises(StateMachineError):
            approval.transition("published", role="author", actor="agent/codex", context={"approval_ref": "approval/1"})
        approval.transition("approved", role="reviewer", actor="entity/shaktisinh", context={"review_ref": "review/1"})
        event = approval.transition(
            "published",
            role="publisher",
            actor="entity/shaktisinh",
            context={"approval_ref": "approval/1", "publish_target": "linkedin"},
        )
        self.assertEqual(event.from_state, "approved")
        self.assertEqual(approval.state, "published")
        self.assertEqual(len(approval.history), 3)

        task = TaskStateMachine()
        task.transition("in_progress", role="agent", actor="agent/codex")
        self.assertFalse(task.can_transition("complete", "agent", {}))
        task.transition("complete", role="agent", actor="agent/codex", context={"evidence_ref": "test/run"})
        self.assertEqual(task.state, "complete")

    def test_temporal_workflows_are_import_safe_without_temporal_server(self) -> None:
        import brain_temporal_workflows as temporal_workflows

        task = temporal_workflows.ResearchWorkflowInput(
            topic="typed brain",
            requester="agent/codex",
            trace_id="trace/test-research",
            source_links=["source/test"],
        )
        self.assertEqual(task.max_hops, 3)
        self.assertTrue(hasattr(temporal_workflows, "ResearchTaskWorkflow"))
        self.assertTrue(hasattr(temporal_workflows, "KbSyncWorkflow"))
        self.assertTrue(hasattr(temporal_workflows, "ContentPipelineWorkflow"))
        self.assertTrue(hasattr(temporal_workflows, "AgentHandoffWorkflow"))


if __name__ == "__main__":
    unittest.main()
