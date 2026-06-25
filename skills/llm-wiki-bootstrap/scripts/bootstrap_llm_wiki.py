#!/usr/bin/env python3
"""Bootstrap a cross-platform LLM Wiki vault and config files."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path


DEFAULT_DOMAINS = [
    "AI Agent工程",
    "业务与运营",
    "产品与工具",
    "研究与阅读",
    "项目复盘",
    "个人方法论",
]


def user_home() -> Path:
    return Path.home()


def detect_os() -> str:
    name = platform.system().lower()
    if name.startswith("darwin"):
        return "macos"
    if name.startswith("windows"):
        return "windows"
    if name.startswith("linux"):
        return "linux"
    return name or "unknown"


def command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def run(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def detect_obsidian_app(os_name: str) -> dict[str, object]:
    home = user_home()
    candidates: list[Path] = []
    if os_name == "macos":
        candidates.extend([
            Path("/Applications/Obsidian.app"),
            home / "Applications/Obsidian.app",
        ])
    elif os_name == "windows":
        local_appdata = os.environ.get("LOCALAPPDATA")
        program_files = os.environ.get("ProgramFiles")
        program_files_x86 = os.environ.get("ProgramFiles(x86)")
        for base in [local_appdata, program_files, program_files_x86]:
            if base:
                candidates.append(Path(base) / "Obsidian" / "Obsidian.exe")
        candidates.append(home / "AppData/Local/Obsidian/Obsidian.exe")
    elif os_name == "linux":
        candidates.extend([
            Path("/usr/bin/obsidian"),
            Path("/usr/local/bin/obsidian"),
            home / ".local/bin/obsidian",
            home / "Applications/Obsidian.AppImage",
        ])
    found = [str(path) for path in candidates if path.exists()]
    return {"installed": bool(found) or command_exists("obsidian"), "paths": found}


def detect_obsidian_cli() -> dict[str, object]:
    candidates = ["obsidian", "obsidian-cli"]
    detected = [cmd for cmd in candidates if command_exists(cmd)]
    verified = []
    unverified = []
    for cmd in detected:
        code, out, err = run([cmd, "--help"])
        help_text = f"{out}\n{err}"
        if code == 0 and "Usage: obsidian" in help_text and "backlinks" in help_text:
            verified.append(cmd)
        else:
            unverified.append(cmd)
    return {
        "installed": bool(verified),
        "commands": verified,
        "detected_commands": detected,
        "unverified_commands": unverified,
    }


def obsidian_route_status(wiki: Path, cli: dict[str, object]) -> dict[str, object]:
    commands = cli.get("commands") or []
    if not commands:
        return {
            "available": False,
            "trusted": False,
            "active_vault_path": "",
            "target_wiki_path": str(wiki),
            "error": "No verified Obsidian CLI command was found.",
        }
    command = str(commands[0])
    code, out, err = run([command, "vault", "info=path"])
    active = out.splitlines()[-1] if out else ""
    trusted = False
    if code == 0 and active:
        try:
            trusted = Path(active).expanduser().resolve() == wiki
        except OSError:
            trusted = False
    return {
        "available": code == 0,
        "trusted": trusted,
        "command": command,
        "active_vault_path": active,
        "target_wiki_path": str(wiki),
        "error": err if code else "",
    }


def detect_package_managers(os_name: str) -> list[str]:
    if os_name == "macos":
        candidates = ["brew"]
    elif os_name == "windows":
        candidates = ["winget", "choco", "scoop"]
    elif os_name == "linux":
        candidates = ["flatpak", "snap", "apt", "dnf", "pacman", "zypper"]
    else:
        candidates = []
    return [cmd for cmd in candidates if command_exists(cmd)]


def shell_family(os_name: str) -> str:
    if os_name == "windows":
        return "powershell"
    shell = os.environ.get("SHELL", "")
    if shell:
        return Path(shell).name
    return "sh"


def default_skill_source() -> str:
    env = os.environ.get("LLMWIKI_SKILL_SOURCE")
    if env:
        return str(Path(env).expanduser())
    script_path = Path(__file__).resolve()
    candidates = [
        script_path.parents[3],
        script_path.parents[2] / ".llmwiki-source",
        Path(os.environ.get("CODEX_SKILLS_DIR", str(Path.home() / ".codex/skills"))) / ".llmwiki-source",
        Path.cwd(),
    ]
    for source_root in candidates:
        if (source_root / "shared").exists() and (source_root / "skills").exists():
            return str(source_root)
    return ""


def build_config(wiki_root: Path, os_name: str) -> dict[str, str]:
    home = user_home()
    config = {
        "WIKI_ROOT": str(wiki_root),
        "LLMWIKI_SKILL_SOURCE": default_skill_source(),
        "CODEX_SKILLS_DIR": os.environ.get("CODEX_SKILLS_DIR", str(home / ".codex/skills")),
        "HERMES_SKILLS_DIR": os.environ.get("HERMES_SKILLS_DIR", str(home / ".hermes/skills")),
        "LARK_AGENT_SKILLS_DIR": os.environ.get("LARK_AGENT_SKILLS_DIR", str(home / ".agents/skills")),
        "OPENCLAW_SKILLS_DIR": os.environ.get("OPENCLAW_SKILLS_DIR", str(home / ".openclaw/workspace/skills")),
        "CLAUDE_CODE_SKILLS_DIR": os.environ.get(
            "CLAUDE_CODE_SKILLS_DIR",
            str(home / ".claude/plugins/marketplaces/claude-plugins-official.bak"),
        ),
    }
    if os_name == "windows":
        config.update({
            key: value.replace("/", "\\") if value else value
            for key, value in config.items()
        })
    return config


def config_paths(os_name: str) -> list[Path]:
    base = user_home() / ".llmwiki"
    if os_name == "windows":
        return [base / "config.ps1", base / "config.cmd"]
    return [base / "config.env"]


def quote_posix(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def write_config_files(paths: list[Path], config: dict[str, str], force: bool, dry_run: bool) -> list[str]:
    written: list[str] = []
    for path in paths:
        if path.exists() and not force:
            continue
        if dry_run:
            written.append(str(path))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".ps1":
            text = "\n".join(f'$env:{key} = "{value}"' for key, value in config.items()) + "\n"
        elif path.suffix == ".cmd":
            text = "\n".join(f"set {key}={value}" for key, value in config.items()) + "\n"
        else:
            text = "\n".join(f"export {key}={quote_posix(value)}" for key, value in config.items()) + "\n"
        path.write_text(text, encoding="utf-8")
        written.append(str(path))
    return written


def frontmatter(title: str, page_type: str, domain: str = "") -> str:
    today = dt.date.today().isoformat()
    domain_line = f"domain: {domain}" if domain else "domain: system"
    return (
        "---\n"
        f"title: {title}\n"
        f"type: {page_type}\n"
        f"created: {today}\n"
        f"updated: {today}\n"
        f"{domain_line}\n"
        "tags: []\n"
        "sources: []\n"
        "status: active\n"
        "---\n\n"
    )


def core_files(domains: list[str]) -> dict[Path, str]:
    domain_links = "\n".join(f"- [[domains/{name}/index|{name}]]" for name in domains)
    return {
        Path("AGENTS.md"): (
            "# LLM Wiki Agent Rules\n\n"
            "- Treat this vault as a durable knowledge base, not a dump folder.\n"
            "- Preserve raw sources under `raw/` and extraction notes under `_meta/extraction-notes/`.\n"
            "- Use Chinese human-facing titles by default when the user's work context is Chinese.\n"
            "- Update `index.md` and `log.md` after meaningful wiki changes.\n"
            "- Do not delete or overwrite existing knowledge without explicit user confirmation.\n"
        ),
        Path("SCHEMA.md"): (
            "# LLM Wiki Schema\n\n"
            "Formal pages should start with YAML frontmatter:\n\n"
            "```yaml\n"
            "title: Page title\n"
            "type: concept | workflow | reference | case | index | log\n"
            "created: YYYY-MM-DD\n"
            "updated: YYYY-MM-DD\n"
            "domain: Domain name\n"
            "tags: []\n"
            "sources: []\n"
            "status: active | draft | archived\n"
            "```\n\n"
            "Use `[[wikilinks]]` for durable relationships and cite raw sources in `sources`.\n"
        ),
        Path("index.md"): (
            frontmatter("LLM Wiki Index", "index")
            + "# LLM Wiki\n\n"
            + "## Domains\n\n"
            + domain_links
            + "\n\n## Operating Pages\n\n"
            + "- [[SCHEMA|Schema]]\n"
            + "- [[log|Log]]\n"
        ),
        Path("log.md"): (
            frontmatter("LLM Wiki Log", "log")
            + "# Log\n\n"
            + f"- {dt.date.today().isoformat()}: Initialized LLM Wiki skeleton.\n"
        ),
    }


def domain_index(domain: str) -> str:
    return (
        frontmatter(domain, "index", domain)
        + f"# {domain}\n\n"
        + "## 领域说明\n\n"
        + "这里记录本领域可复用、可检索、可持续演化的知识。\n\n"
        + "## 入口\n\n"
        + "- 待补充核心概念\n"
        + "- 待补充工作流\n"
        + "- 待补充案例\n\n"
        + "## 待沉淀问题\n\n"
        + "- 这个领域里最常被问到的问题是什么？\n"
        + "- 哪些材料需要通过 `llm-wiki-ingest` 编译进来？\n"
    )


def create_wiki(wiki_root: Path, domains: list[str], force: bool, dry_run: bool) -> dict[str, list[str]]:
    created: list[str] = []
    skipped: list[str] = []
    dirs = [
        Path("domains"),
        Path("raw"),
        Path("raw/transcripts"),
        Path("_meta"),
        Path("_meta/extraction-notes"),
        Path("_meta/templates"),
        Path("Clippings"),
        Path("queries"),
    ]
    for domain in domains:
        dirs.append(Path("domains") / domain)
    for rel in dirs:
        path = wiki_root / rel
        if dry_run:
            created.append(str(path))
        else:
            path.mkdir(parents=True, exist_ok=True)
            created.append(str(path))

    files = core_files(domains)
    for domain in domains:
        files[Path("domains") / domain / "index.md"] = domain_index(domain)

    for rel, text in files.items():
        path = wiki_root / rel
        if path.exists() and not force:
            skipped.append(str(path))
            continue
        if dry_run:
            created.append(str(path))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        created.append(str(path))
    return {"created": created, "skipped": skipped}


def init_git(wiki_root: Path, dry_run: bool) -> dict[str, object]:
    if (wiki_root / ".git").exists():
        return {"status": "exists"}
    if not command_exists("git"):
        return {"status": "missing-git"}
    if dry_run:
        return {"status": "would-init"}
    subprocess.run(["git", "init"], cwd=str(wiki_root), check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {"status": "initialized" if (wiki_root / ".git").exists() else "failed"}


def install_hints(os_name: str, package_managers: list[str]) -> list[str]:
    hints: list[str] = []
    if os_name == "macos":
        if "brew" in package_managers:
            hints.append("Obsidian App: brew install --cask obsidian")
        else:
            hints.append("Install Homebrew or download Obsidian from https://obsidian.md/download")
        hints.append("Obsidian CLI: install the CLI package used by your team, then ensure `obsidian` is on PATH.")
    elif os_name == "windows":
        if "winget" in package_managers:
            hints.append("Obsidian App: winget install Obsidian.Obsidian")
        else:
            hints.append("Download Obsidian from https://obsidian.md/download or install winget/choco/scoop first.")
        hints.append("Obsidian CLI: install the CLI package used by your team and ensure `obsidian.exe` is on PATH.")
    elif os_name == "linux":
        if "flatpak" in package_managers:
            hints.append("Obsidian App: flatpak install flathub md.obsidian.Obsidian")
        elif "snap" in package_managers:
            hints.append("Obsidian App: snap install obsidian --classic")
        else:
            hints.append("Install Obsidian through your distribution, Flatpak, Snap, or AppImage.")
        hints.append("Obsidian CLI: install the CLI package used by your team and ensure `obsidian` is on PATH.")
    else:
        hints.append("Install Obsidian App and Obsidian CLI manually for your operating system.")
    return hints


def load_snippet(os_name: str, paths: list[Path]) -> str:
    if os_name == "windows":
        ps1 = next((p for p in paths if p.suffix == ".ps1"), paths[0])
        return f'. "{ps1}"'
    return f"source {quote_posix(str(paths[0]))}"


def build_summary(args: argparse.Namespace) -> dict[str, object]:
    os_name = detect_os()
    wiki_root = Path(args.wiki_root or os.environ.get("WIKI_ROOT") or user_home() / "wiki").expanduser().resolve()
    domains = args.domain or DEFAULT_DOMAINS
    config = build_config(wiki_root, os_name)
    cfg_paths = [Path(args.config_path).expanduser().resolve()] if args.config_path else config_paths(os_name)
    package_managers = detect_package_managers(os_name)
    obsidian_cli = detect_obsidian_cli()
    obsidian_route = obsidian_route_status(wiki_root, obsidian_cli)
    tools = {
        "os": os_name,
        "shell": shell_family(os_name),
        "python": True,
        "git": command_exists("git"),
        "obsidian_app": detect_obsidian_app(os_name),
        "obsidian_cli": obsidian_cli,
        "obsidian_route": obsidian_route,
        "package_managers": package_managers,
    }
    degraded = []
    if not tools["obsidian_app"]["installed"]:
        degraded.append("Obsidian App not detected")
    if not tools["obsidian_cli"]["installed"]:
        degraded.append("Verified Obsidian CLI not detected")
    elif not tools["obsidian_route"]["trusted"]:
        degraded.append("Obsidian CLI target vault is unavailable or does not match WIKI_ROOT")
    return {
        "wiki_root": str(wiki_root),
        "domains": domains,
        "config_paths": [str(p) for p in cfg_paths],
        "config": config,
        "tools": tools,
        "degraded": degraded,
        "install_hints": install_hints(os_name, package_managers),
        "load_config_command": load_snippet(os_name, cfg_paths),
        "route_audit_check_command": f"{obsidian_route.get('command', 'obsidian')} vault info=path",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap an LLM Wiki vault.")
    parser.add_argument("--wiki-root", help="Target wiki root. Defaults to WIKI_ROOT or ~/wiki.")
    parser.add_argument("--config-path", help="Override config file path.")
    parser.add_argument("--domain", action="append", help="Initial Chinese domain name. Repeatable.")
    parser.add_argument("--check-only", action="store_true", help="Only inspect environment and print a summary.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned writes without writing files.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing bootstrap files.")
    parser.add_argument("--no-git", action="store_true", help="Do not initialize Git.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON summary.")
    args = parser.parse_args()

    summary = build_summary(args)
    if args.check_only:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    wiki_root = Path(summary["wiki_root"])
    cfg_paths = [Path(p) for p in summary["config_paths"]]
    dry_run = bool(args.dry_run)
    if not dry_run:
        wiki_root.mkdir(parents=True, exist_ok=True)

    summary["config_written"] = write_config_files(cfg_paths, summary["config"], args.force, dry_run)
    summary["wiki_writes"] = create_wiki(wiki_root, summary["domains"], args.force, dry_run)
    summary["git"] = {"status": "skipped"} if args.no_git else init_git(wiki_root, dry_run)

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
