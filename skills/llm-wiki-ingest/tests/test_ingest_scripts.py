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
VALIDATE_WRAPPER = SKILL_DIR / "scripts" / "run_ingest_validation.sh"
ROUTE_SCRIPT = SKILL_DIR / "scripts" / "wiki_cli_route_audit.py"
SKILL_FILE = SKILL_DIR / "SKILL.md"
VIDEO_REFERENCE = SKILL_DIR / "references" / "transcript" / "video-course-ingest.md"


def load_script(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def audit_handoff_text() -> str:
    return (
        "---\n"
        "title: Demo audit handoff\n"
        "type: source-summary\n"
        "created: 2026-07-15\n"
        "updated: 2026-07-15\n"
        "domain: meta\n"
        "tags: [llm-wiki, audit-handoff]\n"
        "sources:\n  - raw/demo/source.txt\n"
        "status: active\n"
        "---\n\n# Demo Audit Handoff\n\n"
        "## Source\n- Adapter: demo\n\n"
        "## Outputs\n- Formal pages: domains/demo/page.md\n\n"
        "## Placement Confirmation\n"
        "- User confirmation: yes\n"
        "- Confirmation evidence: explicit reply\n"
        "- Final confirmed path: domains/demo/\n\n"
        "## Coverage Summary\n- Source units: 1\n\n"
        "## Expected Agent Use\n- Future questions this source should support: demo\n\n"
        "## Known Risks\n- Remaining uncertainty: none\n\n"
        "## Self-Validation\n"
        "- No formal write before placement confirmation: yes\n"
        "- Placeholder scan: passed\n"
        "- Representative term search: passed\n"
        "- Index/log check: passed\n"
        "- Remaining gaps: none\n"
    )


class IngestScriptTests(unittest.TestCase):
    def test_skill_forbids_unexpanded_paths_in_file_tools(self):
        text = SKILL_FILE.read_text(encoding="utf-8")
        self.assertIn("Never pass an unexpanded home shortcut", text)
        self.assertIn("Do not send a path beginning with `~`", text)
        self.assertIn("From the resolved installed Skill root", text)

    def test_video_reference_forbids_buffered_long_running_output(self):
        text = VIDEO_REFERENCE.read_text(encoding="utf-8")
        self.assertIn("do not pipe the native command through", text)
        self.assertIn("`Select-Object -Last`", text)
        self.assertIn("exit code `0`", text)
        self.assertIn("Do not run them concurrently", text)
        self.assertIn("audio extraction, ASR, keyframe extraction, then OCR", text)

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
            ]
            for name in required:
                (notes / name).write_text(f"# {name}\n", encoding="utf-8")
            (notes / "knowledge-unit-inventory.md").write_text(
                "| ID | knowledge | disposition |\n"
                "| --- | --- | --- |\n"
                "| S01 | 示例知识 | formalized |\n",
                encoding="utf-8",
            )
            (notes / "audit-handoff.md").write_text(audit_handoff_text(), encoding="utf-8")
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
                "sources:\n"
                "  - raw/demo/source.txt\n"
                "  - _meta/extraction-notes/demo/coverage-matrix.md\n"
                "status: active\n"
                "---\n\n# 页面\n\n" + ("这是经过整理、可以供未来 Agent 直接使用的有效知识内容。" * 40) + "\n",
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

            wrapper_proc = subprocess.run(
                [
                    "bash",
                    str(VALIDATE_WRAPPER),
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
            self.assertEqual(wrapper_proc.returncode, 0, wrapper_proc.stdout + wrapper_proc.stderr)
            self.assertIn("Validated Python:", wrapper_proc.stdout)
            self.assertIn("contract OK", wrapper_proc.stdout)

    def test_validator_rejects_placeholder_in_formal_index(self):
        with tempfile.TemporaryDirectory() as td:
            wiki = Path(td) / "wiki"
            notes = wiki / "_meta" / "extraction-notes" / "demo"
            formal_dir = wiki / "domains" / "电商运营" / "演示"
            notes.mkdir(parents=True)
            formal_dir.mkdir(parents=True)
            for name in [
                "source-profile.md",
                "source-inventory.md",
                "knowledge-unit-inventory.md",
                "omission-audit.md",
                "formal-page-plan.md",
                "audit-handoff.md",
            ]:
                (notes / name).write_text(f"# {name}\n", encoding="utf-8")
            (notes / "coverage-matrix.md").write_text(
                "| source_unit_id | source_location | source_unit | knowledge_role | target_pages | status | reason_or_notes |\n"
                "| --- | --- | --- | --- | --- | --- | --- |\n"
                "| S01 | 00:01 | 示例知识 | concept | domains/电商运营/演示/index.md | formalized | represented |\n",
                encoding="utf-8",
            )
            (formal_dir / "index.md").write_text(
                "---\n"
                "title: 页面\n"
                "type: index\n"
                "created: 2026-07-15\n"
                "updated: 2026-07-15\n"
                "domain: 电商运营\n"
                "tags: []\n"
                "sources:\n"
                "  - raw/demo/source.txt\n"
                "  - _meta/extraction-notes/demo/coverage-matrix.md\n"
                "status: active\n"
                "---\n\n# 页面\n\n后续内容待补充。\n",
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
            self.assertEqual(proc.returncode, 1)
            self.assertIn("placeholder or boilerplate marker present", proc.stdout)

    def test_route_audit_rejects_cli_error_with_zero_exit(self):
        module = load_script(ROUTE_SCRIPT, "wiki_cli_route_audit")
        with mock.patch.object(module, "run", return_value=(0, 'Error: Command "vault" not found', "")):
            status = module.cli_status(Path("/tmp/wiki"))
        self.assertFalse(status["available"])
        self.assertFalse(status["trusted"])
        self.assertIn("Command", status["error"])

    def test_route_audit_rejects_file_error_as_cli_lines(self):
        module = load_script(ROUTE_SCRIPT, "wiki_cli_route_audit_lines")
        with mock.patch.object(module, "run", return_value=(0, 'Error: File "missing.md" not found.', "")):
            self.assertEqual(module.cli_lines(["obsidian", "links"]), [])

    def test_route_audit_normalizes_absolute_target_path(self):
        module = load_script(ROUTE_SCRIPT, "wiki_cli_route_audit_paths")
        with tempfile.TemporaryDirectory() as td:
            wiki = Path(td) / "wiki"
            target = wiki / "queries" / "demo.md"
            target.parent.mkdir(parents=True)
            target.write_text("# demo\n", encoding="utf-8")
            self.assertEqual(module.normalize_route_path(wiki.resolve(), str(target.resolve())), "queries/demo.md")


if __name__ == "__main__":
    unittest.main()
