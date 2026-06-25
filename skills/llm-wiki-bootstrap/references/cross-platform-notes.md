# Cross-Platform Notes

Use this reference when `llm-wiki-bootstrap` runs on Windows/Linux or when any required tool is missing.

## Environment Loading

macOS/Linux:

```bash
source "$HOME/.llmwiki/config.env"
```

PowerShell:

```powershell
. "$env:USERPROFILE\.llmwiki\config.ps1"
```

cmd:

```cmd
call "%USERPROFILE%\.llmwiki\config.cmd"
```

Ask before adding those lines to a shell profile. Common targets are `~/.zshrc`, `~/.bashrc`, PowerShell `$PROFILE`, or a project-specific startup script.

## Obsidian Detection

Full LLM Wiki operation expects both Obsidian App and an Obsidian CLI compatible with commands such as:

```bash
obsidian search query="keyword" limit=30 format=json
obsidian unresolved counts
obsidian backlinks path="domains/example/index.md" counts
```

If the CLI is absent, the wiki can still be initialized and edited through the filesystem. Mark route audit and backlink checks as degraded until the CLI is installed.

Do not treat a command as a valid Obsidian CLI merely because `obsidian` exists on PATH. Verify that `obsidian --help` or `obsidian-cli --help` prints the expected command surface, including route-audit commands such as `backlinks`, `links`, `outline`, and `vault info=path`.

The bootstrap script should register real setup vaults in Obsidian automatically. It writes the platform Obsidian registry config and may open `obsidian://open?vault=<vault-id>` when `--open-obsidian` is requested. For smoke tests and demos, pass `--skip-obsidian-register` or set `OBSIDIAN_CONFIG_PATH` to an isolated temporary file.

## Installation Branches

macOS:

- App check: `/Applications/Obsidian.app`, `~/Applications/Obsidian.app`, or `obsidian` on PATH.
- Preferred package manager: Homebrew.
- App install command after confirmation: `brew install --cask obsidian`.

Windows:

- App check: `%LOCALAPPDATA%\Obsidian\Obsidian.exe`, `%ProgramFiles%\Obsidian\Obsidian.exe`, or `obsidian.exe` on PATH.
- Preferred package manager: `winget`; fallbacks are Chocolatey or Scoop if already present.
- App install command after confirmation: `winget install Obsidian.Obsidian`.
- Prefer PowerShell examples. Quote paths because `Program Files` and user names may contain spaces.

Linux:

- App check: `obsidian` on PATH, common `/usr/bin` and `~/.local/bin` locations, or AppImage under `~/Applications`.
- Package manager varies by distribution.
- Prefer Flatpak when available: `flatpak install flathub md.obsidian.Obsidian`.
- Snap fallback when available: `snap install obsidian --classic`.

## Manual Fallback

When installation cannot be completed by the agent:

1. Tell the user what is missing.
2. Provide one platform-specific manual install option.
3. Finish filesystem bootstrap if possible.
4. Mark the final status as `degraded` and name the exact verification step to rerun after installation.
