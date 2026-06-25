---
name: ai-agent-skill-registry-sync
description: Scan the user's local AI agent skill directories across Codex, Hermes, Lark Agent, OpenClaw, SealSeek, and Claude Code, then update the LLM Wiki skill registry pages under $WIKI_ROOT. Use when the user asks to find newly created skills, refresh the cross-agent skill registry, add agent skills to the wiki, check whether skill inventory is up to date, or make skills discoverable for future AI agents.
---

# AI Agent Skill Registry Sync

## Purpose

Keep the LLM Wiki's cross-agent skill registry in sync with skill files on disk, so any AI Agent can search the wiki before creating a duplicate skill.

The canonical daily-use wiki entry is:

`$WIKI_ROOT/domains/AI Agent工程/90-Skill注册表/01-个人与项目Skill注册库.md`

The full registry is:

`$WIKI_ROOT/domains/AI Agent工程/90-Skill注册表/02-跨Agent Skill注册库.md`

## When To Use

Use this skill when the user asks to:

- scan for new skills created by AI agents
- update the wiki skill registry
- make Codex/Hermes/OpenClaw/SealSeek/Claude Code/Lark skills searchable
- check whether the current skill inventory is stale
- add newly created `SKILL.md` files into the LLM Wiki
- prepare for a query like “以前有没有做过类似的 skill?”

## Workflow

1. Run the sync script:

```bash
python3 <skill-root>/scripts/sync_skill_registry.py
```

2. Review the printed counts by agent and the list of touched wiki pages.
3. Spot-check likely new skills with `rg` against the generated pages.
4. Report:
   - total skill count
   - personal/project skill count
   - per-agent count
   - important new directories or newly visible skills
   - updated wiki page paths

## Dry Run

Before a risky change or when the user only asks to inspect:

```bash
python3 <skill-root>/scripts/sync_skill_registry.py --dry-run
```

## Scanned Sources

The script scans these roots:

- Codex: `$HOME/.codex/skills`
- Hermes: `$HOME/.hermes/skills`
- Lark Agent: `$HOME/.agents/skills`
- OpenClaw: `$HOME/.openclaw/workspace/skills`
- SealSeek:
  - `$HOME/.sealseek/skill_pool`
  - `$HOME/.sealseek/workspace/skills`
  - `$HOME/.sealseek/workspaces/default/skills`
  - `$HOME/.sealseek/workspaces/default/active_skills`
  - `$HOME/.sealseek/workspaces/default/customized_skills`
  - `$HOME/.sealseek/backups`
  - `$HOME/sealseek`
  - `$HOME/hermes/xc-sealseek-aicoding-skill`
- Claude Code: `$HOME/.claude/plugins/marketplaces/claude-plugins-official.bak`

The script excludes `node_modules`, `.venv`, `runtime`, and `__pycache__`.

It also excludes the hidden Codex source repo `.llmwiki-source` and the deprecated LLM Wiki standalone entries:

- `api-docs-wiki-ingest`
- `wiki-clippings-ingest`
- `book-to-llm-wiki`
- `course-transcript-to-knowledge`

Those capabilities are represented by `llm-wiki-ingest` adapters and should not be written as active registry entries.

## Output Pages

The script regenerates numeric Chinese registry pages under
`domains/AI Agent工程/90-Skill注册表/`:

- `01-个人与项目Skill注册库.md`
- `02-跨Agent Skill注册库.md`
- `03-Codex Skill注册页.md`
- `04-Hermes Skill注册页.md`
- `05-Lark Agent Skill注册页.md`
- `06-OpenClaw Skill注册页.md`
- `07-SealSeek Skill注册页.md`
- `08-Claude Code Skill注册页.md`

It also updates:

- `$WIKI_ROOT/index.md`
- `$WIKI_ROOT/domains/AI Agent工程/index.md`
- `$WIKI_ROOT/log.md`

## Registry Content Rules

Each skill entry must include:

- Agent / environment
- ownership classification: personal/project, system/builtin, runtime copy, archive/backup, or generic/uncertain
- source type
- capability category
- original `SKILL.md` file path
- retrieval-oriented capability description
- input / trigger hints
- search keywords

Do not write real API keys, cookies, tokens, customer secrets, or private credentials into the wiki.

## Ownership Rules

- Personal/project skills go into `01-个人与项目Skill注册库.md`.
- System/builtin skills remain only in the full registry.
- Runtime copies and backups remain only in the full registry.
- Hermes skills are classified as personal/project only when they match the user-specific project, ecommerce, visual, courseware, LLM Wiki, SealSeek/OpenClaw, Xicheng, Feishu, or similar customization signals.
