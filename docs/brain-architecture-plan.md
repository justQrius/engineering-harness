# Brain Architecture Plan

Status: final for Phase 1 implementation
Date: 2026-05-20

## Current State Audit

### KnowledgeBase and GBrain

- Canonical markdown source: `/home/justqrius/KnowledgeBase`.
- Existing KnowledgeBase schema is convention-based markdown. The durable pattern is compiled truth above the fold and append-only timeline below it, with source-backed cross-links.
- Existing GBrain database schema, observed from `/home/justqrius/gbrain/src/schema.sql`, has generic storage tables: `pages`, `content_chunks`, `links`, `tags`, `raw_data`, `timeline_entries`, `page_versions`, `ingest_log`, `config`, `access_tokens`, `mcp_request_log`, `files`, and Minions job tables.
- Existing GBrain page types, observed from `/home/justqrius/gbrain/src/core/types.ts`, are broad content categories: `person`, `company`, `deal`, `yc`, `civic`, `project`, `concept`, `source`, `media`, `writing`, `analysis`, `guide`, `hardware`, `architecture`.
- Existing graph layer is page-link based. `links` stores edges between pages with `link_type`, `context`, and provenance fields. It does not require typed edges like Claim -> Entity or Decision -> Agent.
- GBrain docs recommend a database-plus-markdown architecture with an entity registry, event ledger, fact store, and relationship graph. The Phase 1 spine implements the event ledger and relationship projection first, without replacing GBrain.
- GBrain operations include search/query, sync/embed/extract, graph-query traversal, autopilot, and Minions jobs.
- Memory says GBrain should use Postgres Docker for reliability on this machine; PGLite has recurring Bun/runtime instability.
- GBrain autopilot service file exists at `~/.config/systemd/user/gbrain-autopilot.service` and runs `gbrain autopilot --repo '/home/justqrius/KnowledgeBase'`.

### Hermes Agent Setup

- Hermes memory points Codex and Claude work at `/home/justqrius/.hermes/profiles/hermes-lab/workspace/engineering-harness`.
- Hermes memory says GBrain is the canonical source and should be written directly, not treated as a throwaway local repo file.
- Hermes currently keeps its own operational memories under `/home/justqrius/.hermes/profiles/hermes-lab/memories/`; those are runtime memory, not the canonical world-knowledge brain.
- The current Hermes profile has MCP-capable runtime files, but this plan should not depend on Hermes-only APIs. The typed brain writer stays as a plain CLI/importable Python layer usable by OpenClaw, Hermes, Codex, Claude Code, cron, and Temporal workers.

### Workflow Audit

- Current recurring GBrain work is service/cron oriented, not durable workflow oriented. Failures are detected by logs and reruns, not by durable workflow state.
- Content pipeline is documented as planned, but not implemented as a durable research -> draft -> review -> publish workflow.
- Agent handoff exists as markdown and Discord/channel convention, not as typed handoff records with durable execution state.

## Final Answers to Open Questions

### 1. Node type names and required fields

The node type set is right for a working agent if it stays operationally small:

- `Source`
- `Entity`
- `Claim`
- `Decision`
- `Task`
- `Project`
- `ExecutionTrace`
- `Agent`
- `Capability`
- `RoutingRule`
- `ContextHandoff`

Reasoning: these cover the agent's real work surfaces: what exists (`Entity`), what is asserted (`Claim`), what was chosen (`Decision`), what is being done (`Task`/`Project`), what ran (`ExecutionTrace`), who or what ran it (`Agent`/`Capability`), how work routes (`RoutingRule`), and what context crossed agent boundaries (`ContextHandoff`). This maps to the current OpenClaw/Hermes/GBrain operating model without forcing every domain page into a premature graph database schema.

Required fields should stay minimal and enforce only invariants. Every record needs `type`, `id`, `created_at`, and non-empty `source_links`. Type-specific fields should describe the node's identity and most important edge. Do not require lifecycle fields that are often unknown at creation time. In particular, `Project.next_hop` is optional; a project can exist before the next handoff target is known.

### 2. Source node

`Source` remains an explicit support node.

Reasoning: sources are not merely entities and not merely claim attributes. A single source can support many claims, decisions, tasks, and traces. Keeping it explicit preserves provenance, deduplication, replay, and auditability. `source_links` may point either to typed `Source` ids or to external refs such as URLs, file paths, command outputs, Discord message ids, or session refs. A `Source` record itself still has `source_links`; for Source nodes those are the raw external refs that justify the source artifact.

### 3. Append-only event page layout

The event page format is:

1. YAML frontmatter for GBrain indexing and filtering.
2. A human title: `# <Type>: <title/name/id>`.
3. `## Summary` with the compact thing a human or LLM should scan.
4. `## Timeline Event` with record time, created time, type, and source refs.
5. `## Record` containing the canonical JSON payload.
6. `## Required Edges` listing typed references and sources in plain markdown.

Reasoning: the JSONL ledger remains the source of truth, but GBrain's search and link extraction need markdown that is readable, source-rich, and consistently structured. Frontmatter alone is too easy to miss in semantic search; JSON alone is too dense for human review. The page should be append-only and never hand-edited except by regenerating from the ledger.

### 4. Projections

Phase 1 emits markdown projections and a SQLite projection. Postgres tables are deferred.

Reasoning: markdown projections are the human and GBrain ingestion surface. SQLite gives fast local graph/task/entity queries with no service dependency and no coupling to GBrain's internal Postgres schema. Postgres projections become useful later when the typed ledger stabilizes and GBrain ingestion can consume them intentionally. Phase 1 must not write directly into GBrain core tables.

Required Phase 1 projections:

- `summary.md`: counts by type and latest records.
- `entities.md`: entity listing with linked claims.
- `relationships.md`: simple typed edge listing.
- `tasks.md`: tasks grouped by project and status.
- `brain_projection.sqlite`: tables for `events`, `records`, and `edges`.

### 5. Temporal workflow boundaries and approval gates

The four proposed workflows are the right Phase 2 boundary:

- `ResearchTaskWorkflow`: durable research run with Source/Claim/Entity outputs.
- `KbSyncWorkflow`: durable GBrain sync/embed/extract maintenance.
- `ContentPipelineWorkflow`: research -> draft -> review -> approval request. Publishing remains approval-gated.
- `AgentHandoffWorkflow`: ContextHandoff creation, receiver acknowledgement, and traceable context transfer.

Reasoning: these are the four processes that need retry, timeout, checkpoint, and state visibility. Simple typed writes do not need Temporal. They need validation, append-only persistence, and projections.

Approval gates:

- Publishing content requires explicit approval.
- Sending messages as Shaktisinh requires explicit approval.
- Destructive operations require explicit approval.
- Modifying existing KB wiki pages requires explicit approval; Phase 1 only creates append-only typed event/projection pages.
- Strategic pivots, spending money, and Discord changes affecting others require explicit approval.

## Architecture

### Principle

Do not replace GBrain in Phase 1. Add a typed ingestion spine in front of it:

1. Agents submit typed node records.
2. The spine validates required fields, timestamps, source links, and typed references.
3. Valid writes append to a JSONL event ledger and emit GBrain-syncable markdown event pages.
4. Projection jobs read the JSONL ledger and emit markdown plus SQLite views.
5. GBrain indexes the markdown event and projection pages.
6. Later, Postgres or graph database projections can materialize the same ledger without changing the source of truth.

### Storage Layout

Default runtime paths:

- Event ledger: `~/.gbrain/typed/events.jsonl`
- Markdown events: `D:/Projects/KnowledgeBase/TypedBrain/events/*.md`
- Markdown projections: `D:/Projects/KnowledgeBase/TypedBrain/projections/*.md`
- SQLite projection: `~/.gbrain/typed/brain_projection.sqlite`

The event ledger is the typed source of truth. Markdown event pages and projections are GBrain ingestion surfaces. SQLite is a local query accelerator.

### Shared Record Fields

Every typed record requires:

- `type`: node type
- `id`: stable slug-like identifier
- `created_at`: ISO 8601 timestamp
- `source_links`: non-empty list of source references

The writer adds:

- `schema_version`
- `event_id`
- `recorded_at`

### Node Types

#### Source

Required fields: `id`, `title`, `source_type`, `created_at`, `source_links`

Purpose: source artifact such as URL, transcript, file, Discord message, command output, or human assertion.

#### Entity

Required fields: `id`, `name`, `subtype`, `created_at`, `source_links`

Allowed subtypes: `person`, `company`, `product`, `concept`, `project`, `agent`, `source`, `system`, `repository`, `workflow`, `architecture`

#### Claim

Required fields: `id`, `entity`, `claim`, `confidence`, `created_at`, `source_links`

Edges:

- `entity` -> Entity
- `source_links` -> Source or external source reference

#### Decision

Required fields: `id`, `decision`, `made_by`, `decided_at`, `rationale`, `created_at`, `source_links`

Optional: `supersedes`, `superseded_by`

Edges:

- `made_by` -> Agent or Entity
- `supersedes` -> Decision

#### Task

Required fields: `id`, `title`, `owner`, `status`, `project`, `created_at`, `source_links`

Optional: `blockers`

Allowed statuses: `todo`, `doing`, `blocked`, `review`, `done`, `cancelled`

Edges:

- `owner` -> Agent or Entity
- `project` -> Project
- `blockers` -> Task

#### Project

Required fields: `id`, `title`, `owner`, `status`, `created_at`, `source_links`

Optional: `next_hop`

Allowed statuses: `planned`, `active`, `blocked`, `paused`, `done`, `archived`

Edges:

- `owner` -> Agent or Entity
- `next_hop` -> Agent, Capability, RoutingRule, or Task

#### ExecutionTrace

Required fields: `id`, `agent`, `run_type`, `status`, `started_at`, `created_at`, `source_links`

Optional: `ended_at`, `workflow_id`, `input_refs`, `output_refs`

Edges:

- `agent` -> Agent
- `input_refs` -> any typed node
- `output_refs` -> any typed node

#### Agent

Required fields: `id`, `name`, `runtime`, `owner`, `created_at`, `source_links`

Edges:

- `owner` -> Entity

#### Capability

Required fields: `id`, `agent`, `name`, `input_modes`, `output_modes`, `created_at`, `source_links`

Edges:

- `agent` -> Agent

#### RoutingRule

Required fields: `id`, `trigger`, `target`, `action`, `created_at`, `source_links`

Optional: `priority`, `conditions`

Edges:

- `target` -> Agent or Capability

#### ContextHandoff

Required fields: `id`, `from_agent`, `to_agent`, `summary`, `context_refs`, `transferred_at`, `created_at`, `source_links`

Edges:

- `from_agent` -> Agent
- `to_agent` -> Agent
- `context_refs` -> any typed node

## Phase 1 Implementation

Phase 1 is implemented in this repo by:

- `scripts/brain_schema.py`
- `scripts/brain_write.py`
- `scripts/brain_projections.py`
- `examples/brain/`
- `scripts/test_brain_schema.py`

Implementation order:

1. Validate typed records with required fields, enum checks, ISO timestamps, source links, confidence ranges, and known-id reference checks.
2. Append valid writes to `~/.gbrain/typed/events.jsonl`.
3. Emit one GBrain-syncable markdown event page per write.
4. Project the ledger to markdown summaries and SQLite graph tables.
5. Seed real typed records for GBrain, this architecture, the typed-schema decision, the implementation project, and the four implementation phase tasks.
6. Run tests and sync GBrain when the local backend is reachable.

## Phase 2 Temporal Workflows

Temporal owns durability for processes, not canonical knowledge. Workflows write typed records as milestones and state changes.

Workflow definitions:

- `ResearchTaskWorkflow`: create ExecutionTrace, run research, write Claim/Entity/Source outputs, mark trace done or failed.
- `KbSyncWorkflow`: run sync, embed stale chunks, extract graph/timeline, write ExecutionTrace.
- `ContentPipelineWorkflow`: research -> draft -> review -> approved publish request. Publish remains approval-gated.
- `AgentHandoffWorkflow`: create ContextHandoff, verify receiver acknowledgement, preserve transferred context refs.

Activity boundaries:

- `write_typed_record`
- `run_gbrain_command`
- `collect_research`
- `draft_content`
- `request_review`
- `await_approval`
- `send_handoff`
- `verify_handoff_ack`

Phase 2 is implemented as import-safe workflow definitions in `scripts/brain_temporal_workflows.py`. A verified deployment must show Temporal frontend reachable, worker registered on the brain task queue, one `KbSyncWorkflow` smoke run completed, and an `ExecutionTrace` written through `scripts/brain_write.py`.

## Phase 3 State Machines

Use explicit state transitions only for complex routing. Initial candidates:

- inbound message classification
- specialist delegation
- research escalation
- publish approval
- handoff acknowledgement

Simple ingestion does not need LangGraph-style routing. It needs validation and append-only writes.

## Phase 4 Query Accelerator

Neo4j or Memgraph comes after typed data is clean. The source of truth remains the typed event ledger plus GBrain pages. Graph DB ingestion is a projection job, not a replacement for the ledger.
