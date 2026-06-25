#!/usr/bin/env python3
"""Bootstrap a cross-platform LLM Wiki vault and config files."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import shutil
import subprocess
import time
import webbrowser
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


def obsidian_config_candidates(os_name: str) -> list[Path]:
    override = os.environ.get("OBSIDIAN_CONFIG_PATH")
    if override:
        return [Path(override).expanduser()]
    home = Path.home()
    if os_name == "macos":
        return [home / "Library/Application Support/obsidian/obsidian.json"]
    if os_name == "windows":
        bases = [os.environ.get("APPDATA"), os.environ.get("LOCALAPPDATA")]
        return [Path(base) / "Obsidian/obsidian.json" for base in bases if base]
    return [
        home / ".config/obsidian/obsidian.json",
        home / ".var/app/md.obsidian.Obsidian/config/obsidian/obsidian.json",
    ]


def vault_id_for_path(wiki: Path) -> str:
    return hashlib.sha256(str(wiki).encode("utf-8")).hexdigest()[:16]


def quit_obsidian_for_registry(os_name: str) -> dict[str, object]:
    if os_name != "macos" or os.environ.get("OBSIDIAN_CONFIG_PATH"):
        return {"attempted": False}
    result: dict[str, object] = {"attempted": True, "quit": False}
    subprocess.run(
        ["osascript", "-e", 'tell application "Obsidian" to quit'],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    for _ in range(30):
        code, _, _ = run(["pgrep", "-x", "Obsidian"])
        if code != 0:
            result["quit"] = True
            return result
        time.sleep(0.5)
    result["error"] = "Obsidian did not quit before registry update."
    return result


def open_obsidian_app(os_name: str, vault_id: str) -> bool:
    if os_name == "macos":
        proc = subprocess.run(
            ["open", "-a", "Obsidian"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        return proc.returncode == 0
    return bool(webbrowser.open(f"obsidian://open?vault={vault_id}"))


def register_obsidian_vault(wiki: Path, os_name: str, open_obsidian: bool, dry_run: bool) -> dict[str, object]:
    config_path = obsidian_config_candidates(os_name)[0]
    vault_id = vault_id_for_path(wiki)
    result: dict[str, object] = {
        "requested": True,
        "config_path": str(config_path),
        "vault_id": vault_id,
        "vault_path": str(wiki),
        "registered": False,
        "opened": False,
    }
    if dry_run:
        result["dry_run"] = True
        return result

    result["obsidian_quit"] = quit_obsidian_for_registry(os_name)
    if result["obsidian_quit"].get("error"):
        result["error"] = str(result["obsidian_quit"]["error"])
        return result

    data: dict[str, object] = {}
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            result["error"] = f"Cannot parse Obsidian config: {exc}"
            return result
    vaults = data.setdefault("vaults", {})
    if not isinstance(vaults, dict):
        result["error"] = "Obsidian config field `vaults` is not an object."
        return result
    existing_id = ""
    for key, info in vaults.items():
        if isinstance(info, dict) and Path(str(info.get("path", ""))).expanduser().resolve() == wiki:
            existing_id = key
            break
    vault_id = existing_id or vault_id
    for info in vaults.values():
        if isinstance(info, dict):
            info.pop("open", None)
    vaults[vault_id] = {
        "path": str(wiki),
        "ts": int(time.time() * 1000),
        "open": True,
    }
    data["cli"] = True
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    result["registered"] = True
    result["vault_id"] = vault_id

    if open_obsidian:
        result["opened"] = open_obsidian_app(os_name, vault_id)
    return result


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


def existing_wiki_blocker(wiki_root: Path, force: bool) -> str:
    if force or not wiki_root.exists():
        return ""
    try:
        has_content = any(wiki_root.iterdir())
    except OSError as exc:
        return f"Cannot inspect existing wiki root {wiki_root}: {exc}"
    if has_content:
        return (
            f"Refusing to initialize into non-empty wiki root {wiki_root}. "
            "Choose an empty directory or rerun with --force after explicit user confirmation."
        )
    return ""


def registered_obsidian_vault_paths(os_name: str) -> list[Path]:
    paths: list[Path] = []
    for config_path in obsidian_config_candidates(os_name):
        if not config_path.exists():
            continue
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for info in data.get("vaults", {}).values():
            if isinstance(info, dict) and info.get("path"):
                try:
                    paths.append(Path(str(info["path"])).expanduser().resolve())
                except OSError:
                    continue
    return paths


def nested_vault_blocker(wiki_root: Path, os_name: str, force: bool) -> str:
    if force:
        return ""
    for existing in registered_obsidian_vault_paths(os_name):
        if existing == wiki_root:
            continue
        try:
            wiki_root.relative_to(existing)
        except ValueError:
            continue
        return (
            f"Refusing to create a vault inside existing Obsidian vault {existing}. "
            "Choose a path outside existing vault roots or rerun with --force after explicit confirmation."
        )
    return ""


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


def attach_post_register_route(summary: dict[str, object], wiki_root: Path, wait_for_open: bool) -> None:
    if wait_for_open:
        time.sleep(2)
    cli = detect_obsidian_cli()
    route = obsidian_route_status(wiki_root, cli)
    summary["post_register_route"] = {
        "obsidian_cli": cli,
        "obsidian_route": route,
    }
    register = summary.get("obsidian_register", {})
    if isinstance(register, dict) and register.get("registered") and not route.get("trusted"):
        degraded = summary.setdefault("degraded", [])
        message = "Obsidian vault registered/opened, but CLI route does not currently point to WIKI_ROOT"
        if isinstance(degraded, list) and message not in degraded:
            degraded.append(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap an LLM Wiki vault.")
    parser.add_argument("--wiki-root", help="Target wiki root. Defaults to WIKI_ROOT or ~/wiki.")
    parser.add_argument("--config-path", help="Override config file path.")
    parser.add_argument("--domain", action="append", help="Initial Chinese domain name. Repeatable.")
    parser.add_argument("--check-only", action="store_true", help="Only inspect environment and print a summary.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned writes without writing files.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing bootstrap files.")
    parser.add_argument("--no-git", action="store_true", help="Do not initialize Git.")
    parser.add_argument("--skip-obsidian-register", action="store_true", help="Do not register the new vault in Obsidian.")
    parser.add_argument("--open-obsidian", action="store_true", help="Open the registered vault in Obsidian after bootstrap.")
    parser.add_argument("--register-only", action="store_true", help="Only register an existing wiki root in Obsidian.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON summary.")
    args = parser.parse_args()

    summary = build_summary(args)
    if args.check_only:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    wiki_root = Path(summary["wiki_root"])
    cfg_paths = [Path(p) for p in summary["config_paths"]]
    dry_run = bool(args.dry_run)
    if args.register_only:
        if not wiki_root.is_dir():
            summary["error"] = f"Cannot register missing wiki root {wiki_root}."
            print(json.dumps(summary, ensure_ascii=False, indent=2))
            return 2
        summary["config_write_mode"] = "not-written-in-register-only"
        summary["config_written"] = []
        if args.skip_obsidian_register:
            summary["obsidian_register"] = {"requested": False, "reason": "Skipped by --skip-obsidian-register"}
        else:
            summary["obsidian_register"] = register_obsidian_vault(wiki_root, str(summary["tools"]["os"]), args.open_obsidian, dry_run)
            attach_post_register_route(summary, wiki_root, args.open_obsidian and not dry_run)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    blocker = existing_wiki_blocker(wiki_root, args.force)
    if not blocker:
        blocker = nested_vault_blocker(wiki_root, str(summary["tools"]["os"]), args.force)
    if blocker:
        summary["error"] = blocker
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 2
    if not dry_run:
        wiki_root.mkdir(parents=True, exist_ok=True)

    summary["config_written"] = write_config_files(cfg_paths, summary["config"], args.force, dry_run)
    summary["wiki_writes"] = create_wiki(wiki_root, summary["domains"], args.force, dry_run)
    summary["git"] = {"status": "skipped"} if args.no_git else init_git(wiki_root, dry_run)
    if args.skip_obsidian_register:
        summary["obsidian_register"] = {"requested": False, "reason": "Skipped by --skip-obsidian-register"}
    else:
        summary["obsidian_register"] = register_obsidian_vault(wiki_root, str(summary["tools"]["os"]), args.open_obsidian, dry_run)
        attach_post_register_route(summary, wiki_root, args.open_obsidian and not dry_run)

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
