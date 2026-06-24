# Harness Components

Treat the harness as the full agent working environment, not only a system
prompt.

## Core components

### 1. Repo-root agent files

- `AGENTS.md`
- `CLAUDE.md`

Purpose:

- inject deterministic repo-level instructions
- define role split and non-negotiable local rules
- record runtime-specific invariants and operational hazards

### 2. Research layer

Purpose:

- explain why the project exists
- define vision, external evidence, and exploratory canon inputs
- prevent short-term implementation from drifting away from product goals

### 3. Planning layer

Purpose:

- define approved phase maps, roadmaps, initiative plans, and sequencing docs
- keep durable planning distinct from live packet execution

### 4. Design layer

Purpose:

- hold approved feature, subsystem, API, data-flow, and UX design docs
- preserve the intended shape of work beyond one packet

### 5. Architecture layer

Purpose:

- hold chosen system structure, reference architecture, subsystem architecture,
  ADRs, and trust-boundary docs
- keep settled architecture out of exploratory research notes

### 6. Engineering doctrine layer

Purpose:

- define how engineering should happen
- set source hierarchy, ready/done criteria, review order, and release rules

### 7. Handoff layer

Purpose:

- track what is happening now
- make current packet, decisions, reviews, and releases visible to all agents
- support clean resume after a fresh session

### 8. Templates and starter assets

Purpose:

- avoid rewriting the same scaffolding
- keep packet and log formats stable
- increase consistency across repos

### 9. Deterministic scripts

Purpose:

- reduce repeated manual setup
- turn fragile process into reusable automation
- make important checks and scaffolding mechanical

Typical examples:

- scaffold creation
- repo audits
- validation checks
- docs synchronization
- recurring operational commands

### 10. Tool and skill strategy

Purpose:

- decide when to use official docs, MCP tools, local scripts, or browsing
- keep context narrow
- encode specialized workflows as skills instead of bloating top-level prompts

### 11. Subagent and delegation strategy

Purpose:

- isolate noisy subtasks behind context firewalls
- keep one main code-path owner
- use support lanes for bounded investigation or parallel work

### 12. Verification, review, and release loop

Purpose:

- force tests, evals, smoke checks, review, and rollback thinking into the flow
- ensure agent output stays legible and recoverable

### 13. Continuous improvement loop

Purpose:

- convert repeated agent mistakes into permanent harness upgrades
- prune drift and competing canon
- keep the repo legible for future agent runs

### 14. Entry point script

Purpose:

- give contributors one command to run the harness locally
- keep local and CI verification aligned
- reduce adoption friction by hiding command sprawl behind one stable surface

### 15. Cross-project knowledge layer

Purpose:

- capture durable learnings that transcend any single repo
- provide prior-art and concept search before starting research or design
- compound intelligence across all projects and sessions

Implementation:

The canonical KnowledgeBase repo at `D:/Projects/KnowledgeBase`, indexed by GBrain, should be wired into the harness at these points:

- **Research phase**: before deep-diving, **query** the KB to check existing
  concepts, patterns, and prior session findings
- **Session end**: **capture** cross-project learnings, architectural insights,
  and novel patterns discovered during the packet
- **Review findings**: when a review uncovers a durable insight (not just a
  local bug), promote it to the KB via the **capture** operation or by updating
  a wiki page
- **Decision capture**: when `.handoff/DECISIONS.md` records a choice with
  broad applicability, file it into `Concepts/` or `Patterns/` in the KB
- **Compile cycle**: after multiple sessions produce Daily digests, **compile**
  them into wiki pages so knowledge compounds
- **Lint cycle**: periodically **lint** for orphans, contradictions, and stale
  claims to keep the KB healthy

Key operations and scripts:

| Operation | Command | When to use |
|-----------|---------|-------------|
| **Query** | `gbrain query "question"` or `gbrain search "topic"` | Before research — check what's already known |
| **Capture** | Create `Raw/Sessions/`, wiki pages, update `index.md` and `log.md` | After significant work — capture durable findings |
| **Sync** | `gbrain sync` then `gbrain embed --stale` | When pages have been added or edited |
| **Extract** | `gbrain extract all` | After sync, periodically |
| **Stats** | `gbrain stats` | At session start to check KB health |

The KB is not a replacement for repo-local docs. Repo-specific decisions stay
in `.handoff/DECISIONS.md`. The KB captures what applies beyond the repo.

## Practical rule

Whenever an agent fails, ask:

1. was the problem missing context?
2. was the context in the wrong place?
3. should the fix be a template, script, check, or role rule?

Do not solve recurring failures only with longer prompts.