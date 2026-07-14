---
name: llm-wiki-bootstrap
description: Initialize a cross-platform LLM Wiki knowledge base for a new user or machine. Use when the user wants to create or set up an LLM Wiki from scratch, configure WIKI_ROOT, prepare Obsidian App and its bundled CLI, install the media/OCR tools needed by wiki ingestion, create the initial domains/index/schema/log structure, or verify readiness on macOS, Windows, or Linux.
---

# LLM Wiki Bootstrap

## Mission

Create a usable LLM Wiki from an empty or partially configured machine. The main line is: inspect the real environment, agree on the wiki path and starter domains, prepare the required toolchain, create the skeleton, let the user open it as an Obsidian vault, verify the bundled CLI, then hand off to normal ingestion.

Support macOS, Windows, and Linux. Never assume a shell, package manager, CPU architecture, path, or existing vault.

## Main Flow

1. Identify the operating system, native system architecture, SealSeek/Node process architecture, checker/Python architecture, shell, PATH, and independent tool installations. On Windows, `node -p "process.arch"` is a safe single-purpose check for SealSeek's Node process; do not mix CMD `if` syntax into PowerShell.
2. Run `scripts/bootstrap_llm_wiki.py --check-only` and read its complete JSON result.
   Use this script as the primary inventory. Do not repeat its checks with long improvised shell chains unless one specific result needs confirmation.
   In check-only output, `config_paths` and `config` are proposed bootstrap values. Report a configuration as existing only when `current_state.existing_config_paths` contains it; report the Wiki as existing only when `current_state.wiki_root_exists` is true.
3. Read `references/toolchain-install.md` whenever a required tool is missing or installation is requested. Distinguish the core profile from the media-ingestion profile.
4. Explain what is already usable, what is missing, where each missing item will come from, and whether it changes PATH or a profile. Ask for confirmation before installing anything.
5. Install only the confirmed items. Prefer a verified domestic mirror or a course-controlled mirror. Never silently fall back to GitHub or another upstream source after a mirror failure.
6. Re-run the check. Do not treat an emulated process architecture as the native system architecture. Do not install a duplicate runtime when an independent usable copy already exists.
7. Confirm the wiki path and starter domains. The user edits each value only once. Defaults are `~/wiki` and the domains listed below.
8. Ensure the target is absent or empty and is not nested inside another Obsidian vault. Stop on a conflict unless the user explicitly approves an override.
9. Run the bootstrap script with the confirmed values. Git is optional and is not initialized by default.
10. Ask the user to open Obsidian and choose **Open folder as vault**, selecting the newly created wiki directory. Do not edit Obsidian's private `obsidian.json` registry and do not guess a vault ID.
11. If Obsidian 1.12.7 or later is installed, first test its bundled CLI. If it works, continue. If it does not, ask the user to enable **Settings → General → Advanced → Command line interface**, then open a new terminal and test again. Obsidian must be running during CLI commands.
12. Verify the filesystem skeleton, toolchain, active vault route, and next action. If a branch fails, fix that branch and return to the next main-flow step.
13. After confirmation, add a short routing rule to the active SealSeek workspace `AGENTS.md`: this is the only formal Wiki; ordinary requests such as “做成知识库” or “加入 Wiki” should automatically use the installed Wiki Skills and their complete SOP; missing required tools must be installed from a trusted source after confirmation instead of bypassing the step. Do not require the learner to remember Skill names.

## Tool Node

Use the script for deterministic inspection and file creation:

```bash
python3 <skill-dir>/scripts/bootstrap_llm_wiki.py --check-only
python3 <skill-dir>/scripts/bootstrap_llm_wiki.py \
  --wiki-root "$WIKI_ROOT" \
  --domain "财税与经营财务" \
  --domain "电商运营" \
  --domain "品牌策略" \
  --domain "视觉制作"
```

On Windows use `py -3` or `python` when `python3` is unavailable:

```powershell
py -3 <skill-dir>\scripts\bootstrap_llm_wiki.py --check-only
py -3 <skill-dir>\scripts\bootstrap_llm_wiki.py --wiki-root "$env:USERPROFILE\wiki" --domain "电商运营"
```

For a smoke test, pass both a temporary wiki root and temporary config path:

```bash
python3 <skill-dir>/scripts/bootstrap_llm_wiki.py \
  --wiki-root "/tmp/llm-wiki-test/wiki" \
  --config-path "/tmp/llm-wiki-test/config.env" \
  --domain "测试领域" \
  --dry-run \
  --json
```

The script creates files but does not install packages, edit shell profiles, edit Obsidian's registry, or open a vault. Those are deliberate human-visible branches.

## Configuration Contract

Prefer a per-user config file:

- macOS/Linux: `~/.llmwiki/config.env`
- Windows PowerShell: `%USERPROFILE%\.llmwiki\config.ps1`
- Windows cmd: `%USERPROFILE%\.llmwiki\config.cmd`

Core variables:

- `WIKI_ROOT`: target vault. Default: `~/wiki`.
- `LLMWIKI_SKILL_SOURCE`: optional local checkout for shared scripts and skills.
- Agent-specific skill directory variables are optional and used only by registry synchronization.

Ask before adding config loading or tool paths to a profile. Prefer absolute executable paths for the current run before proposing a persistent PATH change.

## Wiki Skeleton

Create:

- `AGENTS.md`, `SCHEMA.md`, `index.md`, and `log.md`.
- `domains/<domain>/index.md` for each confirmed starter domain.
- `raw/`, `raw/transcripts/`, `_meta/`, `_meta/extraction-notes/`, `_meta/templates/`, `Clippings/`, and `queries/`.

Default ecommerce starter domains:

- `财税与经营财务`
- `电商运营`
- `品牌策略`
- `视觉制作`

These are starting points. Later ingest work may add, split, rename, or merge domains.

## Obsidian CLI Rules

Obsidian 1.12.7+ includes the official CLI. It is not a separate application to download.

- Windows: prefer `Obsidian.com` beside `Obsidian.exe`; after Obsidian registers the CLI and a new terminal is opened, `obsidian help` may also work.
- macOS: prefer `/Applications/Obsidian.app/Contents/MacOS/obsidian-cli`; after registration, `/usr/local/bin/obsidian` may work.
- Linux: use the launcher supplied by the installed package only after verifying `obsidian help`.

Verify with `obsidian help`, not `obsidian --help`. A valid command surface includes `backlinks`, `search`, and `vault`. Test the current route with `obsidian vault info=path`. The app must be running, and the active vault must resolve to `WIKI_ROOT` before route-dependent audit work is considered ready.

## Safety

- Never overwrite a non-empty wiki root without explicit confirmation.
- Never create a vault inside another vault without explicit confirmation.
- Never install software silently or replace a usable runtime merely to standardize versions.
- Never infer Windows native architecture only from Python, PowerShell, or another process architecture.
- Never hard-code a mutable release checksum. Obtain the checksum from the same trusted release manifest, pin the resolved version for the current run, verify it, and record both.
- Never use an unverified download mirror. If no trusted compatible artifact exists, report the gap and stop that installation branch.
- Git is optional. Initialize it only when the user asks for version control.
- Keep learner configuration generic; do not copy developer-only paths into it.

## QA

After bootstrap, verify:

- the selected config and wiki paths exist;
- all required directories and starter files exist;
- every requested domain has an index page;
- the real Obsidian registry file was not edited by the bootstrap script;
- the vault is visible because the user opened the folder in Obsidian;
- Obsidian CLI is either verified and routed to `WIKI_ROOT`, or the exact remaining user action is stated;
- core and media tool states are reported separately;
- FFmpeg includes `ffmpeg` and `ffprobe`;
- local ASR has both an executable and a usable model;
- Tesseract includes `chi_sim` and `eng`; ImageMagick is optional until preprocessing is needed;
- Git remains absent when it was not requested;
- the final response lists exact installed paths, versions, missing items, and the next normal ingestion action.

## Patch Area

- If Python 3 is missing, stop file initialization and follow the inspected platform branch in `references/toolchain-install.md`.
- If Obsidian exists but the CLI test fails, do not search for a separate CLI package. Ask the user to enable the built-in command line interface and open a new terminal.
- If the CLI works but reports a different vault, ask the user to open the intended vault in Obsidian, then retry.
- If a media tool is unavailable from a trusted compatible mirror, finish the core Wiki skeleton only and report media ingestion as not ready.
- If the request is only a check, do not install, create, register, or modify anything.
