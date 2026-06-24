# AGENTS.md - engineering-harness

Developer context for Codex and other coding agent sessions. Read this before
making changes. Keep this file semantically aligned with `CLAUDE.md`; only
filename-specific and agent-perspective language should differ.

## Session-Start Protocol

Every session begins here. Follow these steps in order before doing any work:

1. **Read `.handoff/CURRENT.md`** — is there an active work packet?
   - If `approved`: this is your implementation target. Read the packet fully.
   - If `in-progress`: continue where the last session left off.
   - If `review-requested` or `done` or empty: stop. Ask the user what to do.
2. **Read `.handoff/DECISIONS.md`** — know what has been decided.
3. **Identify your role** — check the role table below. Stay in your lane.
4. **Only implement work inside an approved packet.** If there is no approved
   packet, do not start coding.

Do not skip this protocol. Do not start implementation without an approved packet.

## Development Loop (Embedded)

This is the full SDLC. Every non-trivial change follows this loop:

### Plan (Steps 1–3)

1. **Read canon** — product doctrine, engineering doctrine, decisions, current packet
2. **Plan the work** — follow the Planning Process:
   - Clarify: root problem, user job, constraints
   - Check prior art: research/, docs/, decisions
   - Decide artifacts: research doc? design doc? ADR? straight to packet?
   - Decompose large work into thin slices (each independently valuable,
     deployable, testable)
   - Draft work packet from `.handoff/templates/work-packet.md`
   - **Gate: owner must approve before implementation begins**
3. **Build context** — research using source hierarchy, stop when the next step
   is clear

### Build (Steps 4–6)

4. **Design the smallest useful slice** — root problem, user job, constraints,
   invariants, assumptions, smallest learning slice
5. **Write tests alongside** — TDD for deterministic logic, evals for agent
   behavior
6. **Implement in small, reviewable steps** — build from canon and reference
   implementations, integrate against real boundaries

### Ship (Steps 7–8)

7. **Review aggressively** — correctness → regressions → security → test
   coverage → deploy risk → maintainability → style
8. **Deploy thin slices** — reversible changes, monitor immediately, record in
   `.handoff/RELEASES.md`

### Learn (Steps 9–10)

9. **Observe** — watch what happens post-deploy
10. **Fold learning back** — update decisions, capture learnings

Details: `docs/engineering/10-development-loop.md`

## Planning Process (Embedded)

When the Planner creates a new packet, this is the flow:

```
Backlog idea
  → Clarify problem (root cause, user job, constraints)
  → Check prior art (research/, docs/, decisions)
  → Decide artifacts needed:
      Research doc?  → yes if unfamiliar problem space → research/
      Design doc?    → yes if new feature/API/subsystem → docs/design/
      Architecture?  → yes if trust boundary/topology change → docs/architecture/
      Straight to packet? → yes if problem clear, scope small
  → Decompose into thin slices (by risk, dependency, value, learning)
  → Draft packet from template
  → Owner approval (hard gate)
```

As Implementor, your entry point is an **approved packet**. If you think the
packet is wrong or incomplete, raise it — do not silently deviate.

Details: `docs/engineering/20-planning-process.md`

## Collaboration Process

This repo uses capability-based roles. Assign agents and humans to roles based
on what they do best in this repo, not by product identity.

| Role | Capability | Current assignment |
|------|-----------|-------------------|
| **Planner** | Designs work packets, sequences work | {{PLANNER — e.g. Claude Code}} |
| **Implementor** | Writes and integrates code | {{IMPLEMENTOR — e.g. Codex}} |
| **Reviewer** | Reviews diffs for correctness, security, deploy risk | {{REVIEWER — e.g. Claude Code}} |
| **Investigator** | Parallel research, debugging, exploration | {{INVESTIGATOR — e.g. any agent}} |
| **Approver** | Final sign-off (always human) | {{APPROVER — e.g. Owner}} |

No implementation begins until the packet in `.handoff/CURRENT.md` is approved
and the repo-level roles are clear.

## Rules for This Agent

1. **Follow the Session-Start Protocol** at the beginning of every session.
2. Always read `.handoff/CURRENT.md` before starting meaningful work.
3. Only implement work that is inside an approved packet.
4. Review packet feasibility critically before execution.
5. Add timestamped notes with your agent prefix in UTC ISO-8601 form.
6. Respect role boundaries — do not take on capabilities assigned to other agents.
7. When implementation completes, move the packet to `review-requested` and
   summarize what changed.
8. Do not start implementation without an approved packet.

## Repo Operating System

This repo uses a layered engineering system:

| Layer | Location | Answers |
|-------|----------|---------|
| Vision | `research/` | Why does this exist? |
| Planning | `docs/planning/` | What happens over time? |
| Design | `docs/design/` | What shape does this take? |
| Architecture | `docs/architecture/` | What structure is chosen? |
| Doctrine | `docs/engineering/` | How do we work? |
| Execution | `.handoff/` | What's happening now? |

Key engineering docs:
- `docs/engineering/01-product-doctrine.md` — daily engineering rules
- `docs/engineering/02-engineering-doctrine.md` — core engineering principles
- `docs/engineering/10-development-loop.md` — full dev loop with phases
- `docs/engineering/20-planning-process.md` — idea → approved packet

## Session-End Checklist

1. Update `.handoff/CURRENT.md` with current state and progress notes
2. If you couldn't finish, leave clear notes on where you stopped and what's next
3. If improvement opportunities found, note in `.handoff/REVIEWS.md`

## Required Shared Files

- `.handoff/CURRENT.md`
- `.handoff/BACKLOG.md`
- `.handoff/DECISIONS.md`
- `.handoff/REVIEWS.md`
- `.handoff/RELEASES.md`
- `.handoff/templates/work-packet.md`

## Cross-Project Knowledge Base

The canonical KnowledgeBase repo at `D:/Projects/KnowledgeBase`, indexed by GBrain, is a persistent, compounding intelligence layer shared across all projects. Use GBrain operations to search for prior art before research and to capture durable learnings at session end.

| Operation | Command (from any project) | When |
|-----------|---------------------------|------|
| **Query** | `gbrain query "question"` or `gbrain search "topic"` | Before research — check what's already known |
| **Capture** | Create `Raw/Sessions/`, wiki pages, update `index.md` and `log.md` | After significant work — capture durable findings |
| **Sync** | `gbrain sync` then `gbrain embed --stale` | When pages have been added or edited |
| **Extract** | `gbrain extract all` | After sync, periodically |
| **Stats** | `gbrain stats` | At session start to check KB health |

Only promote learnings that apply beyond this repo.

## Project Layout

<!-- Replace this section with the actual repo layout. Guide: -->
<!-- - List the top-level directories and what they contain -->
<!-- - Note the primary language/framework and version -->
<!-- - Call out any runtime-specific invariants (e.g. "must run on Node 20") -->
<!-- - List deployment targets and trust boundaries -->
<!-- - Note any sensitive paths (secrets, credentials, PII) -->
<!-- - Describe the build/test/run commands -->

```
engineering-harness/
├── src/                    # {{description}}
├── tests/                  # {{description}}
├── docs/                   # Engineering docs (harness-managed)
├── research/               # Research and exploration
├── .handoff/               # Work packets and operational state
├── scripts/                # Automation and checks
└── ...
```

**Language/Runtime:** {{e.g. TypeScript 5.x / Node 20}}
**Build:** `{{e.g. npm run build}}`
**Test:** `{{e.g. npm test}}`
**Deploy:** {{e.g. Fly.io via GitHub Actions}}

## Invariants

<!-- List things that must always be true in this repo -->
<!-- Examples: -->
<!-- - All API endpoints require authentication -->
<!-- - Database migrations must be backward-compatible -->
<!-- - No direct dependencies on internal packages outside this repo -->
