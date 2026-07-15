#!/usr/bin/env python3
"""Bootstrap a cross-platform LLM Wiki vault and config files."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import struct
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path


DEFAULT_DOMAINS = [
    "财税与经营财务",
    "电商运营",
    "品牌策略",
    "视觉制作",
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


def run(cmd: list[str], timeout: int = 20) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, "", str(exc)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def architecture_status(os_name: str) -> dict[str, str]:
    checker_arch = platform.machine() or "unknown"
    launcher_arch = checker_arch
    native_arch = checker_arch
    source = "platform.machine"
    if os_name == "windows":
        launcher_arch = os.environ.get("PROCESSOR_ARCHITECTURE") or checker_arch
        native_arch = (
            os.environ.get("PROCESSOR_ARCHITEW6432")
            or launcher_arch
            or checker_arch
        )
        source = "Windows architecture environment"
    return {
        "native": native_arch,
        "launcher_environment": launcher_arch,
        "python_checker": checker_arch,
        "python_bits": str(64 if sys.maxsize > 2**32 else 32),
        "source": source,
    }


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
                candidates.append(Path(base) / "Programs" / "Obsidian" / "Obsidian.exe")
        candidates.append(home / "AppData/Local/Obsidian/Obsidian.exe")
        candidates.append(home / "AppData/Local/Programs/Obsidian/Obsidian.exe")
    elif os_name == "linux":
        candidates.extend([
            Path("/usr/bin/obsidian"),
            Path("/usr/local/bin/obsidian"),
            home / ".local/bin/obsidian",
            home / "Applications/Obsidian.AppImage",
        ])
    found: list[str] = []
    for path in candidates:
        value = str(path)
        if path.exists() and value not in found:
            found.append(value)
    versions: list[dict[str, str]] = []
    if os_name == "windows":
        for path in found:
            command = (
                f"(Get-Item -LiteralPath '{path.replace("'", "''")}')."
                "VersionInfo.ProductVersion"
            )
            code, out, _ = run(["powershell.exe", "-NoProfile", "-Command", command])
            versions.append({"path": path, "version": out if code == 0 else ""})
    return {
        "installed": bool(found) or command_exists("obsidian"),
        "paths": found,
        "versions": versions,
    }


def detect_obsidian_cli(os_name: str, app: dict[str, object] | None = None) -> dict[str, object]:
    app = app or detect_obsidian_app(os_name)
    candidates: list[str] = []
    if os_name == "windows":
        for raw in app.get("paths", []):
            cli_path = Path(str(raw)).with_name("Obsidian.com")
            if cli_path.exists():
                candidates.append(str(cli_path))
        candidates.extend(["obsidian", "Obsidian.com"])
    elif os_name == "macos":
        candidates.extend([
            "/Applications/Obsidian.app/Contents/MacOS/obsidian-cli",
            str(user_home() / "Applications/Obsidian.app/Contents/MacOS/obsidian-cli"),
            "/usr/local/bin/obsidian",
            "obsidian",
        ])
    else:
        candidates.extend(["obsidian", "obsidian-cli"])
    detected = []
    for cmd in candidates:
        resolved = ""
        if Path(cmd).is_absolute() and Path(cmd).exists():
            resolved = cmd
        elif command_exists(cmd):
            resolved = shutil.which(cmd) or cmd
        if resolved and resolved not in detected:
            detected.append(resolved)
    verified = []
    unverified = []
    for cmd in detected:
        code, out, err = run([cmd, "help"])
        help_text = f"{out}\n{err}".lower()
        if code == 0 and all(token in help_text for token in ["backlinks", "search", "vault"]):
            verified.append(cmd)
        else:
            unverified.append({"command": cmd, "exit_code": code, "error": err or out[-300:]})
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


def build_config(
    wiki_root: Path,
    os_name: str,
    media: dict[str, object] | None = None,
) -> dict[str, str]:
    config = {
        "WIKI_ROOT": str(wiki_root),
        "LLMWIKI_SKILL_SOURCE": default_skill_source(),
    }
    media = media or {}
    primary_bin = str(media.get("primary_bin") or "")
    model = media.get("asr_model") or {}
    model_path = str(model.get("path") or "") if isinstance(model, dict) else ""
    if primary_bin:
        config["LLMWIKI_MEDIA_BIN"] = primary_bin
    if model_path:
        config["WHISPER_MODEL"] = model_path
    if os_name == "windows":
        config.update({
            key: value.replace("/", "\\") if value else value
            for key, value in config.items()
        })
    return config


def config_paths(os_name: str) -> list[Path]:
    base = user_home() / ".llmwiki"
    if os_name == "windows":
        return [base / "config.json", base / "config.ps1", base / "config.cmd"]
    return [base / "config.json", base / "config.env"]


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
        if path.suffix == ".json":
            text = json.dumps(config, ensure_ascii=False, indent=2) + "\n"
        elif path.suffix == ".ps1":
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
            "- This vault is the only official LLM Wiki for this environment.\n"
            "- When the user says 做成知识库、加入 Wiki、把资料入库, use the installed Wiki ingestion skill and complete its full SOP.\n"
            "- Do not reduce ingestion to a summary or merely copy the source file.\n"
            "- If an ingestion step needs a missing local tool, explain the trusted installation source and install it after confirmation; do not silently bypass the step.\n"
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


def tools_markdown(tools: dict[str, object]) -> str:
    media = tools.get("media") or {}
    obsidian_app = tools.get("obsidian_app") or {}
    obsidian_cli = tools.get("obsidian_cli") or {}
    architecture = tools.get("architecture") or {}
    rows = [
        ("Obsidian App", ", ".join(str(x) for x in obsidian_app.get("paths", [])), "detected" if obsidian_app.get("installed") else "missing"),
        ("Obsidian CLI", ", ".join(str(x) for x in obsidian_cli.get("commands", [])), "verified" if obsidian_cli.get("installed") else "missing"),
        ("FFmpeg", str((media.get("ffmpeg") or {}).get("command") or ""), str((media.get("ffmpeg") or {}).get("version") or "")),
        ("FFprobe", str((media.get("ffprobe") or {}).get("command") or ""), str((media.get("ffprobe") or {}).get("version") or "")),
        ("Whisper CLI", str((media.get("local_asr") or {}).get("command") or ""), str((media.get("local_asr") or {}).get("version") or "")),
        ("Whisper model", str((media.get("asr_model") or {}).get("path") or ""), "configured" if (media.get("asr_model") or {}).get("configured") else "missing"),
        ("Tesseract", str((media.get("tesseract") or {}).get("command") or ""), str((media.get("tesseract") or {}).get("version") or "")),
    ]
    lines = [
        "# Wiki Tool Inventory",
        "",
        f"- Generated: {dt.datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"- Operating system: {tools.get('os', '')}",
        f"- Native architecture: {architecture.get('native', '')}",
        "- Purpose: verified executable and model locations for Wiki ingestion. This file contains no credentials.",
        "",
        "| Tool | Executable or model path | Verification |",
        "| --- | --- | --- |",
    ]
    for name, command, verification in rows:
        safe_command = command.replace("|", "\\|") or "—"
        safe_verification = verification.replace("|", "\\|") or "—"
        lines.append(f"| {name} | `{safe_command}` | {safe_verification} |")
    lines.extend(["", "Prefer these recorded absolute paths before probing PATH or installing another copy.", ""])
    return "\n".join(lines)


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


def create_wiki(
    wiki_root: Path,
    domains: list[str],
    force: bool,
    dry_run: bool,
    tool_inventory: str = "",
) -> dict[str, list[str]]:
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
    if tool_inventory:
        files[Path("TOOLS.md")] = tool_inventory
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


def target_status(wiki_root: Path) -> dict[str, object]:
    if not wiki_root.exists():
        return {"exists": False, "empty": True, "entries": [], "error": ""}
    try:
        entries = sorted(path.name for path in wiki_root.iterdir())
    except OSError as exc:
        return {"exists": True, "empty": False, "entries": [], "error": str(exc)}
    return {
        "exists": True,
        "empty": not entries,
        "entries": entries,
        "error": "",
    }


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


def media_search_dirs(os_name: str, explicit: str = "") -> list[Path]:
    candidates: list[Path] = []
    for raw in [explicit, os.environ.get("LLMWIKI_MEDIA_BIN", "")]:
        if raw:
            candidates.append(Path(raw).expanduser())
    if os_name == "windows":
        drive = os.environ.get("SystemDrive", "C:")
        candidates.extend([
            Path(f"{drive}\\msys64\\clangarm64\\bin"),
            Path(f"{drive}\\msys64\\mingw64\\bin"),
            user_home() / "msys64/clangarm64/bin",
            user_home() / "msys64/mingw64/bin",
        ])
    result: list[Path] = []
    for path in candidates:
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        if resolved.is_dir() and resolved not in result:
            result.append(resolved)
    return result


def find_executable(command_names: list[str], search_dirs: list[Path]) -> str:
    for command in command_names:
        path = shutil.which(command)
        if path:
            return path
    suffixes = [""] if detect_os() != "windows" else [".exe", ".com", ".cmd", ""]
    for directory in search_dirs:
        for command in command_names:
            for suffix in suffixes:
                candidate = directory / (command if Path(command).suffix else f"{command}{suffix}")
                if candidate.is_file():
                    return str(candidate)
    return ""


def binary_architecture(path: str) -> str:
    try:
        with Path(path).open("rb") as handle:
            if handle.read(2) != b"MZ":
                return ""
            handle.seek(0x3C)
            pe_offset = struct.unpack("<I", handle.read(4))[0]
            handle.seek(pe_offset)
            if handle.read(4) != b"PE\x00\x00":
                return ""
            machine = struct.unpack("<H", handle.read(2))[0]
    except (OSError, struct.error):
        return ""
    return {
        0x014C: "x86",
        0x8664: "x64",
        0xAA64: "ARM64",
    }.get(machine, f"unknown-0x{machine:04x}")


def normalize_architecture(value: str) -> str:
    normalized = value.strip().lower().replace("_", "").replace("-", "")
    return {
        "amd64": "x64",
        "x8664": "x64",
        "aarch64": "arm64",
    }.get(normalized, normalized)


def probe_tool(
    command_names: list[str],
    version_args: list[str],
    search_dirs: list[Path] | None = None,
) -> dict[str, object]:
    path = find_executable(command_names, search_dirs or [])
    if path:
        code, out, err = run([path, *version_args])
        text = out or err
        return {
            "installed": code == 0,
            "command": path,
            "version": text.splitlines()[0] if text else "",
            "exit_code": code,
            "stderr": err[-500:] if err else "",
            "binary_architecture": binary_architecture(path),
        }
    return {"installed": False, "command": "", "version": ""}


def resolve_whisper_model(explicit: str = "") -> dict[str, object]:
    candidates: list[Path] = []
    for raw in [explicit, os.environ.get("WHISPER_MODEL", "")]:
        if raw:
            candidates.append(Path(raw).expanduser())
    candidates.extend([
        user_home() / "whisper-models/ggml-small.bin",
        user_home() / ".cache/whisper/ggml-small.bin",
    ])
    seen: list[str] = []
    for candidate in candidates:
        path = candidate.resolve()
        if str(path) in seen:
            continue
        seen.append(str(path))
        if path.is_file() and path.stat().st_size > 0:
            return {
                "configured": True,
                "path": str(path),
                "size": path.stat().st_size,
                "source": "argument/environment/common-location",
            }
    return {
        "configured": False,
        "path": str(candidates[0].resolve()) if candidates else "",
        "size": 0,
        "searched": seen,
    }


def whisper_canary(command: str, model_path: str) -> dict[str, object]:
    if not command or not model_path:
        return {"requested": True, "passed": False, "error": "Whisper executable or model is missing."}
    with tempfile.TemporaryDirectory(prefix="llmwiki-whisper-canary-") as td:
        root = Path(td)
        audio = root / "silence.wav"
        output_base = root / "result"
        with wave.open(str(audio), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(b"\x00\x00" * 16000)
        code, out, err = run([
            command,
            "-m", model_path,
            "-f", str(audio),
            "-l", "zh",
            "-otxt",
            "-of", str(output_base),
            "-nt",
        ], timeout=180)
        output_file = output_base.with_suffix(".txt")
        return {
            "requested": True,
            "passed": code == 0 and output_file.exists(),
            "exit_code": code,
            "output_created": output_file.exists(),
            "stdout_tail": out[-500:],
            "stderr_tail": err[-500:],
        }


def detect_media_toolchain(
    os_name: str | None = None,
    explicit_media_bin: str = "",
    explicit_model: str = "",
    verify_media: bool = False,
) -> dict[str, object]:
    os_name = os_name or detect_os()
    search_dirs = media_search_dirs(os_name, explicit_media_bin)
    ffmpeg = probe_tool(["ffmpeg"], ["-version"], search_dirs)
    ffprobe = probe_tool(["ffprobe"], ["-version"], search_dirs)
    whisper = probe_tool(["whisper-cli", "whisper.cpp", "whisper-cpp"], ["--version"], search_dirs)
    tesseract = probe_tool(["tesseract"], ["--version"], search_dirs)
    languages: list[str] = []
    if tesseract.get("installed") and tesseract.get("command"):
        code, out, _ = run([str(tesseract["command"]), "--list-langs"])
        if code == 0:
            languages = [line.strip() for line in out.splitlines()[1:] if line.strip()]
    tesseract["languages"] = languages
    tesseract["required_languages_ready"] = all(lang in languages for lang in ["chi_sim", "eng"])
    imagemagick = probe_tool(["magick"], ["-version"], search_dirs)
    model = resolve_whisper_model(explicit_model)
    canary = (
        whisper_canary(str(whisper.get("command") or ""), str(model.get("path") or ""))
        if verify_media
        else {"requested": False, "passed": None}
    )
    required_detected = bool(
        ffmpeg.get("installed")
        and ffprobe.get("installed")
        and whisper.get("installed")
        and model.get("configured")
        and tesseract.get("installed")
        and tesseract.get("required_languages_ready")
    )
    native_arch = architecture_status(os_name)["native"]
    required_tools = [ffmpeg, ffprobe, whisper, tesseract]
    reported_arches = [
        str(item.get("binary_architecture") or "")
        for item in required_tools
        if item.get("command")
    ]
    native_architecture_ready = bool(
        os_name != "windows"
        or (
            len(reported_arches) == len(required_tools)
            and all(
                normalize_architecture(value) == normalize_architecture(native_arch)
                for value in reported_arches
            )
        )
    )
    command_dirs = [
        str(Path(str(item.get("command"))).parent)
        for item in [ffmpeg, ffprobe, whisper, tesseract]
        if item.get("command")
    ]
    primary_bin = command_dirs[0] if command_dirs and len(set(command_dirs)) == 1 else ""
    return {
        "search_dirs": [str(path) for path in search_dirs],
        "primary_bin": primary_bin,
        "ffmpeg": ffmpeg,
        "ffprobe": ffprobe,
        "local_asr": whisper,
        "asr_model": model,
        "asr_canary": canary,
        "native_architecture": native_arch,
        "native_architecture_ready": native_architecture_ready,
        "tesseract": tesseract,
        "imagemagick_optional": imagemagick,
        "required_detected": required_detected,
        "ready": bool(
            required_detected
            and native_architecture_ready
            and (not verify_media or bool(canary.get("passed")))
        ),
    }


def install_hints(os_name: str, package_managers: list[str]) -> list[str]:
    hints: list[str] = []
    if os_name == "macos":
        hints.append("Use the verified Obsidian domestic mirror or the course download; Obsidian 1.12.7+ includes its CLI.")
        hints.append("For media tools, read references/toolchain-install.md and use temporary Tsinghua Homebrew mirror settings.")
    elif os_name == "windows":
        hints.append("Use the verified Obsidian domestic mirror or the course download.")
        hints.append("Obsidian 1.12.7+ bundles the CLI; verify Obsidian.com beside Obsidian.exe after enabling it in Settings.")
        hints.append("For media tools, prefer the Tsinghua MSYS2 mirror after native architecture is confirmed.")
    elif os_name == "linux":
        if "flatpak" in package_managers:
            hints.append("Obsidian App: flatpak install flathub md.obsidian.Obsidian")
        elif "snap" in package_managers:
            hints.append("Obsidian App: snap install obsidian --classic")
        else:
            hints.append("Install Obsidian through your distribution, Flatpak, Snap, or AppImage.")
        hints.append("Obsidian 1.12.7+ bundles its CLI; verify the installed package launcher.")
    else:
        hints.append("Install Obsidian App and Obsidian CLI manually for your operating system.")
    return hints


def load_snippet(os_name: str, paths: list[Path]) -> str:
    if os_name == "windows":
        config_json = next((p for p in paths if p.suffix == ".json"), paths[0])
        return f"Get-Content -Raw -LiteralPath '{config_json}' | ConvertFrom-Json"
    config_json = next((p for p in paths if p.suffix == ".json"), paths[0])
    return f"read JSON config {quote_posix(str(config_json))}"


def build_summary(args: argparse.Namespace) -> dict[str, object]:
    os_name = detect_os()
    wiki_root_value = args.wiki_root or os.environ.get("WIKI_ROOT") or user_home() / "wiki"
    wiki_root_source = "argument" if args.wiki_root else ("environment" if os.environ.get("WIKI_ROOT") else "default proposal")
    wiki_root = Path(wiki_root_value).expanduser().resolve()
    domains = args.domain or DEFAULT_DOMAINS
    package_managers = detect_package_managers(os_name)
    obsidian_app = detect_obsidian_app(os_name)
    obsidian_cli = detect_obsidian_cli(os_name, obsidian_app)
    obsidian_route = obsidian_route_status(wiki_root, obsidian_cli)
    media = detect_media_toolchain(
        os_name,
        explicit_media_bin=args.media_bin or "",
        explicit_model=args.whisper_model or "",
        verify_media=bool(args.verify_media or not args.check_only),
    )
    config = build_config(wiki_root, os_name, media)
    cfg_paths = [Path(args.config_path).expanduser().resolve()] if args.config_path else config_paths(os_name)
    target = target_status(wiki_root)
    nested_blocker = nested_vault_blocker(wiki_root, os_name, False)
    tools = {
        "os": os_name,
        "architecture": architecture_status(os_name),
        "shell": shell_family(os_name),
        "python": {"installed": True, "version": platform.python_version(), "executable": sys.executable},
        "git": command_exists("git"),
        "obsidian_app": obsidian_app,
        "obsidian_cli": obsidian_cli,
        "obsidian_route": obsidian_route,
        "media": media,
        "package_managers": package_managers,
    }
    degraded = []
    if not tools["obsidian_app"]["installed"]:
        degraded.append("Obsidian App not detected")
    if not tools["obsidian_cli"]["installed"]:
        degraded.append("Verified Obsidian CLI not detected")
    elif not tools["obsidian_route"]["trusted"]:
        degraded.append("Obsidian CLI target vault is unavailable or does not match WIKI_ROOT")
    if not tools["media"]["ready"]:
        degraded.append("Media-ingestion toolchain is incomplete")
    core_ready = bool(tools["obsidian_app"]["installed"] and tools["obsidian_cli"]["installed"])
    media_ready = bool(tools["media"]["ready"])
    target_ready = bool(target["empty"] and not target["error"] and not nested_blocker)
    return {
        "inspection_mode": "read-only" if args.check_only else "bootstrap",
        "wiki_root": str(wiki_root),
        "current_state": {
            "wiki_root_source": wiki_root_source,
            "wiki_root_exists": wiki_root.exists(),
            "wiki_root_empty": target["empty"],
            "wiki_root_entries": target["entries"],
            "wiki_root_inspection_error": target["error"],
            "nested_vault_conflict": nested_blocker,
            "existing_config_paths": [str(p) for p in cfg_paths if p.exists()],
            "note": "config_paths and config below are planned bootstrap values; they do not prove that files already exist.",
        },
        "domains": domains,
        "config_paths": [str(p) for p in cfg_paths],
        "config": config,
        "tools": tools,
        "readiness": {
            "target_ready": target_ready,
            "core_ready": core_ready,
            "media_ready": media_ready,
            "bootstrap_ready": bool(target_ready and core_ready and media_ready),
            "media_canary_required": bool(args.verify_media or not args.check_only),
        },
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
    parser.add_argument("--media-bin", help="Directory containing the verified media/OCR executables.")
    parser.add_argument("--whisper-model", help="Path to the verified local Whisper model.")
    parser.add_argument("--verify-media", action="store_true", help="Run a local one-second Whisper canary in addition to version checks.")
    parser.add_argument("--require-toolchain-ready", action="store_true", help="Deprecated compatibility flag; full readiness is required by default.")
    parser.add_argument("--allow-degraded-bootstrap", action="store_true", help="Allow an incomplete toolchain only after the user explicitly accepts degraded initialization.")
    parser.add_argument("--check-only", action="store_true", help="Only inspect environment and print a summary.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned writes without writing files.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing bootstrap files.")
    parser.add_argument("--git", action="store_true", help="Initialize Git after explicit user confirmation.")
    parser.add_argument("--no-git", action="store_true", help="Deprecated compatibility flag; Git is skipped by default.")
    parser.add_argument("--skip-obsidian-register", action="store_true", help="Deprecated compatibility flag; registry edits are always skipped.")
    parser.add_argument("--open-obsidian", action="store_true", help="Deprecated compatibility flag; open the folder visibly in Obsidian instead.")
    parser.add_argument("--register-only", action="store_true", help="Deprecated; prints the safe manual vault-opening instruction.")
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
        summary["obsidian_register"] = {
            "requested": False,
            "reason": "Direct registry editing is disabled. In Obsidian choose Open folder as vault and select WIKI_ROOT.",
            "vault_path": str(wiki_root),
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    if not args.allow_degraded_bootstrap and not summary["readiness"]["bootstrap_ready"]:
        summary["error"] = (
            "Refusing to initialize because the target, Obsidian CLI, or media-ingestion "
            "toolchain is not fully ready. Resolve the reported readiness fields and rerun."
        )
        summary["readiness_gate"] = "blocked-before-write"
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 3

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
    summary["wiki_writes"] = create_wiki(
        wiki_root,
        summary["domains"],
        args.force,
        dry_run,
        tools_markdown(summary["tools"]),
    )
    summary["git"] = init_git(wiki_root, dry_run) if args.git and not args.no_git else {"status": "skipped"}
    summary["obsidian_register"] = {
        "requested": False,
        "reason": "Direct registry editing is disabled. In Obsidian choose Open folder as vault and select WIKI_ROOT.",
        "vault_path": str(wiki_root),
    }

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
