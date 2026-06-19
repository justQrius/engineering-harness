# Work Packet

## Header

- Packet ID: EH-2026-06-19-01
- Title: Harden harness checks for encoding, retrofit, and CI warnings
- Status: review-requested
- Gate: Owner approval confirmed via chat (2026-06-19)
- Owner: Shaktisinh
- Driver agent: Codex
- Reviewer agent: Codex self-review, owner review after commit
- Parallel support agent: none
- Support scope: N/A
- Research/design support: AdiAstra Harness Checks failure on 2026-06-19
- Created: 2026-06-19T14:58:21Z
- Updated: 2026-06-19T15:05:30Z

## Problem

A downstream repo using the harness failed GitHub Harness Checks because `audit_repo.py` crashed on a non-UTF-8 byte in `.handoff/CURRENT.md`. The workflow itself was structurally fine, but the failure mode was harder to read than it needed to be. The same run also surfaced avoidable CI annotations: Go cache restore warnings in repos without `go.sum`, and Node 20 deprecation warnings from older GitHub Action major versions.

## User / Job To Be Done

A repo owner starting or retrofitting a project should get clear, actionable harness feedback. Harness CI should fail on real issues, not Python tracebacks or noisy avoidable warnings.

## Vision Link

This supports the harness goal of making repo operation deterministic, understandable, and reusable across projects.

## Hypothesis

If the harness reports invalid UTF-8 as a first-class audit issue, preserves non-git retrofit tolerance, and avoids known CI warning noise, future projects will be easier to bootstrap, debug, and keep green.

## User Outcome / UX Constraint

Agents and humans should immediately know whether a failing run is caused by repo content, packet drift, or workflow infrastructure.

## Root Constraint / Invariant

Keep the harness universal and repo-agnostic. Do not encode AdiAstra-specific paths, packet IDs, or project assumptions into the reusable harness.

## Assumptions To Test

- Invalid UTF-8 should produce an audit issue instead of an unhandled exception.
- Fresh or non-git retrofit targets should not crash scope checks before git setup.
- GitHub Actions workflow warnings can be reduced without changing harness semantics.

## Smallest Learning Slice

Patch the canonical scripts and workflow, run the harness validation suite, then sync the installed Codex skill copy.

## Thin-Slice Scope

- Improve UTF-8 read error handling in `scripts/audit_repo.py`.
- Preserve or restore non-git fallback in `scripts/check_packet_scope.py`.
- Update reusable GitHub Actions workflow action versions and disable Go cache where no `go.sum` exists.
- Sync maintained changes into the installed Codex skill copy.

## Out Of Scope

- Redesigning packet lifecycle rules.
- Changing project-specific CI behavior beyond the reusable workflow template.
- Updating unrelated harness docs or templates.
- Adding new dependencies.

## Affected Areas

- Files:
- scripts/audit_repo.py
- scripts/check_packet_scope.py
- .github/workflows/harness-checks.yml
- assets/templates/.github/workflows/harness-checks.yml
- assets/templates/scripts/audit_repo.py
- assets/templates/scripts/check_packet_scope.py
- scripts/test_harness_failure_modes.py
- scripts/test_skill_integrity.py
- .handoff/CURRENT.md
- .handoff/REVIEWS.md
- C:/Users/shakt/.codex/skills/engineering-harness/scripts/audit_repo.py
- C:/Users/shakt/.codex/skills/engineering-harness/scripts/check_packet_scope.py
- C:/Users/shakt/.codex/skills/engineering-harness/.github/workflows/harness-checks.yml

- Systems:
- Repo-local harness checks
- GitHub Actions reusable harness workflow
- Installed Codex engineering-harness skill

- Trust boundaries:
- No project-specific data or repo-local state should be copied into the installed universal skill.

## References

### Internal

- Relevant `research/` docs: none
- Relevant `docs/planning/` docs: none
- Relevant `docs/design/` docs: none
- Relevant `docs/architecture/` docs: none
- Relevant `docs/engineering/` docs: `docs/engineering/17-mechanical-enforcement.md`, `docs/engineering/20-planning-process.md`
- Relevant local code: `scripts/audit_repo.py`, `scripts/check_packet_scope.py`, `.github/workflows/harness-checks.yml`

### External

- Official docs: GitHub Changelog, Node 20 deprecation on GitHub Actions runners
- Reference implementations / repos / examples: AdiAstraLabs Harness Checks run `27832316095`
- Other supporting sources: none

## Acceptance Criteria

- `audit_repo.py` reports invalid UTF-8 as a structured issue instead of crashing.
- `check_packet_scope.py` skips diff-aware validation with a warning outside git worktrees.
- Harness workflow avoids Go setup cache warnings in repos without `go.sum`.
- Harness workflow uses current major action versions checked against official GitHub releases.
- Canonical harness validation passes.
- Installed Codex skill copy receives the maintained script/workflow changes.

## Evidence Manifest (optional)

- Local validation command outputs from canonical harness repo.
- Installed skill validation outputs.

## Tests And Evals

- Tests to add or update: add or update harness tests where they cover script/template contracts.
- Evals or scenarios to add or run: run invalid UTF-8 smoke test against `audit_repo.py`.
- Integration or boundary checks: run canonical harness validation suite and installed skill integrity checks.
- Manual smoke checks: verify workflow YAML and installed skill file sync.

## Deployment Impact

- Runtime or infrastructure impact: future GitHub Actions workflow scaffolds use newer action versions and quieter Go setup.
- Config or secret impact: none.
- Observability impact: clearer CI/audit failures.

## Rollback Plan

Revert the script/workflow edits and restore the previous installed skill files from the canonical repo if validation fails.

## Notes / Discussion

- 2026-06-19T14:58:21Z - Codex opened packet after owner approved all proposed harness improvements in chat.

### 2026-06-19T15:05:30Z - Codex implementation handoff

- Implemented canonical harness failure-mode hardening and workflow warning cleanup.
- Synced the maintained script/workflow/template changes into `C:/Users/shakt/.codex/skills/engineering-harness`.
- Verified canonical tests and installed skill validation pass.
