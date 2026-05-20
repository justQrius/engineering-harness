# Temporal Brain Service

Status: service definition drafted; runtime not verified from sandbox

## Purpose

Temporal runs durable workflows for brain operations whose state must survive
agent restarts:

- research tasks
- KB sync jobs
- content pipeline jobs
- agent handoffs

Typed facts still go through `scripts/brain_write.py`; Temporal owns retries,
timeouts, and workflow state.

## Local Service

Use the official Temporal development server or a production Temporal cluster.
For local development:

```bash
temporal server start-dev --db-filename ~/.gbrain/temporal/temporal.db
```

Then start a worker that registers:

- workflows from `scripts/brain_temporal_workflows.py`
- activities bound to local GBrain and messaging commands

## Verification

This session could not start or inspect a service because:

- `systemctl --user` returned `Operation not permitted`
- Docker socket access was denied
- network install is restricted

A verified deployment must show:

- Temporal frontend reachable
- worker registered on the brain task queue
- one `KbSyncWorkflow` smoke run completes
- the workflow writes an `ExecutionTrace` through `scripts/brain_write.py`
