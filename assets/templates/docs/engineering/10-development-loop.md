# Development Loop

The full cycle from idea to learning. Every agent and collaborator follows this
loop for non-trivial work.

## Phase 1: Orient

### Step 1 — Read the canon

Read the foundational docs before touching anything:
- `docs/engineering/01-product-doctrine.md`
- `docs/engineering/02-engineering-doctrine.md`
- `.handoff/CURRENT.md` and `.handoff/DECISIONS.md`

### Step 2 — Plan the work

Follow the planning process in `docs/engineering/20-planning-process.md`:
1. Clarify the problem (root cause, user job, constraints)
2. Check prior art (KB, research/, docs/, decisions)
3. Decide what artifacts are needed (research doc? design doc? ADR?)
4. Decompose large work into thin slices
5. Draft the work packet using `.handoff/templates/work-packet.md`
6. Get owner approval — no implementation before this gate

### Step 3 — Build context

Research deliberately using the source hierarchy. Stop when the next correct
step is clear. Do not over-research.

## Phase 2: Build

### Step 4 — Design the smallest useful, deployable, testable slice

Reduce to: root problem, user job, constraints, invariants, assumptions, and
the smallest slice that delivers value and teaches something.

### Step 5 — Write tests and evals alongside the change

- Deterministic logic → TDD with unit tests
- Agent behavior → evals and scenario checks
- Tests travel with the code, not deferred

### Step 6 — Implement in small, reviewable steps

Build from canon and reference implementations. Integrate early against real
boundaries. Treat rollback and recovery as development concerns.

## Phase 3: Ship

### Step 7 — Review aggressively

Priority: correctness → regressions → security → test coverage → deploy risk →
maintainability → style. See `docs/engineering/13-review-checklist.md`.

### Step 8 — Deploy thin slices

Prefer reversible changes. Monitor immediately. Record in `.handoff/RELEASES.md`.

## Phase 4: Learn

### Step 9 — Observe the result

Watch what actually happens post-deploy.

### Step 10 — Fold learning back

Record disproven assumptions, friction, and insights. Update decisions. Capture
cross-project learnings via the Knowledge Base (see Cross-Project Knowledge Base
section in AGENTS.md/CLAUDE.md).
