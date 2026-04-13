# Continuous Improvement

The harness should improve while normal project work happens — not as a
separate chore, but as a natural byproduct of operating the repo.

## The Improvement Loop (Autoresearch Pattern)

Adapted from [Karpathy's autoresearch](https://github.com/karpathy/autoresearch),
which runs autonomous propose → execute → evaluate → keep/revert cycles on ML
training. The same three primitives apply to harness improvement:

| Autoresearch primitive | Harness equivalent |
|----------------------|-------------------|
| **Editable asset** (`train.py`) | The harness itself: AGENTS.md, CLAUDE.md, templates, scripts, doctrine docs |
| **Scalar metric** (`val_bpb`) | Harness health signals (see Measurement below) |
| **Time-boxed cycle** (5 min) | One packet or one session — the natural unit of work |

### The four-phase cycle

Run this loop once per packet or session, not as a separate initiative:

```
┌─────────────────────────────────────────────────┐
│  1. SCAN (Generator)                            │
│     Surface friction: review findings,          │
│     agent failures, repeated manual work,       │
│     doc staleness, context bloat                │
├─────────────────────────────────────────────────┤
│  2. PROPOSE (Generator → Executor)              │
│     Pick the lightest fix from the promotion    │
│     ladder. One change per cycle — keep the     │
│     delta interpretable                         │
├─────────────────────────────────────────────────┤
│  3. APPLY (Executor)                            │
│     Make the harness change. Commit it.         │
│     If mechanical, add a script or check.       │
│     If conceptual, update doctrine or template. │
├─────────────────────────────────────────────────┤
│  4. EVALUATE (Evaluator + Memory)               │
│     Did the class of failure stop recurring?    │
│     If yes: keep. If no: revert or escalate.    │
│     If cross-project: promote to KB (capture).  │
└─────────────────────────────────────────────────┘
```

The memory layer has two tiers:
- **Repo-local**: `.handoff/REVIEWS.md`, `.handoff/DECISIONS.md`, and the
  harness docs themselves retain what applies to this repo
- **Cross-project**: the Knowledge Base (query, capture, compile, lint) retains what applies everywhere

### Key constraint: one change per cycle

Like autoresearch testing one hypothesis at a time against a single metric,
each improvement cycle should make one interpretable change. Bundling multiple
harness fixes in a single pass makes it impossible to tell which change helped
and which introduced noise.

## Trigger conditions

Improve the harness when:

- the same review finding appears more than once
- the same operational mistake appears more than once
- agents repeatedly miss a repo-specific rule
- current docs are too vague, too noisy, or competing with each other
- repeated manual work should become a script or template
- the current packet workflow does not match how the repo is actually run
- the staleness check (see below) flags decayed docs

## Promotion ladder

Use the lightest fix that prevents recurrence:

1. clarify a role rule in `AGENTS.md` or `CLAUDE.md`
2. tighten doctrine or review docs
3. update a template
4. add or improve a deterministic script
5. add a check or validation step
6. record a durable decision

## Garbage collection and staleness detection

Docs accumulate; relevance decays. Without active garbage collection, the
harness becomes noisy and agents waste context reading stale material.

### Staleness signals

A doc is likely stale when:

- it references files, functions, or flags that no longer exist in the repo
- it has not been read or cited by any agent in the last 5 packets
- it contradicts newer docs without acknowledging the change
- it describes a workflow that the team no longer follows
- its last meaningful edit predates a major architectural change

### Periodic staleness sweep

Run this sweep at the start of each `improve` cycle or every ~5 packets:

1. List all harness docs (doctrine, templates, handoff, research)
2. For each doc, check: does the code still match what the doc describes?
3. Flag docs where the answer is no or uncertain
4. For flagged docs, decide:
   - **Update**: the doc is still load-bearing but drifted from reality
   - **Archive**: the doc was useful once but the context moved on
   - **Delete**: the doc is noise — it was never useful or was superseded
5. Log what was removed and why in `.handoff/DECISIONS.md`

### Staleness in practice

When running `scripts/audit_harness.py`, check for:
- docs referencing deleted files (dead links)
- templates with placeholder text that was never filled in
- competing docs that say different things about the same topic
- research notes that were promoted to docs but never cleaned up

The audit script should report a staleness score alongside the coverage score.

## Review feedback rule

Review comments should not die in a merged diff. When the comment describes a
repeatable class of mistake, encode the lesson into the harness.

## Review-to-Guardrail Promotion

When the same class of finding appears repeatedly:

1. tag or note it as recurring in `REVIEWS.md`
2. run `scripts/scan_recurring_findings.py` to surface clustered patterns
3. decide whether the fix belongs in:
   - a scope check
   - an audit check
   - a template
   - a doctrine clarification
4. make the lightest durable change that prevents the class from recurring

## Cross-project knowledge capture

Some lessons transcend the repo they were discovered in. When the improvement
loop surfaces a durable insight — a pattern, concept, or tool finding that
would be useful in other projects — promote it to the central Knowledge Base:

- Use the **capture** operation to record the context and finding
- Use the **capture** operation for a standalone concept or pattern
- Update existing KB wiki pages when the finding refines known material
- Periodically **compile** Daily digests into wiki pages so knowledge compounds
- Periodically **lint** for orphans, contradictions, and stale claims

The KB at `D:\Projects\KnowledgeBase` is managed by the knowledgebase skill
(operations: query, ingest, compile, lint, capture). It compounds learnings
across all projects and sessions. The promotion decision is simple: if you
would want to know this in a different repo, it belongs in the KB, not just
in the repo-local harness.

## Measurement

The autoresearch pattern requires a scalar metric. For harness health, track
these signals (not all will be measurable in every repo):

| Signal | Direction | How to observe |
|--------|-----------|---------------|
| Review finding recurrence | ↓ fewer is better | Scan `REVIEWS.md` for repeated classes |
| Agent cold-start success | ↑ higher is better | Can a fresh agent session produce useful work without ad hoc rescue? |
| Context bloat | ↓ less is better | Total token count of harness docs loaded at session start |
| Handoff clarity | ↑ higher is better | Can a new agent resume from `CURRENT.md` without asking clarifying questions? |
| Manual setup steps | ↓ fewer is better | Count pre-work steps before useful output begins |
| Doc staleness ratio | ↓ lower is better | Fraction of docs flagged stale in last sweep |
| Garbage collection rate | ↑ steady is good | Docs archived or deleted per improvement cycle |
| KB compile freshness | ↑ recent is better | Last compile date from `kb-status.py` — Daily digests should be promoted regularly |
| KB lint health | ↓ fewer is better | Orphan and broken-link count from `kb-lint.py` |

The harness is working when agents need less ad hoc rescue and more of the
expected behavior emerges from the repository itself.

The harness is decaying when docs accumulate without pruning, the same
findings keep recurring, or agents ignore harness docs because they're
too long or too stale to be useful.
