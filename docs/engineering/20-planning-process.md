# Planning Process

How work moves from idea to approved work packet.

## The flow

```
Backlog idea
  → 1. Clarify the problem (root cause, user job, constraints)
  → 2. Check prior art (KB, research/, docs/, decisions)
  → 3. Decide artifacts needed (research? design? ADR? straight to packet?)
  → 4. Decompose into thin slices
  → 5. Draft the work packet
  → 6. Owner approval → implementation begins
```

## Artifact decision tree

**Need a research doc?** Yes if: unfamiliar problem space, external tool
evaluation needed, technology the team hasn't used. Output → `research/`

**Need a design doc?** Yes if: new feature/subsystem/API, multiple viable
approaches, UX or data flow needs specification, work spans multiple systems.
Output → `docs/design/`

**Need an architecture ADR?** Yes if: changes a trust boundary, data model, or
system topology, constrains future work, involves a trade-off worth recording.
Output → `docs/architecture/`

**Straight to packet?** Yes if: problem is clear, solution is known, scope is
small, existing docs cover the area.

## Thin-slice decomposition

Each slice must be independently valuable, deployable, testable, and reviewable.

Decompose by: user capability, system boundary, risk, or dependency.

Sequence by: risk first, then dependencies, then value, then learning.

Record initiatives and slice sequences in `docs/planning/`. Each slice becomes
its own work packet.

## Backlog priority order

1. Blocking dependencies — what unblocks other work?
2. Risk reduction — what validates the riskiest assumption?
3. User value — what delivers the most value soonest?
4. Learning — what teaches the most about the problem?
5. Effort — among equal-value items, prefer smaller ones

## Gate

No implementation begins before the owner approves the work packet. This is a
hard gate, not a suggestion.
