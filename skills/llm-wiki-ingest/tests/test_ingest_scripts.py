from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SKILL_DIR = Path(__file__).resolve().parents[1]
SEARCH_SCRIPT = SKILL_DIR / "scripts" / "wiki_cli_search.py"
VALIDATE_SCRIPT = SKILL_DIR / "scripts" / "validate_ingest_contract.py"


def load_script(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class IngestScriptTests(unittest.TestCase):
    def test_search_falls_back_to_python_when_rg_is_missing(self):
        module = load_script(SEARCH_SCRIPT, "wiki_cli_search")
        with tempfile.TemporaryDirectory() as td:
            wiki = Path(td)
            target = wiki / "domains" / "电商运营" / "index.md"
            target.parent.mkdir(parents=True)
            target.write_text("抖音电商短视频运营与转化", encoding="utf-8")
            with mock.patch.object(module.shutil, "which", return_value=None):
                result = module.filesystem_search(wiki, "抖音 转化", "domains", 10)
            self.assertEqual(result, ["domains/电商运营/index.md"])

    def test_validator_accepts_formal_directory_and_real_coverage_target(self):
        with tempfile.TemporaryDirectory() as td:
            wiki = Path(td) / "wiki"
            notes = wiki / "_meta" / "extraction-notes" / "demo"
            formal_dir = wiki / "domains" / "电商运营" / "演示"
            notes.mkdir(parents=True)
            formal_dir.mkdir(parents=True)
            required = [
                "source-profile.md",
                "source-inventory.md",
                "knowledge-unit-inventory.md",
                "omission-audit.md",
                "formal-page-plan.md",
                "audit-handoff.md",
            ]
            for name in required:
                (notes / name).write_text(f"# {name}\n", encoding="utf-8")
            (notes / "coverage-matrix.md").write_text(
                "| source_unit_id | source_location | source_unit | knowledge_role | target_pages | status | reason_or_notes |\n"
                "| --- | --- | --- | --- | --- | --- | --- |\n"
                "| S01 | 00:01 | 示例知识 | concept | domains/电商运营/演示/页面.md | formalized | represented |\n",
                encoding="utf-8",
            )
            (formal_dir / "页面.md").write_text(
                "---\n"
                "title: 页面\n"
                "type: concept\n"
                "created: 2026-07-15\n"
                "updated: 2026-07-15\n"
                "domain: 电商运营\n"
                "tags: []\n"
                "sources: []\n"
                "status: active\n"
                "---\n\n# 页面\n",
                encoding="utf-8",
            )
            proc = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATE_SCRIPT),
                    "--wiki-root",
                    str(wiki),
                    "--notes-dir",
                    str(notes),
                    "--formal",
                    str(formal_dir),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("contract OK", proc.stdout)
            self.assertNotIn("WARNING", proc.stdout)


if __name__ == "__main__":
    unittest.main()
