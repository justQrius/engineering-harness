# Implementation Development Principles

Use this document when the repository is in active implementation mode.

## Principles

1. Build from canon and reference implementations, not from blank-page intuition.
2. Use current official documentation for unstable technical facts.
3. Prefer thin, reversible slices over broad rewrites.
4. Use TDD for deterministic logic and eval-driven development for agent behavior.
5. Integrate early against real boundaries.
6. Keep the user outcome and UX constraint explicit.
7. Treat rollback, traces, checkpoints, and recovery as development concerns.
8. Capture issues and durable lessons continuously.

## Rules

- no non-trivial implementation work without an approved packet
- require packets to name:
  - user outcome and UX constraint
  - reference implementations or examples reviewed
  - official docs used when relevant
  - integration boundaries
  - tests, evals, smoke checks, and rollback
- keep related tests with the change
- run at least one integration or boundary check for non-trivial implementation work
- record major issues and repeated lessons in packet notes and durable logs when warranted
- prefer scripts, CI checks, and templates over prose when a rule matters on every change

## Full-cycle note

This document is implementation-centered. Use
`docs/engineering/16-first-principles-and-design-thinking.md` when planning,
research, review, release, or learning capture need the same level of
discipline as coding.
