---
name: ai-agent-skill-registry-sync
description: Scan Peter's local AI agent skill directories across Codex, Hermes, Lark Agent, OpenClaw, SealSeek, and Claude Code, then update the LLM Wiki skill registry pages under /Users/pechen/wiki. Use when the user asks to find newly created skills, refresh the cross-agent skill registry, add agent skills to the wiki, check whether skill inventory is up to date, or make skills discoverable for future AI agents.
---

# AI Agent Skill Registry Sync

## Purpose

Keep the LLM Wiki's cross-agent skill registry in sync with skill files on disk, so any AI Agent can search the wiki before creating a duplicate skill.

The canonical daily-use wiki entry is:

`/Users/pechen/wiki/domains/ai-agent-engineering/90-Skill注册表/01-个人与项目Skill注册库.md`

The full registry is:

`/Users/pechen/wiki/domains/ai-agent-engineering/90-Skill注册表/02-跨Agent Skill注册库.md`

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

- Codex: `/Users/pechen/.codex/skills`
- Hermes: `/Users/pechen/.hermes/skills`
- Lark Agent: `/Users/pechen/.agents/skills`
- OpenClaw: `/Users/pechen/.openclaw/workspace/skills`
- SealSeek:
  - `/Users/pechen/.sealseek/skill_pool`
  - `/Users/pechen/.sealseek/workspace/skills`
  - `/Users/pechen/.sealseek/workspaces/default/skills`
  - `/Users/pechen/.sealseek/workspaces/default/active_skills`
  - `/Users/pechen/.sealseek/workspaces/default/customized_skills`
  - `/Users/pechen/.sealseek/backups`
  - `/Users/pechen/sealseek`
  - `/Users/pechen/hermes/xc-sealseek-aicoding-skill`
- Claude Code: `/Users/pechen/.claude/plugins/marketplaces/claude-plugins-official.bak`

The script excludes `node_modules`, `.venv`, `runtime`, and `__pycache__`.

It also excludes the hidden Codex source repo `.llmwiki-source` and the deprecated LLM Wiki standalone entries:

- `api-docs-wiki-ingest`
- `wiki-clippings-ingest`
- `book-to-llm-wiki`
- `course-transcript-to-knowledge`

Those capabilities are represented by `llm-wiki-ingest` adapters and should not be written as active registry entries.

## Output Pages

The script regenerates numeric Chinese registry pages under
`domains/ai-agent-engineering/90-Skill注册表/`:

- `01-个人与项目Skill注册库.md`
- `02-跨Agent Skill注册库.md`
- `03-Codex Skill注册页.md`
- `04-Hermes Skill注册页.md`
- `05-Lark Agent Skill注册页.md`
- `06-OpenClaw Skill注册页.md`
- `07-SealSeek Skill注册页.md`
- `08-Claude Code Skill注册页.md`

It also updates:

- `/Users/pechen/wiki/index.md`
- `/Users/pechen/wiki/domains/ai-agent-engineering/index.md`
- `/Users/pechen/wiki/log.md`

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
- Hermes skills are classified as personal/project only when they match Peter-specific project, ecommerce, visual, courseware, LLM Wiki, SealSeek/OpenClaw, Xicheng, Feishu, or similar customization signals.
