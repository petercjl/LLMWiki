#!/usr/bin/env python3
"""Shared EPUB helpers for the llm-wiki-ingest book adapter."""

from __future__ import annotations

import hashlib
import html
import json
import posixpath
import re
import zipfile
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


NS = {
    "container": "urn:oasis:names:tc:opendocument:xmlns:container",
    "opf": "http://www.idpf.org/2007/opf",
    "dc": "http://purl.org/dc/elements/1.1/",
    "ncx": "http://www.daisy.org/z3986/2005/ncx/",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_zip_text(zf: zipfile.ZipFile, name: str) -> str:
    data = zf.read(name)
    for encoding in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def text_of(elem: ET.Element | None) -> str:
    if elem is None:
        return ""
    return "".join(elem.itertext()).strip()


def find_child_by_local(elem: ET.Element, name: str) -> ET.Element | None:
    for child in elem.iter():
        if local_name(child.tag) == name:
            return child
    return None


def norm_path(base: str, href: str) -> str:
    if not base:
        return posixpath.normpath(href)
    return posixpath.normpath(posixpath.join(posixpath.dirname(base), href))


def split_src(src: str) -> tuple[str, str]:
    if "#" in src:
        path, frag = src.split("#", 1)
        return path, frag
    return src, ""


def slugify(value: str, fallback: str = "item") -> str:
    value = html.unescape(value).strip().lower()
    value = re.sub(r"[^\w\s-]", "", value, flags=re.ASCII)
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or fallback


@dataclass
class TocItem:
    id: str
    play_order: int | None
    depth: int
    title: str
    src: str
    file: str
    fragment: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "play_order": self.play_order,
            "depth": self.depth,
            "title": self.title,
            "src": self.src,
            "file": self.file,
            "fragment": self.fragment,
        }


class BasicHTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.in_title = False
        self.title_parts: list[str] = []
        self.heading_level: int | None = None
        self.first_heading = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attrs_dict = {k.lower(): v or "" for k, v in attrs}
        if tag == "title":
            self.in_title = True
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.heading_level = int(tag[1])
            self.parts.append("\n\n" + "#" * self.heading_level + " ")
        elif tag in {"p", "div", "section", "article", "blockquote"}:
            self.parts.append("\n\n")
        elif tag == "li":
            self.parts.append("\n- ")
        elif tag == "br":
            self.parts.append("\n")
        elif tag == "img":
            src = attrs_dict.get("src")
            if src:
                self.parts.append(f"\n\n[image: {src}]\n\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self.in_title = False
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.heading_level = None
            self.parts.append("\n\n")
        elif tag in {"p", "div", "section", "article", "blockquote", "li"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        data = re.sub(r"\s+", " ", data)
        if not data.strip():
            return
        if self.in_title:
            self.title_parts.append(data.strip())
            return
        if self.heading_level and not self.first_heading:
            self.first_heading = data.strip()
        self.parts.append(data)

    def text(self) -> str:
        raw = "".join(self.parts)
        raw = raw.replace("\r\n", "\n").replace("\r", "\n")
        raw = re.sub(r"[ \t]+\n", "\n", raw)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        return raw.strip() + "\n"

    def html_title(self) -> str:
        return " ".join(self.title_parts).strip()


def html_to_text(markup: str) -> tuple[str, str]:
    parser = BasicHTMLTextExtractor()
    parser.feed(markup)
    parser.close()
    return parser.text(), parser.first_heading or parser.html_title()


def find_opf_path(zf: zipfile.ZipFile) -> str:
    container_xml = read_zip_text(zf, "META-INF/container.xml")
    root = ET.fromstring(container_xml)
    rootfile = root.find(".//container:rootfile", NS)
    if rootfile is None:
        raise ValueError("META-INF/container.xml has no rootfile entry")
    full_path = rootfile.attrib.get("full-path")
    if not full_path:
        raise ValueError("rootfile entry has no full-path")
    return full_path


def parse_opf(zf: zipfile.ZipFile, opf_path: str) -> dict[str, Any]:
    root = ET.fromstring(read_zip_text(zf, opf_path))

    def meta_text(local: str) -> str:
        for elem in root.iter():
            if local_name(elem.tag) == local:
                return text_of(elem)
        return ""

    metadata = {
        "title": meta_text("title"),
        "creator": meta_text("creator"),
        "publisher": meta_text("publisher"),
        "date": meta_text("date"),
        "language": meta_text("language"),
        "identifier": meta_text("identifier"),
        "isbn": "",
    }
    identifiers: list[dict[str, str]] = []
    for elem in root.iter():
        if local_name(elem.tag) == "identifier":
            attrs = {local_name(k): v for k, v in elem.attrib.items()}
            value = text_of(elem)
            identifiers.append({"value": value, **attrs})
            if attrs.get("scheme", "").upper() == "ISBN":
                metadata["isbn"] = value
    metadata["identifiers"] = identifiers

    manifest: dict[str, dict[str, str]] = {}
    for elem in root.iter():
        if local_name(elem.tag) != "item":
            continue
        item_id = elem.attrib.get("id")
        href = elem.attrib.get("href")
        if not item_id or not href:
            continue
        media_type = elem.attrib.get("media-type", "")
        manifest[item_id] = {
            "href": href,
            "path": norm_path(opf_path, href),
            "media_type": media_type,
            "properties": elem.attrib.get("properties", ""),
        }

    spine_elem = find_child_by_local(root, "spine")
    toc_id = spine_elem.attrib.get("toc", "") if spine_elem is not None else ""
    spine: list[dict[str, str]] = []
    if spine_elem is not None:
        for itemref in spine_elem:
            if local_name(itemref.tag) != "itemref":
                continue
            idref = itemref.attrib.get("idref", "")
            item = manifest.get(idref, {})
            spine.append({"idref": idref, **item})

    ncx_path = ""
    if toc_id and toc_id in manifest:
        ncx_path = manifest[toc_id]["path"]
    else:
        for item in manifest.values():
            if item.get("media_type") == "application/x-dtbncx+xml":
                ncx_path = item["path"]
                break

    html_files = [
        item["path"]
        for item in manifest.values()
        if item.get("media_type") in {"application/xhtml+xml", "text/html"}
    ]
    image_files = [
        item["path"]
        for item in manifest.values()
        if item.get("media_type", "").startswith("image/")
    ]

    return {
        "opf_path": opf_path,
        "metadata": metadata,
        "manifest": manifest,
        "spine": spine,
        "ncx_path": ncx_path,
        "html_files": html_files,
        "image_files": image_files,
    }


def parse_ncx(zf: zipfile.ZipFile, ncx_path: str) -> list[TocItem]:
    if not ncx_path:
        return []
    root = ET.fromstring(read_zip_text(zf, ncx_path))
    items: list[TocItem] = []

    def walk(node: ET.Element, depth: int) -> None:
        for child in node:
            if local_name(child.tag) != "navPoint":
                continue
            label = ""
            src = ""
            for sub in child.iter():
                if local_name(sub.tag) == "text" and not label:
                    label = text_of(sub)
                elif local_name(sub.tag) == "content" and not src:
                    src = sub.attrib.get("src", "")
            file_part, fragment = split_src(src)
            play_order_raw = child.attrib.get("playOrder")
            try:
                play_order = int(play_order_raw) if play_order_raw else None
            except ValueError:
                play_order = None
            items.append(
                TocItem(
                    id=child.attrib.get("id", ""),
                    play_order=play_order,
                    depth=depth,
                    title=label,
                    src=src,
                    file=norm_path(posixpath.dirname(ncx_path) + "/", file_part),
                    fragment=fragment,
                )
            )
            walk(child, depth + 1)

    nav_map = find_child_by_local(root, "navMap")
    if nav_map is not None:
        walk(nav_map, 1)
    return items


def inspect_epub(epub_path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(epub_path) as zf:
        names = zf.namelist()
        opf_path = find_opf_path(zf)
        opf = parse_opf(zf, opf_path)
        toc = parse_ncx(zf, opf["ncx_path"])
        warnings: list[str] = []
        if not toc:
            warnings.append("No NCX table of contents found")
        if not opf["spine"]:
            warnings.append("No spine entries found")
        if not opf["metadata"].get("title"):
            warnings.append("Missing dc:title")

        return {
            "source_path": str(epub_path),
            "sha256": sha256_file(epub_path),
            "zip_file_count": len(names),
            "opf_path": opf_path,
            "ncx_path": opf["ncx_path"],
            "metadata": opf["metadata"],
            "counts": {
                "spine_items": len(opf["spine"]),
                "toc_items": len(toc),
                "html_files": len(opf["html_files"]),
                "image_files": len(opf["image_files"]),
            },
            "spine": opf["spine"],
            "toc": [item.as_dict() for item in toc],
            "html_files": opf["html_files"],
            "image_files": opf["image_files"],
            "warnings": warnings,
        }


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
