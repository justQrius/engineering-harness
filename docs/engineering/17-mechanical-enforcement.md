# Mechanical Enforcement

Use this document when the repository wants stronger guarantees than doctrine
and review alone can provide.

## Purpose

Mechanical enforcement turns the most important workflow rules into repo-local
scripts and CI checks so contributors and reviewers share the same baseline.

## First enforcement layer

- `scripts/audit_repo.py`
  Verifies the active packet has the required structure, sections, and review linkage.
- `scripts/check_packet_scope.py`
  Inspects the current git diff and fails obvious packet, scope, or durable-log hygiene violations.
- `scripts/packet_transition.py`
  Advances packet states through legal transitions and keeps timestamps and durable logs synchronized.
- `scripts/validate_evidence.py`
  Verifies that evidence bundles are complete before review relies on them.
- `scripts/check_agent_drift.py`
  Warns when `AGENTS.md` and `CLAUDE.md` drift structurally or in repo invariants.
- `.github/workflows/harness-checks.yml`
  Runs the repo-local checks in CI.

## Scope cross-reference

`scripts/check_packet_scope.py` should compare changed files against the
`Affected Areas -> Files` list in `.handoff/CURRENT.md`. Start by warning on
undeclared file touches instead of hard-failing them; once packet authorship is
consistently precise, a project can promote that warning into a blocking check.

## Rules

- fail on clear structural violations rather than relying on reviewers to spot them later
- warn on fuzzy scope drift rather than pretending every judgment can be automated
- use the same repo-local scripts in local development and CI
- treat script failures as blockers unless the owner explicitly accepts an exception
- keep the checks small, legible, and easy to update as the harness evolves