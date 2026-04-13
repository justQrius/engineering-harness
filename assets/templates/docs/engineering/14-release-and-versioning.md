# Release And Versioning

## What Qualifies As A Release

A release is any deployable change that reaches a real environment or changes a
real validation lane in a way future operators may depend on. Completed packets
that deploy to a validation host should usually have a release entry. Internal
drafts, planning updates, and docs-only changes do not.

## Branching

- prefer short-lived branches
- keep diffs narrow and reviewable

## Commits

Prefer small commits with clear intent.

## Release Notes

Record meaningful deployable changes in `.handoff/RELEASES.md`.
When a packet transitions to `done`, scaffold or confirm the corresponding
release entry instead of relying on memory later.

## Deployment Discipline

- deploy thin slices
- prefer reversible changes
- monitor immediately after release
- record known follow-up items