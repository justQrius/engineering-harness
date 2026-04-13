# Lifecycle Modes

Use the same skill across the full repository lifecycle. Choose the narrowest
mode that matches the current need.

## `init`

Use for a new or nearly empty repo.

Goals:

- create the operating structure
- install starter docs and logs
- establish agent roles and packet workflow
- seed research, doctrine, and handoff layers

Checklist:

1. Audit the repo to confirm little or no existing harness.
2. Run `bootstrap_harness.py`.
3. Fill project layout, runtime, trust-boundary, and deployment specifics.
4. Create the first backlog or current packet if work is ready.

## `retrofit`

Use for an existing repo with partial docs or inconsistent process.

Goals:

- preserve strong existing material
- install missing harness layers
- remove ambiguity about canon and ownership
- create a migration path instead of a blind rewrite

Checklist:

1. Audit the repo.
2. Compare existing docs and workflows against the harness baseline.
3. Create only missing scaffold files first.
4. Merge real local truth into the harness docs.
5. Add a retrofit packet if the migration itself is substantial.

## `operate`

Use when the repo already has the harness and active engineering work is in
progress.

Goals:

- keep work packet driven
- preserve clear handoff state
- update decisions, reviews, and releases as durable outputs land
- check and contribute to cross-project knowledge

Checklist:

1. Read `CURRENT.md` before doing non-trivial work.
2. Query the Knowledge Base before research or design phases to check prior art.
3. Keep packet status aligned with actual work state.
4. Update decisions, reviews, and releases when the change merits it.
5. Keep canon and source hierarchy clear as docs evolve.
6. At session end, capture durable cross-project learnings via the Knowledge Base if they emerged.

## `improve`

Use when the harness is present but repeated friction shows it is no longer
sufficient.

Examples:

- agents repeat the same mistake
- review findings cluster around the same class of bug
- current docs are too vague or too long
- repeated work should become a script or template
- canon has drifted or duplicated itself

Checklist:

1. Identify the repeated failure mode.
2. Decide whether the fix belongs in docs, templates, scripts, checks, or role rules.
3. Encode the lesson once so future runs inherit it.
4. If the lesson applies beyond this repo, promote it to the KB via the capture operation or by updating a wiki page.
5. Validate the change against a real or representative workflow.
