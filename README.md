# Engineering Harness

Agent-ready engineering operating system for repositories. Bootstrap, retrofit,
operate, and continuously improve a development harness that makes AI coding
agents and human reviewers effective over the full project lifecycle.

## Quick Start

```bash
# Audit an existing repo
python scripts/audit_harness.py /path/to/repo

# Bootstrap into a new repo
python scripts/bootstrap_harness.py /path/to/repo --project-name "My Project"

# Retrofit into an existing repo (merges key sections into existing files)
python scripts/bootstrap_harness.py /path/to/repo --project-name "My Project" --mode retrofit

# Force overwrite existing files
python scripts/bootstrap_harness.py /path/to/repo --project-name "My Project" --force
```

## What It Installs

- `AGENTS.md` and `CLAUDE.md` — Agent collaboration contracts
- `docs/engineering/` — Development loop, planning process, doctrine
- `docs/planning/`, `docs/design/`, `docs/architecture/` — Layered decision docs
- `.handoff/` — Work packets, decisions, reviews, releases
- `research/` — Vision, landscape, open synthesis
- `scripts/` — Audit, scope checking, packet transitions, evidence validation

## Lifecycle Modes

| Mode | When |
|------|-------|
| `init` | Greenfield repo with little or no operating structure |
| `retrofit` | Existing repo with partial docs or inconsistent process |
| `operate` | Active repo using the harness, needs packet-driven work |
| `improve` | Repeated mistakes or drift should be encoded back into the harness |

## Repository Structure

```
engineering-harness/
├── SKILL.md                    # Skill definition (trigger, workflow, resources)
├── agents/
│   └── openai.yaml             # Codex UI config
├── assets/
│   └── templates/              # Starter files copied into target repos
│       ├── AGENTS.md           # Agent collaboration contract
│       ├── CLAUDE.md           # Claude Code specific instructions
│       ├── .handoff/           # Work packet templates
│       ├── docs/engineering/   # Doctrine docs
│       ├── docs/planning/      # Planning docs
│       ├── docs/design/        # Design docs
│       ├── docs/architecture/  # Architecture docs
│       ├── research/           # Research templates
│       ├── scripts/            # Repo-level automation scripts
│       └── Taskfile.yml        # Task runner for local checks
├── references/
│   ├── adaptation-rules.md     # What to preserve vs. standardize
│   ├── ci-stack-integration.md # Separating harness CI from project CI
│   ├── continuous-improvement.md # Autoresearch-adapted improvement loop
│   ├── evidence-discipline.md  # Review-grade evidence bundles
│   ├── first-principles-and-design-thinking.md # Full-cycle guidance
│   ├── harness-components.md   # Full component model
│   ├── implementation-phase-principles.md # Implementation-era rules
│   ├── lifecycle-modes.md      # Mode-specific checklists
│   ├── mechanical-enforcement.md # Machine-enforced checks
│   └── planning-process.md     # Backlog to approved packet flow
└── scripts/
    ├── audit_harness.py         # Inspect repo harness coverage and gaps
    ├── bootstrap_harness.py     # Scaffold from templates, merge in retrofit
    ├── test_skill_integrity.py   # Verify skill internal consistency
    └── test_template_audit_contract.py # Verify template-audit agreement
```

## Retrofit Mode

When bootstrapping into an existing repo (`--mode retrofit`, the default), the
script:

1. **Scaffolds missing files** — creates only what doesn't exist yet
2. **Merges key sections** — appends "Cross-Project Knowledge Base" section to
   existing `CLAUDE.md`/`AGENTS.md` if they lack it
3. **Upgrades inline references** — replaces `/kb` slash commands with
   operation names and script paths that work from any agent
4. **Idempotent** — running twice produces the same result; already-present
   sections and already-upgraded references are skipped

## Cross-Project Knowledge Base

The harness integrates with a central Knowledge Base at `D:\Projects\KnowledgeBase`.
Operations (query, capture, compile, lint, status) are available via Python scripts
that any agent can invoke from any project directory:

```bash
python D:\Projects\KnowledgeBase\skill\scripts\kb-query.py "topic" --log
python D:\Projects\KnowledgeBase\skill\scripts\kb-compile.py --dry-run
python D:\Projects\KnowledgeBase\skill\scripts\kb-lint.py --check all
python D:\Projects\KnowledgeBase\skill\scripts\kb-status.py
```

## Deployment

The skill lives in this repo and is deployed to both Claude Code and Codex:

- **Claude Code:** `~/.claude/skills/engineering-harness/`
- **Codex:** `~/.codex/skills/engineering-harness/`

Edit the source in this repo, then copy to both platform directories.

## License

Private. All rights reserved.