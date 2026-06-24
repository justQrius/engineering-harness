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

The harness integrates with the canonical KnowledgeBase repo at `D:/Projects/KnowledgeBase`, indexed by GBrain.
Operations (query, capture, sync, extract, stats) are available via the GBrain CLI
that any agent can invoke from any project directory:

```bash
gbrain query "question"          # Semantic search across KB
gbrain search "topic"            # Keyword search across KB
gbrain sync                     # Re-index pages from repo
gbrain embed --stale            # Embed unembedded chunks
gbrain extract all              # Extract links and timeline
gbrain stats                    # Show pages, chunks, embeddings
```

## Deployment

The skill lives in this repo and is deployed to platform skill directories:

- **Claude Code:** `~/.claude/skills/engineering-harness/`
- **Codex:** `~/.codex/skills/engineering-harness/`

Edit the source in this repo, then copy to the platform directory:

```bash
# macOS / Linux
cp -r * ~/.claude/skills/engineering-harness/
cp -r * ~/.codex/skills/engineering-harness/

# Windows (Git Bash)
cp -r * "$HOME/.claude/skills/engineering-harness/"
cp -r * "$HOME/.codex/skills/engineering-harness/"
```

## Adapting for Codex (OpenAI)

The skill works natively with Claude Code. To adapt it for Codex, address these
differences:

### Frontmatter constraints

Codex validates SKILL.md frontmatter more strictly than Claude Code:

| Field | Claude Code | Codex |
|-------|------------|-------|
| `name` | Any case, spaces allowed | Must match `^[a-z0-9-]+$` (lowercase, dashes only) |
| `description` | No hard limit | Max 1024 characters, no angle brackets |
| Other fields | `hooks`, `preamble-tier`, `allowed-tools` | Only `name`, `description`, `license`, `allowed-tools`, `metadata` |

The current `name: engineering-harness` and description (~650 chars) already meet
both platforms' constraints. No changes needed for frontmatter.

### SKILL.md length

Codex loads the entire SKILL.md into context. At 406 lines (~18KB), this is
large. If Codex struggles with the token budget, create a trimmed version:

1. Keep the Overview, Workflow, and Resources sections (the trigger and execution path)
2. Replace inline details with one-liner references to `references/` files
3. Target under 250 lines for the Codex version
4. Store as `SKILL.codex.md` and deploy that version to `~/.codex/skills/`

### Bash access

The harness scripts (`bootstrap_harness.py`, `audit_harness.py`) require Bash
execution and filesystem write access. Codex's sandbox may restrict:

- Writing files outside the project directory
- Running arbitrary Python scripts
- Creating directories recursively

If Codex can't run the scripts, the agent can still follow the SKILL.md workflow
manually — the scripts are a convenience, not a requirement. The workflow steps
(scaffold files, merge sections, audit coverage) can be done by hand.

### agents/openai.yaml

The `agents/openai.yaml` file configures Codex's UI:

```yaml
interface:
  display_name: "Engineering Harness"
  short_description: "Bootstrap and maintain an agent-ready engineering harness"
  default_prompt: "Use $engineering-harness to bootstrap, retrofit, or improve this repo's engineering harness for agents and human collaborators."
```

Codex reads this for skill discovery and display. The `$engineering-harness`
variable is replaced with the skill name at runtime.

### AGENTS.md vs CLAUDE.md

Both files serve the same purpose (agent instructions) for different audiences:

- **CLAUDE.md** — Loaded automatically by Claude Code at session start. Can
  include Claude-specific tool references and formatting.
- **AGENTS.md** — Loaded by Codex and other agents. Should avoid Claude-specific
  syntax and prefer universal formats (Bash commands, file paths, plain markdown).

The templates use universal syntax (Bash commands, Python script paths) so both
files work for any agent. When customizing for a specific repo, keep this
compatibility in mind.

## License

Private. All rights reserved.