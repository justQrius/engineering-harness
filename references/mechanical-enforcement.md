# Mechanical Enforcement

Use this reference when the user wants stronger guarantees than prose and
review discipline alone can provide.

## Goal

Move the most important full-cycle rules into scripts and CI without forcing the
repo into a heavyweight process.

## First enforcement layer

Add these in order:

1. `scripts/audit_repo.py`
   Validate the active packet and the minimum repo operating structure.
2. `scripts/check_packet_scope.py`
   Inspect the current git diff and fail obvious scope or hygiene violations.
3. `scripts/packet_transition.py`
   Enforce legal packet-state transitions and synchronize durable logs.
4. `scripts/check_agent_drift.py`
   Warn when `AGENTS.md` and `CLAUDE.md` drift structurally or in repo invariants.
5. `scripts/validate_evidence.py`
   Validate that review-critical evidence bundles are complete.
6. `.github/workflows/harness-checks.yml`
   Run the local scripts in CI so they stop being advisory.

## What to enforce first

- a current packet exists and has the required header fields and sections
- active packets include user outcome, constraints, assumptions, learning slice,
  tests/evals, and rollback
- review-state packets have a matching review log entry
- harness changes also update durable logs
- implementation-like changes do not proceed from a draft or missing packet
- changed files outside harness paths should be cross-checked against
  `Affected Areas -> Files` and warned when undeclared

## State-machine enforcement

Packet workflows should be legal, not implied. The default harness transition
model is:

- `draft -> approved`
- `approved -> in-progress`
- `in-progress -> review-requested`
- `review-requested -> review-complete`
- `review-complete -> done`

Projects can add custom states, but they should do so deliberately and in one
script rather than by hand-editing packet headers ad hoc.

## Contract testing

Whenever a template and a validator encode the same contract, test them against
each other. The packet template and `audit_repo.py` are the canonical example:
if they drift apart, the harness becomes self-contradictory.

## What not to over-automate yet

- nuanced architecture judgments
- product-shape versus kernel-boundary arguments
- detailed source quality scoring across research docs
- complex path ownership rules before the repo actually needs them

## Design rules

- prefer simple, legible Python scripts over opaque policy engines
- fail on clear structural violations; warn on fuzzy scope drift
- keep the scripts repo-local so contributors and CI use the same checks
- treat mechanical enforcement as a complement to packet review, not a replacement