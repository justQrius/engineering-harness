# Adaptation Rules

This skill installs a universal operating system, not a universal product
architecture. Adapt the harness to the repository in front of you.

## Preserve

- real project vision and business goals
- runtime-specific invariants
- product-specific trust boundaries
- deploy and rollback realities
- coherent local naming and numbering conventions
- existing high-signal docs, tests, scripts, and runbooks

## Standardize

- agent role contract
- research -> planning/design/architecture -> doctrine -> handoff layering
- packet-driven implementation workflow
- source hierarchy
- review and release discipline
- durable decision logging
- continuous harness-improvement loop

## Do not do these

- overwrite strong local documentation just to match the template
- invent canon that conflicts with existing product truth
- copy runtime-specific rules from one repo into another without validation
- collapse everything into one giant instruction file
- treat every repo as if it needs the same deployment or ops model

## Universal vs project-specific split

Universal:

- structure
- collaboration model
- workflow gates
- validation discipline
- improvement loop

Project-specific:

- system architecture
- durable planning and design docs
- runtime contracts
- deployment commands
- secrets and credential model
- external integrations
- operations runbooks

## Retrofit rule

When adapting an existing repo:

1. audit first
2. scaffold missing pieces second
3. merge local truth third
4. tighten only what repeated failures justify

Promote material when it settles:

- keep external scans, exploratory synthesis, and vision in `research/`
- move approved plans into `docs/planning/`
- move approved feature or subsystem designs into `docs/design/`
- move chosen reference architecture and ADRs into `docs/architecture/`

If a local rule matters to daily engineering, move it into the harness instead
of leaving it buried in chat history.
