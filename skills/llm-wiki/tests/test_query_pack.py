from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "wiki_cli_search.py"


class QueryPackTests(unittest.TestCase):
    def make_wiki(self, root: Path) -> Path:
        wiki = root / "wiki"
        (wiki / "queries").mkdir(parents=True)
        detail = wiki / "domains" / "电商运营" / "抖音电商" / "短视频运营"
        detail.mkdir(parents=True)
        (wiki / "raw" / "transcripts").mkdir(parents=True)
        (wiki / "SCHEMA.md").write_text("# Schema\n", encoding="utf-8")
        (wiki / "index.md").write_text(
            "# Index\n- [[domains/电商运营/抖音电商/短视频运营/index|短视频运营]]\n",
            encoding="utf-8",
        )
        (wiki / "log.md").write_text("# Log\n", encoding="utf-8")
        (wiki / "queries" / "抖音短视频运营诊断.md").write_text(
            "# 抖音短视频运营诊断\n"
            "- [[domains/电商运营/抖音电商/短视频运营/01-流量与曝光|流量与曝光]]\n"
            "- [[domains/电商运营/抖音电商/短视频运营/02-转化路径|转化路径]]\n",
            encoding="utf-8",
        )
        (wiki / "queries" / "AI短视频制作.md").write_text(
            "# AI短视频制作\n介绍短视频生成工具和制作流程。\n",
            encoding="utf-8",
        )
        (detail / "index.md").write_text("# 短视频运营\n", encoding="utf-8")
        (detail / "01-流量与曝光.md").write_text("# 流量与曝光\n抖音短视频曝光和流量池。\n", encoding="utf-8")
        (detail / "02-转化路径.md").write_text("# 转化路径\n短视频提升转化的方法。\n", encoding="utf-8")
        (wiki / "raw" / "transcripts" / "噪声.md").write_text(
            "抖音 曝光 转化 " * 100,
            encoding="utf-8",
        )
        return wiki

    def run_script(self, wiki: Path, query: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), query, "--wiki", str(wiki)],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_chinese_query_prefers_query_route_and_linked_pages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = self.make_wiki(Path(tmp))
            result = self.run_script(wiki, "抖音短视频怎么放大曝光和提升转化？")
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["backend"], "python-stdlib")
            self.assertEqual(data["query_pages"][0], "queries/抖音短视频运营诊断.md")
            self.assertNotIn("queries/AI短视频制作.md", data["query_pages"])
            self.assertIn("domains/电商运营/抖音电商/短视频运营/01-流量与曝光.md", data["linked_pages"])
            self.assertIn("domains/电商运营/抖音电商/短视频运营/02-转化路径.md", data["linked_pages"])
            self.assertFalse(any(path.startswith("raw/") for path in data["recommended_read_order"]))

    def test_invalid_root_returns_structured_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_script(Path(tmp) / "missing", "测试")
            self.assertEqual(result.returncode, 2)
            data = json.loads(result.stdout)
            self.assertEqual(data["error"], "invalid-wiki-root")


if __name__ == "__main__":
    unittest.main()
