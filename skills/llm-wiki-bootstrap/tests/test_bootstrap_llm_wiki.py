from __future__ import annotations

import importlib.util
import json
import os
import subprocess
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
            ["python3", str(SCRIPT), *args],
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
                "--json",
                env=env,
            )
            self.assertEqual(code, 0)
            self.assertEqual(result["git"]["status"], "skipped")
            self.assertFalse((wiki / ".git").exists())
            self.assertEqual(fake_obsidian_config.read_text(encoding="utf-8"), sentinel)
            self.assertFalse(result["obsidian_register"]["requested"])
            self.assertTrue((wiki / "domains" / "电商运营" / "index.md").exists())
            agents = (wiki / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("only official LLM Wiki", agents)
            self.assertIn("做成知识库", agents)

    def test_git_is_opt_in(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            code, result = self.run_script(
                "--wiki-root",
                str(root / "wiki"),
                "--config-path",
                str(root / "config.env"),
                "--git",
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
        self.assertEqual(status["process"], "AMD64")

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


if __name__ == "__main__":
    unittest.main()
