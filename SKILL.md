---
name: engineering-harness
description: "Bootstrap, retrofit, operate, and continuously improve an agent-ready engineering and development harness for a repository. Use when any AI coding agent needs to set up or maintain the full working system for agents and human collaborators: AGENTS.md and CLAUDE.md, research and doctrine docs, handoff logs, work-packet workflow, review and release discipline, tool and skill strategy, and recurring harness-improvement rules. Trigger this skill at the start of a new project, when adopting an existing project that lacks a clear operating model, or when repeated agent failures indicate the repository needs stronger guardrails, better docs, or more deterministic scaffolding."
---

# Engineering Harness

## Overview

Install and maintain a repository-local engineering operating system that makes
AI coding agents and human reviewers effective over the full project lifecycle.
Treat the repository as the system of record for agent instructions, planning,
design, architecture, workflow, decisions, reviews, releases, and recurring
lessons.

## Source of Truth and Agent Installation

The canonical engineering-harness skill repository lives at
`/home/justqrius/.hermes/profiles/hermes-lab/workspace/engineering-harness`. Make changes there
first, then install or update the Claude Code and Codex skill copies:

- Claude Code: `/home/justqrius/.claude/skills/engineering-harness/`
- Codex: `/home/justqrius/.codex/skills/engineering-harness/`

Do not treat installed copies as the source of truth. They are deployment targets
for the coding agents.

## Workflow

### 1. Classify the repository first

Decide which mode applies:

- `init`: greenfield repo with little or no operating structure
- `retrofit`: existing repo with partial docs, process, or agent guidance
- `operate`: active repo that already uses the harness and needs packet-driven work
- `improve`: repo where repeated mistakes, review findings, or drift should be
  encoded back into the harness

Run the audit script before changing anything. Use its output to identify what
already exists and what is missing. The audit also detects the repo stack and
recommends project-CI additions so the harness job and the product job can be
configured separately.

**Note:** Harness scripts live in this skill's `scripts/` directory and are
copied into the target repo by `bootstrap_harness.py`. Before bootstrap, run
audit from the skill directory:

```bash
python <skill-dir>/scripts/audit_harness.py <repo-path>
```

After bootstrap, the scripts are available locally in the target repo's
`scripts/` directory and can be run directly.

Read [references/lifecycle-modes.md](./references/lifecycle-modes.md) for the
mode-specific checklist.

### 1b. Check the Knowledge Base for prior art

Before starting research or design, query the central Knowledge Base for
existing concepts, patterns, and session findings that may inform the work.

The canonical KB repo at `D:/Projects/KnowledgeBase`, indexed by GBrain, is a cross-project intelligence layer
managed by the `knowledgebase` skill. It accumulates research, architectural
decisions, patterns, and tool knowledge across all projects. Checking it before
work prevents re-deriving what was already discovered in a previous session or
project.

**Operations:**

| Operation | How | When |
|-----------|-----|------|
| **query** | Search with `gbrain__query` / `gbrain__search` or run `gbrain query "question"` / `gbrain search "topic"` | Before research, when answering questions |
| **sync** | Run `gbrain sync` then `gbrain embed --stale` | When new pages or edits have accumulated |
| **extract** | Run `gbrain extract all` | After sync, periodically |
| **stats** | Run `gbrain stats` | At session start to check KB health |
| **capture** | Create `Raw/Sessions/`, wiki pages, update `index.md` and `log.md` | When session yields findings |

### 2. Preserve local truth and adapt the harness

Do not blindly stamp templates over a repository.

Preserve:

- real product or architecture truth already present in the repo
- runtime-specific invariants
- deployment and trust-boundary constraints
- established naming or numbering schemes when they are coherent

Standardize:

- agent collaboration contract
- research -> planning/design/architecture -> doctrine -> handoff layering
- work-packet lifecycle
- review, release, and rollback discipline
- source hierarchy and canon rules
- continuous harness-improvement loop

Read [references/adaptation-rules.md](./references/adaptation-rules.md) before
retrofitting an existing repo.

### 3. Install the core harness

Use `scripts/bootstrap_harness.py <repo-path> --project-name <name>` to copy the
starter files from `assets/templates/` into the target repository. By default
the script only creates missing files. Use `--force` only when replacing
placeholder scaffolding or when the user explicitly wants a reset.

In `--mode retrofit` (the default), the script also merges key sections into
existing files that lack them. For example, if a repo already has `CLAUDE.md`
but it doesn't have a "Cross-Project Knowledge Base" section, the script
appends it. Inline references to `/kb` slash commands are upgraded to
operation names with script paths. Running retrofit twice is idempotent —
already-present sections and already-updated references are skipped.

The baseline harness includes:

- `AGENTS.md` and `CLAUDE.md`
- `research/`
- `docs/planning/`
- `docs/design/`
- `docs/architecture/`
- `docs/engineering/`
- `.handoff/`

After bootstrapping, edit the scaffold so it reflects the actual repo:

- project layout
- runtime and deployment invariants
- collaboration roles
- product, design, and architecture canon
- operations and rollback notes where relevant

When the harness includes a local entrypoint such as `Taskfile.yml`, adapt it
to the repo's actual stack and make sure `task check` becomes the normal local
verification path.

Read [references/harness-components.md](./references/harness-components.md) for
the full component model.

### 4. Make the harness legible to agents

Keep top-level instructions concise and deterministic. Prefer progressive
disclosure:

- short repo-root agent files with embedded critical process
- focused planning, design, and architecture docs
- focused engineering doctrine docs
- handoff files for current state
- scripts for deterministic repeated tasks
- references for detailed material loaded only when needed

The most important principle for agent adherence: **embed the critical SDLC
steps directly in `CLAUDE.md` and `AGENTS.md`**, not behind "read this doc"
pointers. Agents load these files at session start. If the process is only in
`docs/engineering/`, agents may not read it. The templates include:

- **Session-Start Protocol** — the exact steps an agent must follow when
  beginning a session (check CURRENT.md, check decisions, identify role, follow
  the dev loop)
- **Development Loop (embedded)** — the full 10-step SDLC condensed into the
  agent file so it is always in context
- **Planning Process (embedded)** — the flow from backlog idea to approved
  packet, condensed into the agent file

The `docs/engineering/` layer provides full details for agents that need deeper
context. But the agent files must be self-sufficient for the common case: an
agent should be able to pick up work correctly with zero manual prompting from
the user beyond "continue" or "start next packet."

When editing `AGENTS.md` or `CLAUDE.md`, update both files in the same change.
The drift-check script should stay green.

Encode real constraints mechanically when possible. If a rule matters on every
change, prefer a script, check, template, or generated file over prose alone.

Keep the document layers clean:

- `research/` for vision, landscape, external evidence, and open synthesis
- `docs/planning/` for approved phase maps, roadmaps, and initiative plans
- `docs/design/` for approved feature, subsystem, API, and UX design docs
- `docs/architecture/` for chosen reference architecture, subsystem
  architecture, ADRs, and trust-boundary docs
- `docs/engineering/` for process and workflow doctrine
- `.handoff/` for the active packet and current operational state

Promote settled material out of `research/` once it becomes the chosen plan,
design, or architecture. Do not leave canonical implementation direction buried
inside exploratory notes.

When a repository needs to bridge the gap between backlog ideas and approved
work packets, install the planning process. The planning process defines:

- how to clarify problems before framing a packet
- when to create research docs, design docs, or architecture ADRs vs. going
  straight to a packet
- how to decompose large initiatives into thin slices
- how to prioritize the backlog
- the hard approval gate before implementation begins

The planning process is embedded directly in `CLAUDE.md` and `AGENTS.md` so
agents always have it in context, with full details in
`docs/engineering/20-planning-process.md`. This ensures agents can pick up work
correctly without manual prompting from the user.

Read [references/planning-process.md](./references/planning-process.md) for the
full planning flow, artifact decision tree, and decomposition strategies.

When a repository is crossing from research or planning into active
implementation, add an explicit implementation-phase doctrine. At minimum, the
harness should encode:

- reference-implementation-first development for non-trivial subsystems
- current official documentation checks for unstable libraries, APIs, SDKs, and protocols
- TDD for deterministic behavior plus eval-driven development for agent behavior
- integration-driven development against real boundaries, not mocks alone
- explicit user outcome and UX constraints for each meaningful slice
- continuous issue and learning capture in packet notes and durable logs

Read [references/implementation-phase-principles.md](./references/implementation-phase-principles.md)
when the user wants stronger development guarantees or when implementation work
is about to begin.

When the user wants first-principles thinking or design thinking embedded into
the harness, encode them across the full cycle rather than as philosophy-only
statements. Add guidance and templates that cover:

- planning from root problem, user job, constraints, invariants, and assumptions
- research that separates durable truths from unstable implementation facts
- development that tests the riskiest assumption early and preserves UX intent
- review that distinguishes root-cause fixes from local symptom patches
- release that verifies the user-facing outcome, not only internal correctness
- learning capture that records disproven assumptions and durable insights

Read [references/first-principles-and-design-thinking.md](./references/first-principles-and-design-thinking.md)
when the user wants end-to-end cycle guidance rather than implementation-only
rules.

When the user wants stronger guarantees beyond doctrine, add a first mechanical
enforcement layer into the harness. At minimum, the shared harness should be
able to install:

- a repo-local audit script that validates packet structure and required sections
- a diff-aware scope check that fails obvious packet, log, and harness hygiene violations
- a CI workflow that runs the repo-local checks on push and pull request
- doctrine that explains what is mechanically enforced and what still depends on review

Read [references/mechanical-enforcement.md](./references/mechanical-enforcement.md)
when the user wants machine-enforced packet, scope, or release discipline.

Read [references/ci-stack-integration.md](./references/ci-stack-integration.md)
when adapting the project CI job to the actual language stack.

### 5. Wire collaboration and ownership

Make the repo-level role contract explicit using capability-based roles, not
product names. Tools change; capabilities persist.

Default lane policy for Shaktisinh's engineering workflow:

- **Morpheus** conducts the workflow: packet framing, context shaping, lane
  prompts, tool/skill routing, verification, and final integration judgment.
- **Claude Code via Ollama cloud** is the default implementation lane because it
  has the higher practical rate-limit budget for long edit/test/fix loops.
- **Codex** is a sparse independent review and challenge lane. Use it at gates:
  plan critique for complex work, diff review, adversarial/security challenge,
  or correction review when the implementation lane gets stuck.
- **Default Claude Code using first-party model access** is a manual reserve lane
  only. Do not put it on the default hot path. Use it only when Shaktisinh
  explicitly asks for a premium reserve judgment pass.

This preserves limited first-party/Codex rate limits for high-leverage judgment
instead of spending them on routine implementation tokens.

| Role | Capability | Typical assignment |
|------|-----------|-------------------|
| **Orchestrator** | Frames packets, routes tools/skills, manages context, verifies | Morpheus |
| **Planner** | Designs work packets, breaks down problems, sequences work | Morpheus, with sparse Codex/Claude reserve critique when useful |
| **Implementor** | Writes and integrates code within approved packets | Claude Code via Ollama cloud |
| **Reviewer** | Reviews diffs for correctness, regressions, security, deploy risk | Codex at gates; Morpheus verifies deterministically |
| **Investigator** | Parallel support: research, debugging, exploration in isolation | Any agent in a support lane |
| **Approver** | Final sign-off — always human | Owner / tech lead |

Assign roles based on what each agent is best at in the current repo, not by
product identity. The same agent may hold different roles across repos. When
a tool is deprecated or replaced, the role contract survives — just reassign
the role to the new tool.

Track work through `.handoff/CURRENT.md` using the shared packet template.
Require explicit scope, acceptance criteria, tests, deploy impact, and rollback
before implementation begins.

Use `python scripts/packet_transition.py <new-status>` in the target repo when
the harness installs it. Prefer the transition script over hand-editing packet
status, timestamps, and review or release scaffolding.

### 6. Bake in verification and back-pressure

The harness should force useful pauses:

- readiness checks before implementation
- tests and eval expectations alongside code changes
- review focused on correctness, regressions, security, and deploy risk
- release notes and rollback notes for meaningful deployable changes
- escalation to a human when judgment, approval, or risk acceptance is needed

Prefer deterministic scripts and runbooks for repeated operator flows.

If the user asks for stronger guarantees, add machine-enforced checks rather
than only expanding prose:

- packet and scope validation scripts
- CI gates for required tests, evals, and logs
- path ownership rules
- secret and supply-chain protections
- implementation templates that require reference implementations, integration
  checks, and user-outcome framing

For packets that rely on real-host or otherwise expensive evidence, declare the
expected artifacts in the packet and use `python scripts/validate_evidence.py`
before requesting review.

### 7. Continuously improve the harness while the project runs

Do not treat the harness as finished after setup. The harness uses an
autoresearch-style improvement loop (adapted from
[Karpathy's autoresearch](https://github.com/karpathy/autoresearch)):

```
SCAN → PROPOSE → APPLY → EVALUATE (keep or revert)
```

Each cycle makes one interpretable change to the harness, then measures whether
the class of failure it targeted stops recurring. One change per cycle — bundling
fixes makes evaluation impossible.

When agents repeat mistakes, feed the lesson back using the promotion ladder:

1. clarify a role rule in `AGENTS.md` or `CLAUDE.md` (lightest)
2. tighten doctrine or review docs
3. update a template
4. add or improve a deterministic script
5. add a check or validation step
6. record a durable decision (heaviest)

Periodically run garbage collection: flag stale docs, archive superseded
material, delete noise. Docs accumulate; relevance decays.

Read [references/continuous-improvement.md](./references/continuous-improvement.md)
for the full autoresearch-adapted loop, staleness detection, and measurement
signals.

Periodically run `python scripts/scan_recurring_findings.py` in the target repo
to surface review patterns that should be promoted into guardrails.

### 7b. Capture cross-project learnings to the Knowledge Base

When harness work produces insights that apply beyond this repo, promote them
to the central Knowledge Base using the `knowledgebase` skill:

| What was learned | KB operation |
|-----------------|------------|
| Novel pattern or concept | **capture** (create `Concepts/` page) |
| Tool discovery or configuration | **capture** (update `Tools/` page) |
| Architectural insight with broad applicability | **capture** (create `Raw/Sessions/` + wiki pages) |
| Research findings worth preserving | **capture** (create `Raw/Papers/` + wiki pages) |
| Recurring review finding (class-level, not instance) | **capture** (create `Patterns/` page) |
| Question that was answered during work | **query** + **file-back** (run `gbrain query`, then write result to wiki page) |
| Daily digests accumulated without promotion | **sync** (`gbrain sync` then `gbrain embed --stale`) |
| Orphaned pages or broken links found | **extract** (`gbrain extract all`) + manual review |

The KB is not a mirror of repo-local docs. Only promote learnings that would
be useful in a different project or a future session with no repo context.

Read [references/harness-components.md](./references/harness-components.md)
component #15 for the full integration model.

### 8. Validate after every meaningful harness change

Run from the skill directory (paths relative to this skill's root):

```bash
# Validate the target repo's harness
python scripts/audit_harness.py <repo-path>

# Smoke-test scaffold generation in a temp directory
python scripts/bootstrap_harness.py <temp-repo> --project-name "Test Project"

# Verify internal consistency
python scripts/test_template_audit_contract.py
python scripts/test_skill_integrity.py
```

After bootstrap has installed scripts into the target repo, you can also run
`python scripts/audit_repo.py` from within the repo itself for ongoing checks.

Use a temp directory for scaffold tests so the skill proves it can create the
expected structure without damaging a live repository.

## Resources

### scripts/

- `bootstrap_harness.py`: scaffold the repository operating system from starter
  templates
- `audit_harness.py`: inspect a repository and report harness coverage and gaps
- `test_template_audit_contract.py`: verify that the packet template and audit
  script still agree
- `test_skill_integrity.py`: verify the skill's templates, references, and
  scripts are internally consistent

### references/

- `lifecycle-modes.md`: mode-specific execution checklist
- `adaptation-rules.md`: what to preserve, standardize, and infer
- `harness-components.md`: the full harness model across docs, tools, skills,
  subagents, checks, and runbooks
- `continuous-improvement.md`: how to encode repeated lessons back into the repo
- `implementation-phase-principles.md`: implementation-era development
  principles, rules, and enforcement hooks
- `first-principles-and-design-thinking.md`: full-cycle planning, development,
  review, release, and learning guidance
- `planning-process.md`: how work moves from backlog idea to approved work
  packet, including artifact decision tree and decomposition strategies
- `mechanical-enforcement.md`: the first mechanical enforcement layer for packet,
  scope, and CI checks
- `ci-stack-integration.md`: how to keep the universal harness job separate
  from stack-specific project CI
- `evidence-discipline.md`: how to structure and validate review-grade evidence
  bundles

### assets/

- `templates/`: starter files for `AGENTS.md`, `CLAUDE.md`, `research/`,
  `docs/engineering/`, and `.handoff/`