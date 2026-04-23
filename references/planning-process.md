# Planning Process

This document defines how work moves from a backlog idea to an approved work
packet. It bridges the gap between strategic vision (research/, docs/planning/)
and tactical execution (.handoff/CURRENT.md).

## When to use this process

Any non-trivial work — anything that changes code, architecture, or
configuration — should go through this process. Trivial fixes (typos, one-line
config changes) can skip to a minimal packet.

## The planning flow

```
Backlog idea
  │
  ├─ 1. Clarify the problem
  │
  ├─ 2. Check prior art (KB, research/, docs/)
  │
  ├─ 3. Decide: what artifacts are needed?
  │     ├─ Research doc?      → research/
  │     ├─ Design doc?        → docs/design/
  │     ├─ Architecture ADR?  → docs/architecture/
  │     └─ Straight to packet → .handoff/CURRENT.md
  │
  ├─ 4. Decompose into thin slices
  │
  ├─ 5. Draft the work packet
  │
  └─ 6. Get owner approval → status: approved
```

## Step 1: Clarify the problem

Before anything else, answer:

- What is the root problem? (not the symptom)
- Whose job are we helping?
- What outcome should improve?
- What constraints are non-negotiable?

If you cannot answer these clearly, the work is not ready to plan. Go back to
research or discussion.

## Step 2: Check prior art

Before creating new artifacts:

- Search the Knowledge Base: query via `gbrain query "question"` or `gbrain search "topic"`
- Check `research/INDEX.md` for existing analysis
- Check `docs/planning/` for existing roadmaps or phase maps
- Check `docs/architecture/` for relevant ADRs
- Check `docs/design/` for existing designs in the affected area
- Check `.handoff/DECISIONS.md` for relevant prior decisions

This prevents re-deriving what is already known and ensures new work builds on
existing decisions rather than contradicting them.

## Step 3: Decide what artifacts are needed

Not every piece of work needs every artifact. Use this decision tree:

### Do you need a research doc?

Yes, if:
- The problem space is unfamiliar or the solution is uncertain
- External tools, APIs, or platforms need evaluation
- Competitive or market analysis would inform the approach
- The work involves a technology the team hasn't used before

No, if:
- The problem and solution are well understood
- Existing research already covers the topic

Output: a doc in `research/` with findings, options, and recommendation.

### Do you need a design doc?

Yes, if:
- The work involves a new feature, subsystem, or API
- Multiple implementation approaches exist and the choice matters
- The UX or data flow needs explicit specification
- The work spans multiple files or systems and the shape matters

No, if:
- The work is a bugfix or small enhancement with an obvious approach
- The design is already documented in an existing design doc
- The scope is small enough that the work packet itself captures the design

Output: a doc in `docs/design/` with the chosen approach, alternatives
considered, and interface contracts.

### Do you need an architecture decision?

Yes, if:
- The work changes a trust boundary, data model, or system topology
- The decision constrains future work across the project
- The choice involves a trade-off that should be recorded for posterity
- An existing ADR needs to be updated or superseded

No, if:
- The design is local to one feature and doesn't constrain the system
- The architecture is already settled for this area

Output: an ADR in `docs/architecture/` (or a draft in `docs/architecture/drafts/`
if not yet ratified).

### Can you go straight to a work packet?

Yes, if:
- The problem is clear, the solution is known, and the scope is small
- Existing research, design, and architecture cover the affected area
- The work is a well-understood pattern (bugfix, config change, small feature)

## Step 4: Decompose into thin slices

Large initiatives must be broken into slices before becoming work packets.
Each slice should be:

- **Independently valuable** — delivers a usable outcome, not just scaffolding
- **Independently deployable** — can ship without waiting for other slices
- **Independently testable** — has clear acceptance criteria and tests
- **Small enough to review** — one reviewer can understand the full diff

### Decomposition strategies

1. **By user capability** — each slice delivers one thing the user can do
2. **By system boundary** — each slice touches one integration or subsystem
3. **By risk** — the riskiest assumption gets its own slice, tested first
4. **By dependency** — slice along the dependency graph so earlier slices
   unblock later ones

### Sequencing slices

Order slices by:

1. **Risk** — test the riskiest assumption first
2. **Dependency** — build foundations before features
3. **Value** — deliver user-facing value as early as possible
4. **Learning** — front-load slices that teach something important

Record the full initiative and its slice sequence in `docs/planning/`. Each
slice becomes its own work packet when it reaches the top of the backlog.

## Step 5: Draft the work packet

Use `.handoff/templates/work-packet.md` as the template. Fill in every section.
The packet must pass the Definition of Ready gate before approval:

- Problem and outcome are clear
- Thin-slice scope is defined
- Out-of-scope items are named
- Affected files or systems are identified
- Relevant docs and sources are identified
- Tests and evals are known
- Deployment impact is known
- Rollback is known

## Step 6: Get owner approval

The work packet moves to `.handoff/CURRENT.md` with status `draft`. The owner
reviews and either:

- **Approves** → status changes to `approved`, implementation can begin
- **Requests changes** → Planner revises the packet
- **Rejects** → packet is archived or returned to backlog with a note

No implementation begins before approval. This is a hard gate.

## Backlog prioritization

When multiple items compete for attention, prioritize by:

1. **Blocking dependencies** — what unblocks other work?
2. **Risk reduction** — what validates the riskiest assumption?
3. **User value** — what delivers the most value soonest?
4. **Learning** — what teaches the most about the problem space?
5. **Effort** — among equal-value items, prefer smaller ones

The backlog in `.handoff/BACKLOG.md` should always be ordered by priority.
Only the top item moves to `CURRENT.md`.

## Planning artifacts lifecycle

```
research/          → persists as reference; archive when superseded
docs/planning/     → persists as roadmap; update as slices complete
docs/design/       → persists as specification; update or supersede
docs/architecture/ → persists as decision record; supersede, never delete
.handoff/CURRENT.md → one active packet; transitions through states
.handoff/BACKLOG.md → ordered queue; top item is next
```
