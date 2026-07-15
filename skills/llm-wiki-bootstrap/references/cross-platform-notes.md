# Cross-Platform Notes

The normative installation and verification branches are in `toolchain-install.md`. Use this short reference for environment loading only.

All platforms should prefer reading `~/.llmwiki/config.json` as data. Shell
compatibility files remain available for interactive use.

macOS/Linux compatibility:

```bash
source "$HOME/.llmwiki/config.env"
```

PowerShell (preferred, execution-policy independent):

```powershell
$config = Get-Content -Raw -LiteralPath "$env:USERPROFILE\.llmwiki\config.json" | ConvertFrom-Json
$wikiRoot = [string]$config.WIKI_ROOT
```

Do not change execution policy merely to load `config.ps1`. Older shell config
files may be read as plain text when `config.json` is not yet present.

cmd:

```cmd
call "%USERPROFILE%\.llmwiki\config.cmd"
```

Ask before adding any of these to a shell profile. A config file is useful but not required for basic filesystem operation.
