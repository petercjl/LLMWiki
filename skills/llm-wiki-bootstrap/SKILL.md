---
name: llm-wiki-bootstrap
description: Initialize a cross-platform LLM Wiki knowledge base for a new user or machine. Use when the user wants to create or set up an LLM Wiki from scratch, configure WIKI_ROOT and related environment variables, prepare Obsidian App and Obsidian CLI access, create the initial domains/index/schema/log structure, or verify that a local LLM Wiki environment is ready on macOS, Windows, or Linux.
---

# LLM Wiki Bootstrap

## Mission

Create a usable LLM Wiki system on a user's machine, starting from an empty or partially configured environment. The main line is: detect environment, agree on configuration, create the wiki skeleton, connect Obsidian when possible, verify the result, and hand off to `llm-wiki-ingest`.

This skill must support macOS, Windows, and Linux. Never assume Homebrew, zsh, Unix paths, or an existing Obsidian vault.

## Main Flow

1. Identify the operating system and shell context.
2. Detect required tools with `scripts/bootstrap_llm_wiki.py --check-only`.
3. Explain missing prerequisites and attempt safe installation only when the package manager is obvious and user consent is available.
4. Propose configuration values, especially `WIKI_ROOT` and `LLMWIKI_SKILL_SOURCE`.
5. Ask the user to confirm or adjust the wiki path and initial knowledge domains.
6. Run `scripts/bootstrap_llm_wiki.py` with the confirmed values.
7. Review the generated summary, degraded capabilities, and next actions.
8. Verify with filesystem checks, Git status, and Obsidian CLI checks when available.

If a branch fails, fix the branch and return to the next main-flow step. Do not turn this skill into a general package manager or Obsidian support workflow.

## Tool Node

Use the bootstrap script for deterministic work:

```bash
python3 <skill-dir>/scripts/bootstrap_llm_wiki.py --check-only
python3 <skill-dir>/scripts/bootstrap_llm_wiki.py --wiki-root "$WIKI_ROOT" --domain "AI Agent工程" --domain "业务与运营"
```

On Windows, use `py -3` or `python` if `python3` is unavailable:

```powershell
py -3 <skill-dir>\scripts\bootstrap_llm_wiki.py --check-only
py -3 <skill-dir>\scripts\bootstrap_llm_wiki.py --wiki-root "$env:USERPROFILE\wiki" --domain "AI Agent工程"
```

The script creates files but does not edit shell profiles automatically. If the user wants persistent environment loading, show the platform-specific snippet from the script output and ask before changing profile files.

## Configuration Contract

Prefer a per-user config file:

- macOS/Linux: `~/.llmwiki/config.env`
- Windows PowerShell: `%USERPROFILE%\.llmwiki\config.ps1`
- Windows cmd: `%USERPROFILE%\.llmwiki\config.cmd`

Core variables:

- `WIKI_ROOT`: target LLM Wiki vault directory. Default: `~/wiki`.
- `LLMWIKI_SKILL_SOURCE`: local source checkout for shared scripts and skills when available.
- `CODEX_SKILLS_DIR`, `HERMES_SKILLS_DIR`, `LARK_AGENT_SKILLS_DIR`, `OPENCLAW_SKILLS_DIR`, `CLAUDE_CODE_SKILLS_DIR`: optional directories used by registry sync.

When variables are unset, existing LLM Wiki skills should fall back to user-home defaults. The config file improves portability; it is not a hard requirement for basic operation.

## Cross-Platform Rules

Read `references/cross-platform-notes.md` when tools are missing, installation is requested, or the user is on Windows/Linux.

- macOS: detect Obsidian at `/Applications/Obsidian.app` and common Homebrew paths. Install only after confirmation, usually with `brew install --cask obsidian` and the selected Obsidian CLI package if available.
- Windows: detect Obsidian in `Program Files` and `%LOCALAPPDATA%`. Prefer `winget` when available. Use PowerShell snippets and semicolon-safe paths. Do not write Unix `export` lines into Windows profiles.
- Linux: detect `obsidian`, Flatpak, Snap, AppImage-style paths, and common package managers. Installation varies by distribution; ask before using `flatpak`, `snap`, `apt`, `dnf`, or `pacman`.

Obsidian App and CLI are required for full route auditing. If either cannot be installed, finish filesystem initialization and mark the setup as degraded.

## Wiki Skeleton

The initial wiki should include:

- `AGENTS.md`: local operating rules for agents.
- `SCHEMA.md`: frontmatter and page-type contract.
- `index.md`: top-level navigation.
- `log.md`: change log.
- `domains/<domain>/index.md`: one Chinese index page per confirmed domain.
- `raw/`, `raw/transcripts/`, `_meta/`, `_meta/extraction-notes/`, `_meta/templates/`, `Clippings/`, `queries/`.

Default domains when the user has no preference:

- `AI Agent工程`
- `业务与运营`
- `产品与工具`
- `研究与阅读`
- `项目复盘`
- `个人方法论`

Tell the user these are starting points. Future ingest runs may add, split, or merge domains.

## Safety

- Never overwrite an existing non-empty wiki root without explicit confirmation.
- If `index.md`, `SCHEMA.md`, or `AGENTS.md` already exists, update only when the user confirms.
- Initialize Git when absent. Do not commit unless the user asked for a committed bootstrap or the setup is clearly a new empty repo.
- Do not install software silently. Package installs and shell profile edits need explicit user confirmation.
- Keep generated config generic. Do not include local personal names or machine-specific absolute paths except the current user's chosen paths.

## QA

After bootstrap, verify:

- config files exist and contain the selected variables.
- `WIKI_ROOT` exists with the required directories.
- `AGENTS.md`, `SCHEMA.md`, `index.md`, and `log.md` exist.
- every requested domain has `domains/<domain>/index.md`.
- Git status is understandable.
- Obsidian CLI can report the target vault or the setup summary clearly marks degraded mode.
- The final response lists exact paths, installed/missing tools, and next commands for the user's OS.

## Patch Area

- If Python is missing, do not attempt bootstrap with shell-only fragments. Tell the user Python 3 is required and provide platform-specific installation options.
- If the user is on Windows and paths contain spaces, quote every path in examples and prefer PowerShell over cmd.
- If Obsidian App is installed but CLI is missing, create the wiki and config anyway, then mark route audit unavailable until CLI is installed.
