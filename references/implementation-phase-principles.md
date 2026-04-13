# Implementation-Phase Principles

Use this reference when a repository is entering active implementation or when a
user asks for stronger engineering guarantees than prose-only doctrine.

## Core principles

1. Build from canon and reference implementations, not from blank-page intuition.
2. Use current official documentation for unstable facts about libraries, APIs,
   SDKs, protocols, or platform behavior.
3. Prefer thin, reversible slices over broad rewrites.
4. Use TDD for deterministic logic and eval-driven development for agent
   behavior.
5. Integrate early against real boundaries; do not rely on mocks alone for the
   main validation story.
6. Keep the intended user outcome and UX constraint explicit in each meaningful
   slice.
7. Treat traces, checkpoints, rollback, and recovery as part of development,
   not as later operational cleanup.
8. Record issues, failures, and lessons continuously so mistakes are not
   rediscovered by the next session.

## Rules to encode in the harness

- No non-trivial implementation work without an active packet.
- Require packets to name:
  - runtime boundary
  - owned paths
  - reference implementations or examples reviewed
  - official documentation sources when relevant
  - integration boundaries
  - tests, evals, smoke checks, and rollback
- Keep related test code in the same change.
- Require at least one integration or boundary check for non-trivial
  implementation work.
- Require packet notes or durable logs to capture major issues and repeated
  lessons.
- Require review to check architecture, trust boundaries, validation, rollback,
  and user-facing impact before style.

## Preferred enforcement mechanisms

Prefer mechanical enforcement over repeated reminders:

- packet validation scripts
- scope and ownership checks against `git diff`
- CI gates for tests, evals, smoke checks, and required logs
- CODEOWNERS or equivalent ownership controls
- branch protection or rulesets
- secret scanning / push protection
- supply-chain provenance and dependency review when the repository matures

## Template changes that usually help

- Add an implementation development doctrine doc to `docs/engineering/`.
- Expand the packet template with user outcome, reference implementations, and
  integration checks.
- Update AGENTS/CLAUDE instructions so all implementors follow the same shared
  implementation rules.
- Add explicit "issues and learnings" expectations to definition-of-done or the
  packet notes convention.
