---
name: llm-wiki
description: "Karpathy's LLM Wiki — build and maintain a persistent, interlinked markdown knowledge base. Ingest sources, query compiled knowledge, and lint for consistency."
license: MIT
metadata:
  hermes:
    tags: [wiki, knowledge-base, research, notes, markdown, rag-alternative]
    category: research
    related_skills: [obsidian, arxiv, agentic-research-ideas]
    config:
      - key: wiki.path
        description: Path to the LLM Wiki knowledge base directory
        default: "~/wiki"
        prompt: Wiki directory path
---

# Karpathy's LLM Wiki

Build and maintain a persistent, compounding knowledge base as interlinked markdown files.
Based on [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

Unlike traditional RAG (which rediscovers knowledge from scratch per query), the wiki
compiles knowledge once and keeps it current. Cross-references are already there.
Contradictions have already been flagged. Synthesis reflects everything ingested.

**Division of labor:** The human curates sources and directs analysis. The agent
extracts all meaningful knowledge units, reconstructs and enriches them,
cross-references, files, and maintains consistency. Do not reduce ingestion to a
summary unless the user explicitly asks for a lightweight summary.

## When This Skill Activates

Use this skill when the user:
- Asks to create, build, or start a wiki or knowledge base
- Asks to ingest, add, or process a source into their wiki
- Asks a question and an existing wiki is present at the configured path
- Asks to lint, audit, or health-check their wiki
- References their wiki, knowledge base, or "notes" in a research context

For new source ingestion, delegate to `llm-wiki-ingest`. For compile/route/reason quality review, delegate to `llm-wiki-audit-and-optimization`.

## Wiki Location

Configured via `skills.config.wiki.path` in `~/.hermes/config.yaml` (prompted
during `hermes config migrate` or `hermes setup`):

```yaml
skills:
  config:
    wiki:
      path: ~/wiki
```

Falls back to `~/wiki` default. The resolved path is injected when this
skill loads — check the `[Skill config: ...]` block above for the active value.

The wiki is just a directory of markdown files — open it in Obsidian, VS Code, or
any editor. No database, no special tooling required.

## Architecture: Three Layers

## Architecture: Three Layers

```
wiki/
├── SCHEMA.md           # Conventions, structure rules, domain config
├── index.md            # Sectioned content catalog with one-line summaries
├── log.md              # Chronological action log (append-only, rotated yearly)
├── raw/                # Layer 1: Immutable source material
│   ├── articles/       # Web articles, clippings
│   ├── papers/         # PDFs, arxiv papers
│   ├── transcripts/    # Meeting notes, interviews
│   └── assets/         # Images, diagrams referenced by sources
├── entities/           # Layer 2: Entity pages (people, orgs, products, models)
├── concepts/           # Layer 2: Concept/topic pages
├── comparisons/        # Layer 2: Side-by-side analyses
└── queries/            # Layer 2: Filed query results worth keeping
```

**Layer 1 — Raw Sources:** Immutable. The agent reads but never modifies these.
**Layer 2 — The Wiki:** Agent-owned markdown files. Created, updated, and
cross-referenced by the agent.
**Layer 3 — The Schema:** `SCHEMA.md` defines structure, conventions, and tag taxonomy.

## Memory-First Principle

The wiki owner's LLM Wiki is a personal memory system, not a source archive and not a
course catalog. New knowledge should be classified by what it is about and how it
will be reused, not by how it was acquired.

When adding or reorganizing knowledge:

- Prefer content-domain placement over acquisition-path placement. A course,
  book, meeting, transcript, or clipping is a source package; it is not normally
  the final home for the formal knowledge.
- Before creating new formal pages, search existing pages and decide whether the
  new material should merge into, extend, challenge, or split an existing page.
- Treat related sources as human memory would: use later material to confirm,
  refine, enrich, or revise earlier theory instead of piling up parallel notes.
- Preserve old knowledge structures when they still have value. Use associative
  links, "related memory" sections, and source/package indexes before doing a
  destructive merge.
- Ask the user for confirmation when classification or merge choices are ambiguous,
  especially for broad domains such as ecommerce operations, tax/finance,
  brand, visual production, AI application development, and personal interests.
- Use Chinese human-facing titles and index labels by default. English slugs may
  remain as metadata, aliases, or transitional paths, but user navigation should
  be Chinese-readable.
- Top-level human-facing domain directories under `domains/` should also be
  Chinese-readable by default, e.g. `domains/AI Agent工程/` or
  `domains/财税与经营财务/`. Keep English slugs only as aliases, tags, or
  metadata when they are useful for search or compatibility.
- Use numeric prefixes on human-facing domain folders and formal knowledge
  pages when reading order matters, e.g. `01-电商财税合规/` and
  `03-增值税进销项与发票管理.md`. The prefix should express the intended
  learning/navigation order; the title after the prefix should remain
  Chinese-readable.

### Optional architecture: One Vault, Multiple Domains

For users with several related but mostly distinct knowledge areas, prefer a
single vault with domain subtrees before splitting into multiple vaults. This is
especially useful when the same concepts support several workstreams (for
example business operations, visual production, and brand strategy).

```
wiki/
├── AGENTS.md           # Cross-agent operating protocol (Codex/OpenClaw/etc.)
├── SCHEMA.md
├── index.md
├── log.md
├── inbox/              # Web Clipper and temporary inputs; not a final home
├── raw/                # Immutable sources
├── domains/            # Long-lived professional knowledge domains
│   ├── 电商运营/
│   ├── 视觉制作/
│   └── 品牌策略/
├── shared/             # Cross-domain concepts, frameworks, rules, workflows
├── projects/           # Project-specific context and decisions
├── entities/
├── comparisons/
├── queries/
├── decisions/
└── _meta/
```

Placement rule:
- `domains/` = long-lived professional capability or reusable domain method.
- `shared/` = concepts used across multiple domains; avoid duplicate pages.
- `projects/` = concrete project/client/product context.
- `inbox/` = entry point for clips and rough notes; later ingest into formal pages.
- `raw/` = source-of-truth copies; never edit.
- `source-packages/`, `course-packages/`, or a Chinese equivalent such as
  `课程包/` may hold source-oriented maps and audit trails, but the durable
  knowledge should still live in content-domain pages.

Do not split into multiple vaults early unless one domain is large enough to
need independent permissions, tooling, or maintainers. A single vault keeps
cross-links, agent orientation, `index.md`, `log.md`, and Git history simpler.
```
wiki/
├── AGENTS.md           # Cross-agent operating protocol (Codex/OpenClaw/etc.)
├── CLAUDE.md           # Thin pointer to AGENTS.md for Claude Code
├── HERMES.md           # Thin pointer/supplement for Hermes
├── OPENCLAW.md         # Thin pointer/supplement for OpenClaw
├── SEALSEEK.md         # Thin pointer/supplement for SealSeek
├── SCHEMA.md
├── index.md
├── log.md
├── inbox/              # Web Clipper and temporary notes before ingest
├── raw/                # Immutable source material
├── domains/            # Long-lived professional domains
│   ├── 电商运营/
│   ├── 视觉制作/
│   └── 品牌策略/
├── shared/             # Cross-domain concepts and workflows
│   ├── consumer-psychology/
│   ├── platform-rules/
│   ├── ai-agent-workflows/
│   └── knowledge-management/
├── projects/           # Project-specific context
├── entities/
├── comparisons/
├── queries/
├── decisions/
└── _meta/
```

Use one vault when domains overlap conceptually (e.g. ecommerce operations,
visual production, and brand strategy share consumer psychology, platform rules,
main-image CTR, positioning, and selling-point extraction). Split into separate
vaults only after a domain is very large, independently maintained, and cross-links
are no longer central. This avoids duplicate concepts, divergent schemas, and
confusion about which vault an agent should use.

**Layer 1 — Raw Sources:** Immutable. The agent reads but never modifies these.
**Layer 2 — The Wiki:** Agent-owned markdown files. Created, updated, and
cross-referenced by the agent. In multi-domain wikis, place long-lived domain
knowledge in `domains/`, cross-domain foundations in `shared/`, and concrete
project context in `projects/`.
**Layer 3 — The Schema/Protocol:** `SCHEMA.md` defines structure, conventions,
and tag taxonomy. `AGENTS.md` is the shared operating protocol for all agents; tool-specific
files should point to it rather than duplicate rules.

## Resuming an Existing Wiki (CRITICAL — do this every session)

When the user has an existing wiki, **always orient yourself before doing anything**:

① **Read `SCHEMA.md`** — understand the domain, conventions, and tag taxonomy.
② **Read `index.md`** — learn what pages exist and their summaries.
③ **Scan recent `log.md`** — read the last 20-30 entries to understand recent activity.

```bash
WIKI="${wiki_path:-$HOME/wiki}"
# Orientation reads at session start
read_file "$WIKI/SCHEMA.md"
read_file "$WIKI/index.md"
read_file "$WIKI/log.md" offset=<last 30 lines>
```

Only after orientation should you ingest, query, or lint. This prevents:
- Creating duplicate pages for entities that already exist
- Missing cross-references to existing content
- Contradicting the schema's conventions
- Repeating work already logged

For large wikis (100+ pages), also run a quick `search_files` for the topic
at hand before creating anything new.

## Query Pack Mode

When answering a user question from an existing wiki, do not simply read a user-provided directory and answer from the first matching files. Build a query pack first.

Use the protocol in the source repo when available:

```bash
python3 $LLMWIKI_SKILL_SOURCE/shared/scripts/wiki_cli_search.py "<user question>"
```

If the script is unavailable, manually follow the same order:

1. Search `queries/` for a task-specific entry page.
2. Search for `Agent 使用模板` or `agent-usage-template`.
3. Search domain, project, and learning-path indexes.
4. Search concept/playbook/detail pages.
5. Expand promising pages with outgoing links, backlinks, and outline when Obsidian CLI is available.

Preferred read order:

```text
queries/ -> Agent usage templates -> domain/project/learning-path indexes -> playbooks/concepts -> detailed chapters
```

The answer should be grounded in the selected query pack. If no query/template/index route exists for a recurring task, mention that as a route gap and consider creating a query page or Agent usage template.

## Initializing a New Wiki

When the user asks to create or start a wiki:

1. Determine the wiki path from config, `WIKI_ROOT`, or the user's explicit path; use `~/wiki` only as the generic home-directory default.
2. Create the directory structure above
3. Ask the user what domain the wiki covers — be specific
4. Write `SCHEMA.md` customized to the domain (see template below)
5. Write initial `index.md` with sectioned header
6. Write initial `log.md` with creation entry
7. Confirm the wiki is ready and suggest first sources to ingest

### SCHEMA.md Template

Adapt to the user's domain. The schema constrains agent behavior and ensures consistency:

```markdown
# Wiki Schema

## Domain
[What this wiki covers — e.g., "AI/ML research", "personal health", "startup intelligence"]

## Conventions
- File names: lowercase, hyphens, no spaces (e.g., `transformer-architecture.md`)
- Every wiki page starts with YAML frontmatter (see below)
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page)
- When updating a page, always bump the `updated` date
- Every new page must be added to `index.md` under the correct section
- Every action must be appended to `log.md`

## Frontmatter
  ```yaml
  ---
  title: Page Title
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
  type: entity | concept | comparison | query | summary
  tags: [from taxonomy below]
  sources: [raw/articles/source-name.md]
  ---
  ```

## Tag Taxonomy
[Define 10-20 top-level tags for the domain. Add new tags here BEFORE using them.]

Example for AI/ML:
- Models: model, architecture, benchmark, training
- People/Orgs: person, company, lab, open-source
- Techniques: optimization, fine-tuning, inference, alignment, data
- Meta: comparison, timeline, controversy, prediction

Rule: every tag on a page must appear in this taxonomy. If a new tag is needed,
add it here first, then use it. This prevents tag sprawl.

## Page Thresholds
- **Create a page** when an entity/concept appears in 2+ sources OR is central to one source
- **Add to existing page** when a source mentions something already covered
- **DON'T create a page** for passing mentions, minor details, or things outside the domain
- **Split a page** when it exceeds ~200 lines — break into sub-topics with cross-links
- **Archive a page** when its content is fully superseded — move to `_archive/`, remove from index

## Entity Pages
One page per notable entity. Include:
- Overview / what it is
- Key facts and dates
- Relationships to other entities ([[wikilinks]])
- Source references

## Concept Pages
One page per concept or topic. Include:
- Definition / explanation
- Current state of knowledge
- Open questions or debates
- Related concepts ([[wikilinks]])

## Comparison Pages
Side-by-side analyses. Include:
- What is being compared and why
- Dimensions of comparison (table format preferred)
- Verdict or synthesis
- Sources

## Update Policy
When new information conflicts with existing content:
1. Check the dates — newer sources generally supersede older ones
2. If genuinely contradictory, note both positions with dates and sources
3. Mark the contradiction in frontmatter: `contradictions: [page-name]`
4. Flag for user review in the lint report
```

### index.md Template

The index is sectioned by type. Each entry is one line: wikilink + summary.

```markdown
# Wiki Index

> Content catalog. Every wiki page listed under its type with a one-line summary.
> Read this first to find relevant pages for any query.
> Last updated: YYYY-MM-DD | Total pages: N

## Entities
<!-- Alphabetical within section -->

## Concepts

## Comparisons

## Queries
```

**Scaling rule:** When any section exceeds 50 entries, split it into sub-sections
by first letter or sub-domain. When the index exceeds 200 entries total, create
a `_meta/topic-map.md` that groups pages by theme for faster navigation.

### log.md Template

```markdown
# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: ingest, update, query, lint, create, archive, delete
> When this file exceeds 500 entries, rotate: rename to log-YYYY.md, start fresh.

## [YYYY-MM-DD] create | Wiki initialized
- Domain: [domain]
- Structure created with SCHEMA.md, index.md, log.md
```

## Core Operations

### 1. Ingest

When the user provides a source (URL, file, paste), integrate it into the wiki:

① **Capture the raw source:**
   - URL → use `web_extract` to get markdown, save to `raw/articles/`
   - PDF → use `web_extract` (handles PDFs), save to `raw/papers/`
   - Pasted text → save to appropriate `raw/` subdirectory
   - Name the file descriptively: `raw/articles/karpathy-llm-wiki-2026.md`

② **Discuss takeaways** with the user — what's interesting, what matters for
   the domain. (Skip this in automated/cron contexts — proceed directly.)

③ **Check what already exists** — search index.md and use `search_files` to find
   existing pages for mentioned entities/concepts. This is the difference between
   a growing wiki and a pile of duplicates.

④ **Write or update wiki pages:**
   - **New entities/concepts:** Create pages only if they meet the Page Thresholds
     in SCHEMA.md (2+ source mentions, or central to one source)
   - **Existing pages:** Add new information, update facts, bump `updated` date.
     When new info contradicts existing content, follow the Update Policy.
   - **Cross-reference:** Every new or updated page must link to at least 2 other
     pages via `[[wikilinks]]`. Check that existing pages link back.
   - **Tags:** Only use tags from the taxonomy in SCHEMA.md

⑤ **Update navigation:**
   - Add new pages to `index.md` under the correct section, alphabetically
   - Update the "Total pages" count and "Last updated" date in index header
   - Append to `log.md`: `## [YYYY-MM-DD] ingest | Source Title`
   - List every file created or updated in the log entry

⑥ **Report what changed** — list every file created or updated to the user.

A single source can trigger updates across 5-15 wiki pages. This is normal
and desired — it's the compounding effect.

### 2. Query

When the user asks a question about the wiki's domain:

① **Read `index.md`** to identify relevant pages.
② **For wikis with 100+ pages**, also `search_files` across all `.md` files
   for key terms — the index alone may miss relevant content.
③ **Read the relevant pages** using `read_file`.
④ **Synthesize an answer** from the compiled knowledge. Cite the wiki pages
   you drew from: "Based on [[page-a]] and [[page-b]]..."
⑤ **File valuable answers back** — if the answer is a substantial comparison,
   deep dive, or novel synthesis, create a page in `queries/` or `comparisons/`.
   Don't file trivial lookups — only answers that would be painful to re-derive.
⑥ **Update log.md** with the query and whether it was filed.

### 3. Lint

When the user asks to lint, health-check, or audit the wiki:

① **Orphan pages:** Find pages with no inbound `[[wikilinks]]` from other pages.
```python
# Use execute_code for this — programmatic scan across all wiki pages
import os, re
from collections import defaultdict
wiki = "<WIKI_PATH>"
# Scan all .md files in entities/, concepts/, comparisons/, queries/
# Extract all [[wikilinks]] — build inbound link map
# Pages with zero inbound links are orphans
```

② **Broken wikilinks:** Find `[[links]]` that point to pages that don't exist.

③ **Index completeness:** Every wiki page should appear in `index.md`. Compare
   the filesystem against index entries.

④ **Frontmatter validation:** Every wiki page must have all required fields
   (title, created, updated, type, tags, sources). Tags must be in the taxonomy.

⑤ **Stale content:** Pages whose `updated` date is >90 days older than the most
   recent source that mentions the same entities.

⑥ **Contradictions:** Pages on the same topic with conflicting claims. Look for
   pages that share tags/entities but state different facts.

⑦ **Page size:** Flag pages over 200 lines — candidates for splitting.

⑧ **Tag audit:** List all tags in use, flag any not in the SCHEMA.md taxonomy.

⑨ **Log rotation:** If log.md exceeds 500 entries, rotate it.

⑩ **Report findings** with specific file paths and suggested actions, grouped by
   severity (broken links > orphans > stale content > style issues).

⑪ **Append to log.md:** `## [YYYY-MM-DD] lint | N issues found`

## Working with the Wiki

### Git / GitHub sync for multi-agent wikis

When a wiki is used by multiple agents or devices, treat it like a private Git
repository:

1. Initialize or verify the local repo in the wiki directory.
2. Add a private remote such as `git@github.com:<user>/wiki.git`.
3. Ignore local editor state; for Obsidian, use at least:
   ```gitignore
   .obsidian/
   .DS_Store
   *.tmp
   *.temp
   ```
4. Before ingesting, run `git pull --ff-only` and check `git status`.
5. After ingest/lint/update verification, commit with a descriptive message and
   push, e.g. `git commit -m "ingest marketing theory for ecommerce images"`.

Prefer private repositories. LLM wikis often contain project context, customer
examples, internal business rules, agent setup notes, and commercial judgments.
Do not push secrets, tokens, or raw sensitive datasets.

### Ingesting long source documents

For long source markdown files, do not simply move the whole file into the formal
wiki layer and do not compress it into key takeaways. Use this pattern:

1. Copy the untouched source into `raw/articles/` or the correct raw subfolder.
2. Build a coverage checklist for headings, tables, examples, code, formulas,
   cases, images-with-information, definitions, caveats, and operational steps.
3. Create formal page(s) in the best location (`shared/` for cross-domain
   frameworks, `domains/` for domain-specific methods, `projects/` for project
   context). Use as many pages as needed for complete coverage without creating
   thin fragments.
4. Link each formal page back to the raw source in frontmatter `sources:`.
5. Update relevant domain/project index pages to point to the compiled knowledge.
6. Add a "coverage notes" or "omission audit" section/file listing source units
   represented, intentionally raw-only, or unresolved.
7. Verify wikilinks, update main `index.md`, append `log.md`, then commit/push if
   the wiki is Git-backed.

This keeps raw provenance intact while making the knowledge quickly searchable
and usable by agents. Formal output may be longer than a source summary because
it should include interpretation, relationship maps, decision rules, examples,
and Agent-usable templates.

### Searching

```bash
# Find pages by content
search_files "transformer" path="$WIKI" file_glob="*.md"

# Find pages by filename
search_files "*.md" target="files" path="$WIKI"

# Find pages by tag
search_files "tags:.*alignment" path="$WIKI" file_glob="*.md"

# Recent activity
read_file "$WIKI/log.md" offset=<last 20 lines>
```

### Bulk Ingest

When ingesting multiple sources at once, batch the updates:
1. Read all sources first
2. Identify all entities and concepts across all sources
3. Check existing pages for all of them (one search pass, not N)
4. Create/update pages in one pass (avoids redundant updates)
5. Update index.md once at the end
6. Write a single log entry covering the batch

### Archiving

When content is fully superseded or the domain scope changes:
1. Create `_archive/` directory if it doesn't exist
2. Move the page to `_archive/` with its original path (e.g., `_archive/entities/old-page.md`)
3. Remove from `index.md`
4. Update any pages that linked to it — replace wikilink with plain text + "(archived)"
5. Log the archive action

### Obsidian Integration

The wiki directory works as an Obsidian vault out of the box:
- `[[wikilinks]]` render as clickable links
- Graph View visualizes the knowledge network
- YAML frontmatter powers Dataview queries
- The `raw/assets/` folder holds images referenced via `![[image.png]]`

For best results:
- Set Obsidian's attachment folder to `raw/assets/`
- Enable "Wikilinks" in Obsidian settings (usually on by default)
- Install Dataview plugin for queries like `TABLE tags FROM "entities" WHERE contains(tags, "company")`

If using the Obsidian skill alongside this one, set `OBSIDIAN_VAULT_PATH` to the
same directory as the wiki path.

### Obsidian Headless (servers and headless machines)

On machines without a display, use `obsidian-headless` instead of the desktop app.
It syncs vaults via Obsidian Sync without a GUI — perfect for agents running on
servers that write to the wiki while Obsidian desktop reads it on another device.

**Setup:**
```bash
# Requires Node.js 22+
npm install -g obsidian-headless

# Login (requires Obsidian account with Sync subscription)
ob login --email <email> --password '<password>'

# Create a remote vault for the wiki
ob sync-create-remote --name "LLM Wiki"

# Connect the wiki directory to the vault
cd "$WIKI_ROOT"
ob sync-setup --vault "<vault-id>"

# Initial sync
ob sync

# Continuous sync (foreground — use systemd for background)
ob sync --continuous
```

**Continuous background sync via systemd:**
```ini
# ~/.config/systemd/user/obsidian-wiki-sync.service
[Unit]
Description=Obsidian LLM Wiki Sync
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/path/to/ob sync --continuous
WorkingDirectory=<absolute path to WIKI_ROOT>
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now obsidian-wiki-sync
# Enable linger so sync survives logout:
sudo loginctl enable-linger $USER
```

This lets the agent write to `$WIKI_ROOT` on a server while you browse the same
vault in Obsidian on your laptop/phone — changes appear within seconds.

## Pitfalls

- **Never modify files in `raw/`** — sources are immutable. Corrections go in wiki pages.
- **Always orient first** — read SCHEMA + index + recent log before any operation in a new session.
  Skipping this causes duplicates and missed cross-references.
- **Always update index.md and log.md** — skipping this makes the wiki degrade. These are the
  navigational backbone.
- **Don't create pages for passing mentions** — follow the Page Thresholds in SCHEMA.md. A name
  appearing once in a footnote doesn't warrant an entity page.
- **Don't create pages without cross-references** — isolated pages are invisible. Every page must
  link to at least 2 other pages.
- **Frontmatter is required** — it enables search, filtering, and staleness detection.
- **Tags must come from the taxonomy** — freeform tags decay into noise. Add new tags to SCHEMA.md
  first, then use them.
- **Keep pages scannable** — a wiki page should be readable in 30 seconds. Split pages over
  200 lines. Move detailed analysis to dedicated deep-dive pages.
- **Ask before mass-updating** — if an ingest would touch 10+ existing pages, confirm
  the scope with the user first.
- **Rotate the log** — when log.md exceeds 500 entries, rename it `log-YYYY.md` and start fresh.
  The agent should check log size during lint.
- **Handle contradictions explicitly** — don't silently overwrite. Note both claims with dates,
  mark in frontmatter, flag for user review.
