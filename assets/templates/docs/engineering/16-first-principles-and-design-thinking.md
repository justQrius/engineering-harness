# First Principles And Design Thinking

Use this document when work needs stronger end-to-end engineering discipline
across planning, research, implementation, review, release, and learning.

## First-principles thinking

Reduce the problem to:

- root problem
- user job
- constraints
- invariants
- assumptions
- smallest learning slice

Ask what must remain true, what can stay flexible, and what assumption should be
tested first.

## Design thinking

Keep the user workflow explicit:

- what job is the user trying to get done?
- where is the real friction?
- what outcome should improve?
- what UX constraint must remain true?
- how will we know the workflow actually got better?

## Rules

- planning must name the user job, root problem, constraints, assumptions, and
  intended learning objective
- research must distinguish canon, official current docs, and reference
  implementations
- development must test the riskiest assumption early and integrate against real
  boundaries
- review must ask whether the change fixes a root cause or only a symptom
- release must define how user-facing improvement will be observed
- learning capture must record disproven assumptions, workflow friction, and
  durable insights
