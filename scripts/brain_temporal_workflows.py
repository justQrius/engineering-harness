#!/usr/bin/env python3
"""Temporal workflow definitions for the typed brain.

The module is import-safe in the engineering harness: tests can import the
dataclasses and workflow classes without a Temporal server or the temporalio
package. In deployment, install temporalio and register the activity callables
with a worker on the brain task queue.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable


try:
    from temporalio import activity, workflow

    TEMPORAL_AVAILABLE = True
except ImportError:  # pragma: no cover - normal in the local harness
    TEMPORAL_AVAILABLE = False

    class _NoopTemporalNamespace:
        def defn(self, obj: Callable[..., Any] | None = None, **_: Any) -> Any:
            if obj is None:
                return lambda wrapped: wrapped
            return obj

        def run(self, fn: Callable[..., Any]) -> Callable[..., Any]:
            return fn

        def now(self) -> datetime:
            return datetime.now(timezone.utc)

        async def execute_activity(self, *_: Any, **__: Any) -> Any:
            raise RuntimeError("temporalio is not installed; workflow execution requires a Temporal worker")

    activity = _NoopTemporalNamespace()
    workflow = _NoopTemporalNamespace()


ACTIVITY_TIMEOUT = timedelta(minutes=5)
LONG_ACTIVITY_TIMEOUT = timedelta(minutes=30)


@dataclass(frozen=True)
class TypedWrite:
    record: dict[str, Any]
    ledger: str | None = None
    pages_dir: str | None = None


@dataclass(frozen=True)
class ResearchWorkflowInput:
    topic: str
    requester: str
    trace_id: str
    source_links: list[str]
    max_hops: int = 3
    seed_refs: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class KbSyncWorkflowInput:
    trace_id: str
    repo: str
    source_links: list[str]
    projection_command: list[str] = field(default_factory=lambda: ["project"])


@dataclass(frozen=True)
class ContentPipelineWorkflowInput:
    topic: str
    requester: str
    trace_id: str
    source_links: list[str]
    audience: str = "general"
    publish_requires_approval: bool = True


@dataclass(frozen=True)
class AgentHandoffWorkflowInput:
    handoff_id: str
    trace_id: str
    from_agent: str
    to_agent: str
    summary: str
    context_refs: list[str]
    source_links: list[str]


# Backwards-compatible aliases for Phase 1 draft names.
ResearchTaskInput = ResearchWorkflowInput
KbSyncInput = KbSyncWorkflowInput
ContentPipelineInput = ContentPipelineWorkflowInput
AgentHandoffInput = AgentHandoffWorkflowInput


@activity.defn
async def write_typed_record(write: TypedWrite) -> dict[str, Any]:
    """Write one typed record through the host's validated writer.

    Production workers should provide an implementation that either imports
    brain_write helpers or shells out to scripts/brain_write.py. The definition
    lives here so workflows have a stable activity name.
    """

    raise NotImplementedError("register a host-specific typed brain writer activity")


@activity.defn
async def run_gbrain_command(args: list[str]) -> dict[str, Any]:
    raise NotImplementedError("register a host-specific gbrain command runner activity")


@activity.defn
async def collect_research(task: ResearchWorkflowInput) -> list[dict[str, Any]]:
    raise NotImplementedError("register a host-specific multi-hop research collector activity")


@activity.defn
async def draft_content(task: ContentPipelineWorkflowInput) -> dict[str, Any]:
    raise NotImplementedError("register a host-specific content drafter activity")


@activity.defn
async def request_review(payload: dict[str, Any]) -> dict[str, Any]:
    raise NotImplementedError("register a host-specific review request activity")


@activity.defn
async def await_approval(payload: dict[str, Any]) -> dict[str, Any]:
    raise NotImplementedError("register a host-specific approval gate activity")


@activity.defn
async def publish_content(payload: dict[str, Any]) -> dict[str, Any]:
    raise NotImplementedError("register a host-specific publisher activity")


@activity.defn
async def send_handoff(payload: AgentHandoffWorkflowInput) -> dict[str, Any]:
    raise NotImplementedError("register a host-specific handoff sender activity")


@activity.defn
async def verify_handoff_ack(payload: AgentHandoffWorkflowInput) -> dict[str, Any]:
    raise NotImplementedError("register a host-specific handoff acknowledgement activity")


@workflow.defn
class ResearchTaskWorkflow:
    """Durable multi-hop research run with typed Source/Claim/Entity outputs."""

    @workflow.run
    async def run(self, task: ResearchWorkflowInput) -> dict[str, Any]:
        started_at = workflow.now().isoformat()
        await _write_trace(
            trace_id=task.trace_id,
            agent=task.requester,
            run_type="research",
            status="running",
            started_at=started_at,
            source_links=task.source_links,
            input_refs=task.seed_refs,
        )
        try:
            records = await _activity(collect_research, task, timeout=LONG_ACTIVITY_TIMEOUT)
            typed_outputs: list[str] = []
            for record in records:
                await _activity(write_typed_record, TypedWrite(record))
                if isinstance(record.get("id"), str):
                    typed_outputs.append(record["id"])
            await _write_trace(
                trace_id=task.trace_id,
                agent=task.requester,
                run_type="research",
                status="completed",
                started_at=started_at,
                source_links=task.source_links,
                input_refs=task.seed_refs,
                output_refs=typed_outputs,
            )
            return {"trace_id": task.trace_id, "records_written": len(records), "output_refs": typed_outputs}
        except Exception:
            await _write_trace(
                trace_id=task.trace_id,
                agent=task.requester,
                run_type="research",
                status="failed",
                started_at=started_at,
                source_links=task.source_links,
                input_refs=task.seed_refs,
            )
            raise


@workflow.defn
class KbSyncWorkflow:
    """Durably project typed ledger pages, sync GBrain markdown, and embed."""

    @workflow.run
    async def run(self, task: KbSyncWorkflowInput) -> dict[str, Any]:
        started_at = workflow.now().isoformat()
        await _write_trace(task.trace_id, "agent/neo", "kb-sync", "running", started_at, task.source_links)
        try:
            await _activity(run_gbrain_command, task.projection_command)
            sync = await _activity(run_gbrain_command, ["sync", "--repo", task.repo], timeout=LONG_ACTIVITY_TIMEOUT)
            embed = await _activity(run_gbrain_command, ["embed", "--stale"], timeout=LONG_ACTIVITY_TIMEOUT)
            extract = await _activity(run_gbrain_command, ["extract", "all"], timeout=LONG_ACTIVITY_TIMEOUT)
            await _write_trace(
                task.trace_id,
                "agent/neo",
                "kb-sync",
                "completed",
                started_at,
                task.source_links,
                output_refs=[task.repo],
            )
            return {"trace_id": task.trace_id, "repo": task.repo, "sync": sync, "embed": embed, "extract": extract}
        except Exception:
            await _write_trace(task.trace_id, "agent/neo", "kb-sync", "failed", started_at, task.source_links)
            raise


@workflow.defn
class ContentPipelineWorkflow:
    """Draft -> review -> approval-gated publish with typed provenance."""

    @workflow.run
    async def run(self, task: ContentPipelineWorkflowInput) -> dict[str, Any]:
        started_at = workflow.now().isoformat()
        await _write_trace(task.trace_id, task.requester, "content-pipeline", "running", started_at, task.source_links)
        research_records = await _activity(
            collect_research,
            ResearchWorkflowInput(
                topic=task.topic,
                requester=task.requester,
                trace_id=f"{task.trace_id}/research",
                source_links=task.source_links,
            ),
            timeout=LONG_ACTIVITY_TIMEOUT,
        )
        for record in research_records:
            await _activity(write_typed_record, TypedWrite(record))
        draft = await _activity(draft_content, task, timeout=LONG_ACTIVITY_TIMEOUT)
        review = await _activity(request_review, {"draft": draft, "topic": task.topic, "trace_id": task.trace_id})
        approval = {"approved": not task.publish_requires_approval, "approval_required": task.publish_requires_approval}
        publish_result: dict[str, Any] | None = None
        if task.publish_requires_approval:
            approval = await _activity(await_approval, {"review": review, "trace_id": task.trace_id})
        if approval.get("approved") is True:
            publish_result = await _activity(publish_content, {"draft": draft, "approval": approval, "trace_id": task.trace_id})
        await _write_trace(
            task.trace_id,
            task.requester,
            "content-pipeline",
            "completed",
            started_at,
            task.source_links,
            output_refs=_ids_from_records(research_records),
        )
        return {
            "trace_id": task.trace_id,
            "research_records": len(research_records),
            "draft": draft,
            "review": review,
            "approval": approval,
            "publish": publish_result,
        }


@workflow.defn
class AgentHandoffWorkflow:
    """Typed context transfer between Morpheus, Claude, Codex, and Neo."""

    @workflow.run
    async def run(self, task: AgentHandoffWorkflowInput) -> dict[str, Any]:
        started_at = workflow.now().isoformat()
        await _write_trace(
            task.trace_id,
            task.from_agent,
            "agent-handoff",
            "running",
            started_at,
            task.source_links,
            input_refs=task.context_refs,
        )
        await _activity(
            write_typed_record,
            TypedWrite(
                {
                    "type": "ContextHandoff",
                    "id": task.handoff_id,
                    "from_agent": task.from_agent,
                    "to_agent": task.to_agent,
                    "summary": task.summary,
                    "context_refs": task.context_refs,
                    "transferred_at": workflow.now().isoformat(),
                    "created_at": workflow.now().isoformat(),
                    "source_links": task.source_links,
                }
            ),
        )
        sent = await _activity(send_handoff, task)
        ack = await _activity(verify_handoff_ack, task)
        await _write_trace(
            task.trace_id,
            task.from_agent,
            "agent-handoff",
            "completed",
            started_at,
            task.source_links,
            input_refs=task.context_refs,
            output_refs=[task.handoff_id],
        )
        return {"handoff_id": task.handoff_id, "trace_id": task.trace_id, "sent": sent, "ack": ack}


async def _activity(fn: Callable[..., Any], arg: Any, timeout: timedelta = ACTIVITY_TIMEOUT) -> Any:
    return await workflow.execute_activity(fn, arg, start_to_close_timeout=timeout)


async def _write_trace(
    trace_id: str,
    agent: str,
    run_type: str,
    status: str,
    started_at: str,
    source_links: list[str],
    input_refs: list[str] | None = None,
    output_refs: list[str] | None = None,
) -> None:
    record: dict[str, Any] = {
        "type": "ExecutionTrace",
        "id": trace_id,
        "agent": agent,
        "run_type": run_type,
        "status": status,
        "started_at": started_at,
        "created_at": workflow.now().isoformat(),
        "source_links": source_links,
    }
    if input_refs:
        record["input_refs"] = input_refs
    if output_refs:
        record["output_refs"] = output_refs
    if status in {"completed", "failed", "cancelled"}:
        record["ended_at"] = workflow.now().isoformat()
    await _activity(write_typed_record, TypedWrite(record))


def _ids_from_records(records: list[dict[str, Any]]) -> list[str]:
    return [record["id"] for record in records if isinstance(record.get("id"), str)]
