#!/usr/bin/env python3
"""Extract XMind topic trees to Markdown and JSONL inventories."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


def walk_json_topic(topic: dict, path: list[str], depth: int, rows: list[dict], sheet: str) -> None:
    title = topic.get("title") or ""
    topic_id = topic.get("id") or ""
    current_path = path + [title]
    image = topic.get("image") or {}
    rows.append(
        {
            "sheet": sheet,
            "id": topic_id,
            "parent_path": " / ".join(path),
            "node_path": " / ".join(current_path),
            "depth": depth,
            "title": title,
            "notes": topic.get("notes", {}),
            "labels": topic.get("labels", []),
            "markers": topic.get("markers", []),
            "href": topic.get("href", ""),
            "image_src": image.get("src", "") if isinstance(image, dict) else "",
        }
    )
    children = topic.get("children", {})
    attached = children.get("attached", []) if isinstance(children, dict) else []
    for child in attached:
        walk_json_topic(child, current_path, depth + 1, rows, sheet)


def extract_content_json(zf: zipfile.ZipFile) -> list[dict]:
    data = json.loads(zf.read("content.json").decode("utf-8"))
    sheets = data if isinstance(data, list) else [data]
    rows: list[dict] = []
    for sheet in sheets:
        sheet_title = sheet.get("title") or "Sheet"
        root = sheet.get("rootTopic") or {}
        walk_json_topic(root, [], 0, rows, sheet_title)
    return rows


def extract_content_xml(zf: zipfile.ZipFile) -> list[dict]:
    xml = zf.read("content.xml")
    root = ET.fromstring(xml)
    ns = {"x": "urn:xmind:xmap:xmlns:content:2.0"}
    rows: list[dict] = []

    def topic_title(topic: ET.Element) -> str:
        title = topic.find("x:title", ns)
        return title.text.strip() if title is not None and title.text else ""

    def walk(topic: ET.Element, path: list[str], depth: int, sheet: str) -> None:
        title = topic_title(topic)
        topic_id = topic.attrib.get("id", "")
        current_path = path + [title]
        image = topic.find("x:image", ns)
        rows.append(
            {
                "sheet": sheet,
                "id": topic_id,
                "parent_path": " / ".join(path),
                "node_path": " / ".join(current_path),
                "depth": depth,
                "title": title,
                "notes": "",
                "labels": [],
                "markers": [],
                "href": topic.attrib.get("href", ""),
                "image_src": image.attrib.get("src", "") if image is not None else "",
            }
        )
        for child in topic.findall(".//x:children/x:topics[@type='attached']/x:topic", ns):
            parent = child.find("../..")
            if parent is not None:
                pass
        attached = topic.find("x:children/x:topics[@type='attached']", ns)
        if attached is not None:
            for child in attached.findall("x:topic", ns):
                walk(child, current_path, depth + 1, sheet)

    for sheet in root.findall("x:sheet", ns):
        sheet_title_el = sheet.find("x:title", ns)
        sheet_title = sheet_title_el.text.strip() if sheet_title_el is not None and sheet_title_el.text else "Sheet"
        topic = sheet.find("x:topic", ns)
        if topic is not None:
            walk(topic, [], 0, sheet_title)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("xmind")
    parser.add_argument("--out-jsonl")
    parser.add_argument("--out-md")
    args = parser.parse_args()

    xmind_path = Path(args.xmind)
    with zipfile.ZipFile(xmind_path) as zf:
        names = set(zf.namelist())
        if "content.json" in names:
            rows = extract_content_json(zf)
        elif "content.xml" in names:
            rows = extract_content_xml(zf)
        else:
            raise SystemExit("Unsupported XMind file: no content.json or content.xml")

    if args.out_jsonl:
        Path(args.out_jsonl).write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
    if args.out_md:
        lines = ["| node_id | sheet | depth | node_path | title | image_src |", "| --- | --- | --- | --- | --- | --- |"]
        for row in rows:
            lines.append(f"| {row['id']} | {row['sheet']} | {row['depth']} | {row['node_path']} | {row['title']} | {row.get('image_src', '')} |")
        Path(args.out_md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"nodes: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
