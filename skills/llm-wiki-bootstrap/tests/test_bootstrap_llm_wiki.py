from __future__ import annotations

import importlib.util
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "bootstrap_llm_wiki.py"


def load_module():
    spec = importlib.util.spec_from_file_location("bootstrap_llm_wiki", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class BootstrapTests(unittest.TestCase):
    def run_script(self, *args: str, env: dict[str, str] | None = None) -> tuple[int, dict]:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        self.assertTrue(proc.stdout, proc.stderr)
        return proc.returncode, json.loads(proc.stdout)

    def test_check_only_does_not_write(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            wiki = root / "wiki"
            config = root / "config.env"
            code, result = self.run_script(
                "--check-only", "--wiki-root", str(wiki), "--config-path", str(config)
            )
            self.assertEqual(code, 0)
            self.assertFalse(wiki.exists())
            self.assertFalse(config.exists())
            self.assertEqual(result["inspection_mode"], "read-only")
            self.assertFalse(result["current_state"]["wiki_root_exists"])
            self.assertEqual(result["current_state"]["existing_config_paths"], [])
            self.assertTrue({"WIKI_ROOT", "LLMWIKI_SKILL_SOURCE"}.issubset(result["config"]))
            self.assertIn("architecture", result["tools"])
            self.assertIn("media", result["tools"])

    def test_real_bootstrap_skips_git_and_registry(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            wiki = root / "wiki"
            config = root / "config.env"
            fake_obsidian_config = root / "obsidian.json"
            sentinel = '{"vaults":{"keep":{"path":"/keep"}}}'
            fake_obsidian_config.write_text(sentinel, encoding="utf-8")
            env = os.environ.copy()
            env["OBSIDIAN_CONFIG_PATH"] = str(fake_obsidian_config)
            code, result = self.run_script(
                "--wiki-root",
                str(wiki),
                "--config-path",
                str(config),
                "--domain",
                "电商运营",
                "--allow-degraded-bootstrap",
                "--json",
                env=env,
            )
            self.assertEqual(code, 0)
            self.assertEqual(result["git"]["status"], "skipped")
            self.assertFalse((wiki / ".git").exists())
            self.assertEqual(fake_obsidian_config.read_text(encoding="utf-8"), sentinel)
            self.assertFalse(result["obsidian_register"]["requested"])
            self.assertTrue((wiki / "domains" / "电商运营" / "index.md").exists())
            self.assertTrue((wiki / "TOOLS.md").exists())
            agents = (wiki / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("only official LLM Wiki", agents)
            self.assertIn("做成知识库", agents)

    def test_windows_config_includes_execution_policy_independent_json(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as td:
            with mock.patch.object(module, "user_home", return_value=Path(td)):
                paths = module.config_paths("windows")
                self.assertEqual(paths[0].name, "config.json")
                written = module.write_config_files(
                    paths,
                    {"WIKI_ROOT": r"C:\Users\learner\wiki"},
                    force=False,
                    dry_run=False,
                )
            self.assertEqual(len(written), 3)
            data = json.loads((Path(td) / ".llmwiki" / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(data["WIKI_ROOT"], r"C:\Users\learner\wiki")

    def test_check_only_lists_even_empty_target_subdirectories(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            wiki = root / "wiki"
            (wiki / "_meta").mkdir(parents=True)
            code, result = self.run_script(
                "--check-only",
                "--wiki-root",
                str(wiki),
                "--config-path",
                str(root / "config.env"),
            )
            self.assertEqual(code, 0)
            self.assertFalse(result["current_state"]["wiki_root_empty"])
            self.assertEqual(result["current_state"]["wiki_root_entries"], ["_meta"])
            self.assertFalse(result["readiness"]["target_ready"])

    def test_required_toolchain_gate_blocks_before_any_write(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            wiki = root / "wiki"
            config = root / "config.env"
            env = os.environ.copy()
            env["PATH"] = ""
            env["HOME"] = str(root / "home")
            env.pop("WHISPER_MODEL", None)
            env.pop("LLMWIKI_MEDIA_BIN", None)
            code, result = self.run_script(
                "--wiki-root",
                str(wiki),
                "--config-path",
                str(config),
                env=env,
            )
            self.assertEqual(code, 3)
            self.assertEqual(result["readiness_gate"], "blocked-before-write")
            self.assertFalse(wiki.exists())
            self.assertFalse(config.exists())

    def test_whisper_canary_requires_real_output_file(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fake = root / "whisper-cli"
            fake.write_text(
                "#!/bin/sh\n"
                "out=''\n"
                "while [ $# -gt 0 ]; do\n"
                "  if [ \"$1\" = '-of' ]; then shift; out=\"$1\"; fi\n"
                "  shift\n"
                "done\n"
                "[ -n \"$out\" ] && : > \"${out}.txt\"\n",
                encoding="utf-8",
            )
            fake.chmod(0o755)
            model = root / "model.bin"
            model.write_bytes(b"model")
            result = module.whisper_canary(str(fake), str(model))
            self.assertTrue(result["passed"])

    def test_git_is_opt_in(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            code, result = self.run_script(
                "--wiki-root",
                str(root / "wiki"),
                "--config-path",
                str(root / "config.env"),
                "--git",
                "--allow-degraded-bootstrap",
                "--json",
            )
            self.assertEqual(code, 0)
            self.assertIn(result["git"]["status"], {"initialized", "missing-git"})

    def test_windows_native_architecture_is_not_process_architecture(self):
        module = load_module()
        with mock.patch.dict(
            os.environ,
            {"PROCESSOR_ARCHITEW6432": "ARM64", "PROCESSOR_ARCHITECTURE": "AMD64"},
            clear=False,
        ), mock.patch.object(module.platform, "machine", return_value="AMD64"):
            status = module.architecture_status("windows")
        self.assertEqual(status["native"], "ARM64")
        self.assertEqual(status["launcher_environment"], "AMD64")
        self.assertEqual(status["python_checker"], "AMD64")

    def test_windows_system_commands_are_not_media_tools(self):
        module = load_module()
        with mock.patch.object(module.shutil, "which") as which:
            which.side_effect = lambda name: {
                "main": r"C:\\Windows\\System32\\main.cpl",
                "convert": r"C:\\Windows\\System32\\convert.exe",
            }.get(name)
            result = module.detect_media_toolchain()
        self.assertFalse(result["local_asr"]["installed"])
        self.assertEqual(result["local_asr"]["command"], "")
        self.assertFalse(result["imagemagick_optional"]["installed"])
        self.assertEqual(result["imagemagick_optional"]["command"], "")

    def test_windows_obsidian_cli_prefers_com_redirector(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as td:
            app = Path(td) / "Obsidian.exe"
            cli = Path(td) / "Obsidian.com"
            app.touch()
            cli.touch()
            with mock.patch.object(module, "run", return_value=(0, "backlinks search vault", "")):
                result = module.detect_obsidian_cli("windows", {"installed": True, "paths": [str(app)]})
        self.assertTrue(result["installed"])
        self.assertEqual(result["commands"][0], str(cli))

    def test_windows_obsidian_helper_enforces_single_verified_download(self):
        helper = SKILL_DIR / "scripts" / "install_obsidian_windows.ps1"
        text = helper.read_text(encoding="utf-8")
        self.assertIn("Get-AuthenticodeSignature", text)
        self.assertIn("Get-FileHash -Algorithm SHA256", text)
        self.assertIn("FileShare]::None", text)
        self.assertIn("curl.exe", text)
        self.assertNotIn("Start-BitsTransfer", text)

    def test_pe_architecture_detection_distinguishes_arm64_and_x64(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for machine, expected in [(0xAA64, "ARM64"), (0x8664, "x64")]:
                binary = root / f"{expected}.exe"
                data = bytearray(0x90)
                data[0:2] = b"MZ"
                data[0x3C:0x40] = struct.pack("<I", 0x80)
                data[0x80:0x84] = b"PE\x00\x00"
                data[0x84:0x86] = struct.pack("<H", machine)
                binary.write_bytes(data)
                self.assertEqual(module.binary_architecture(str(binary)), expected)


if __name__ == "__main__":
    unittest.main()
