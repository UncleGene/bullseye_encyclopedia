#!/usr/bin/env python3
"""Build the EPUB export from normalized Bullseye content."""

from __future__ import annotations

import argparse
import html
import json
import mimetypes
import os
import posixpath
import re
import shutil
import subprocess
import sys
import zipfile
from collections import OrderedDict
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urldefrag, urljoin, urlparse


COMBINED_BACKUP = Path("archive/raw/wayback/manifests/20260522T-combined-backup-blobs.json")

# Sub-articles nested under a specific parent article, matching raw-site subdirectory structure.
SUBGROUP_INJECTIONS: dict[str, list[str]] = {
    "amucover":  ["chapterf", "chapter0", "chapter1", "chapter2", "chapter3", "chapter4",
                  "chapter5", "chapter6", "chapter7", "chapter8", "chapter9", "chapter10",
                  "annex2", "glossary"],
    "amuprfil":  ["profile1", "profile2", "profile3", "profile4", "profile5", "profile6", "profile7"],
    "mikelav1":  ["mikelav2"],
    "savino2":   ["savino"],
    "wong":      ["wong1", "wong2", "wong3", "wong4", "wong5", "wong6", "wong7", "wongbio"],
    "zins":      ["zins1"],
}

RAW_INDEX = Path(
    "archive/raw/wayback/files/20260522T143136Z/202508/article_candidate/"
    "www.bullseyepistol.com/20250818003737-index-5fffb450c2814c7e.html"
)
ARTICLE_INDEX = Path("content/canonical/articles.index.json")
ARTICLE_DIR = Path("content/canonical/articles")
ASSET_INDEX = Path("content/assets/assets.index.json")
CANONICAL_REPORT = Path("exports/static-site/raw/_raw-export-report.json")
OUT_DIR = Path("exports/ebook")
EPUB_NAME = "bullseye-pistol.epub"
SUPPORTED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/svg+xml": ".svg",
}
SECTION_RE = re.compile(r'<td[^>]*class=["\']nav["\'][^>]*>(.*?)</td>', re.IGNORECASE | re.DOTALL)
ART_RE = re.compile(r'<td[^>]*class=["\']art["\'][^>]*>(.*?)</td>', re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")

_EPUB_INLINE_TAGS = frozenset(["b", "strong", "i", "em", "u", "s", "strike", "sup", "sub", "code", "tt", "small", "big"])


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attrs_map = {name.lower(): value or "" for name, value in attrs}
        href = attrs_map.get("href")
        if href:
            self._href = html.unescape(href)
            self._text = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href:
            self.links.append({"href": self._href, "text": clean_text(" ".join(self._text))})
            self._href = None
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href:
            self._text.append(data)


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = {name.lower(): value or "" for name, value in attrs}
        for attr in ("href", "src"):
            value = attrs_map.get(attr)
            if value:
                self.refs.append({"tag": tag.lower(), "attr": attr, "value": html.unescape(value)})


class EbookBodyParser(HTMLParser):
    def __init__(
        self,
        article: dict[str, Any],
        article_map: dict[str, dict[str, Any]],
        assets: dict[str, dict[str, Any]],
        copied_assets: dict[str, str],
        resource_records: dict[str, dict[str, Any]],
        out_root: Path,
        report: dict[str, Any],
    ) -> None:
        super().__init__()
        self.article = article
        self.article_map = article_map
        self.assets = assets
        self.copied_assets = copied_assets
        self.resource_records = resource_records
        self.out_root = out_root
        self.report = report
        self.blocks: list[str] = []
        self.chapter_asset_paths: list[str] = []
        self.rendered_asset_ids: set[str] = set()
        self._buf: list[str] = []
        self._inline_stack: list[str] = []
        self._last_break = False
        self._skip_depth = 0
        self._font_stack: list[dict] = []  # {white: bool, heading: bool}
        self._in_heading = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag_l = tag.lower()
        if tag_l in {"script", "style"}:
            self._skip_depth += 1
            return
        if tag_l == "font":
            d = {k.lower(): (v or "") for k, v in attrs}
            color = d.get("color", "").lower().replace(" ", "")
            is_white = color in {"white", "#fff", "#ffffff"}
            size_str = d.get("size", "").lstrip("+-")
            size = int(size_str) if size_str.isdigit() else 0
            is_heading = (not is_white) and (size >= 4)
            self._font_stack.append({"white": is_white, "heading": is_heading})
            if is_white:
                self._skip_depth += 1
            elif is_heading:
                self._flush_buf()
                self._in_heading = True
            return
        if self._skip_depth:
            return
        if tag_l in {"p", "div", "center", "table", "tr", "li", "blockquote", "h1", "h2", "h3", "h4", "hr", "pre"}:
            self._flush_buf()
            return
        if tag_l == "br":
            if self._last_break:
                self._flush_buf()
            else:
                self._buf.append(" ")
                self._last_break = True
            return
        if tag_l == "img":
            attrs_map = {name.lower(): value or "" for name, value in attrs}
            self._flush_buf()
            self.render_image(attrs_map)
            return
        if self._in_heading:
            return  # content passes through; inline markup inside headings is stripped
        if tag_l in _EPUB_INLINE_TAGS:
            self._buf.append(f"<{tag_l}>")
            self._inline_stack.append(tag_l)
            return
        if tag_l == "a":
            href = self._resolve_href(attrs)
            if href:
                self._buf.append(f'<a href="{html.escape(href, quote=True)}">')
                self._inline_stack.append("a")

    def handle_endtag(self, tag: str) -> None:
        tag_l = tag.lower()
        if tag_l == "font":
            if self._font_stack:
                info = self._font_stack.pop()
                if info["white"] and self._skip_depth > 0:
                    self._skip_depth -= 1
                elif info["heading"] and self._in_heading:
                    content = "".join(self._buf).strip()
                    if content:
                        self.blocks.append(f"<h2>{content}</h2>")
                    self._buf = []
                    self._inline_stack.clear()
                    self._in_heading = False
            return
        if tag_l in {"script", "style"} and self._skip_depth:
            self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if tag_l in {"p", "div", "center", "table", "tr", "li", "blockquote", "h1", "h2", "h3", "h4", "hr", "pre"}:
            self._flush_buf()
            return
        if self._in_heading:
            return
        if tag_l in _EPUB_INLINE_TAGS:
            if self._inline_stack and self._inline_stack[-1] == tag_l:
                self._inline_stack.pop()
                self._buf.append(f"</{tag_l}>")
            return
        if tag_l == "a":
            if self._inline_stack and self._inline_stack[-1] == "a":
                self._inline_stack.pop()
                self._buf.append("</a>")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = SPACE_RE.sub(" ", html.unescape(data or ""))
        if not text.strip():
            if text and self._buf and not self._in_heading:
                self._buf.append(html.escape(text))
            return
        if self._in_heading:
            self._buf.append(html.escape(text.strip()))
        else:
            self._buf.append(html.escape(text))
            self._last_break = False

    def _flush_buf(self) -> None:
        for tag in reversed(self._inline_stack):
            self._buf.append(f"</{tag}>")
        self._inline_stack.clear()
        content = "".join(self._buf).strip()
        if content:
            self.blocks.append(f"<p>{content}</p>")
        self._buf = []
        self._last_break = False

    def _resolve_href(self, attrs: list[tuple[str, str | None]]) -> str | None:
        d = {k.lower(): (v or "") for k, v in attrs}
        raw = html.unescape(d.get("href", ""))
        if not raw or raw.startswith("#"):
            return None
        resolved = urljoin(str(self.article.get("preferred_original_url", "")), raw)
        if is_internal_url(resolved):
            target_id = article_id_from_url(resolved)
            if target_id and target_id in self.article_map:
                if target_id == str(self.article["id"]):
                    return None  # self-link — fragment anchor within same article
                return f"../chapters/{target_id}.xhtml"
            normalized = normalize_url(resolved)
            if normalized in self.resource_records:
                self.report["suppressed_internal_resource_links"].append(
                    {"article_id": str(self.article["id"]), "href": resolved, "context": "body-link"}
                )
        return None  # external links and unresolved internals: drop href, keep text

    def render_image(self, attrs: dict[str, str]) -> None:
        src = attrs.get("src", "")
        resolved = normalize_url(urljoin(str(self.article.get("preferred_original_url", "")), src))
        asset_id = None
        alt = attrs.get("alt", "")
        for image in self.article.get("images", []):
            if normalize_url(str(image.get("resolved_url", ""))) == resolved and image.get("asset_ids"):
                asset_id = str(image["asset_ids"][0])
                alt = str(image.get("alt") or alt or "")
                break
        if not asset_id:
            return
        figure = render_asset_figure(
            self.article,
            asset_id,
            alt,
            self.assets,
            self.copied_assets,
            self.out_root,
            self.report,
        )
        if not figure:
            return
        self.blocks.append(figure)
        self.rendered_asset_ids.add(asset_id)
        rel = self.copied_assets[asset_id]
        if rel not in self.chapter_asset_paths:
            self.chapter_asset_paths.append(rel)

    def finish(self) -> tuple[str, list[str], set[str]]:
        self._flush_buf()
        return "".join(self.blocks), self.chapter_asset_paths, self.rendered_asset_ids


def clean_text(value: str) -> str:
    return SPACE_RE.sub(" ", html.unescape(TAG_RE.sub(" ", value or ""))).strip()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_url(url: str) -> str:
    resolved, _fragment = urldefrag(url)
    parsed = urlparse(resolved)
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    if host.endswith(":80"):
        host = host[:-3]
    path = parsed.path or "/"
    if path == "/":
        path = "/index.htm"
    if path.lower().endswith(".html"):
        path = path[:-5] + ".htm"
    return f"http://{host}{path}"


def is_internal_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme and parsed.scheme.lower() not in {"http", "https"}:
        return False
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    if host.endswith(":80"):
        host = host[:-3]
    return not host or host == "bullseyepistol.com"


def article_id_from_url(url: str) -> str | None:
    parsed = urlparse(url)
    if not is_internal_url(url):
        return None
    name = Path(parsed.path).name
    if not name:
        return None
    stem = re.sub(r"\.[A-Za-z0-9]{1,8}$", "", name)
    stem = re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-").lower()
    return stem or None


def best_resource_records(backup: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for record in backup.get("records", []):
        if record.get("status") != "success":
            continue
        original = str(record.get("original", ""))
        if not is_internal_url(original):
            continue
        normalized = normalize_url(original)
        if normalized not in records or str(record.get("timestamp", "")) > str(records[normalized].get("timestamp", "")):
            records[normalized] = record
    return records


def parse_raw_index_sections(path: Path, base_url: str, article_ids: set[str]) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    sections: list[dict[str, Any]] = []
    pos = 0
    while True:
        section_match = SECTION_RE.search(text, pos)
        if not section_match:
            break
        title = clean_text(section_match.group(1)).rstrip(":")
        art_match = ART_RE.search(text, section_match.end())
        if not art_match:
            pos = section_match.end()
            continue
        parser = LinkParser()
        parser.feed(art_match.group(1))
        items = []
        seen: set[str] = set()
        for link in parser.links:
            resolved = urljoin(base_url, link["href"])
            article_id = article_id_from_url(resolved)
            if not article_id or article_id not in article_ids or article_id in seen:
                continue
            seen.add(article_id)
            items.append({"article_id": article_id, "label": link["text"]})
        if items:
            sections.append({"title": title, "items": items})
        pos = art_match.end()
    return sections


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "item"


def chapter_href(article_id: str) -> str:
    return f"chapters/{slug(article_id)}.xhtml"


def xhtml_page(title: str, body: str, stylesheet_href: str = "../styles/ebook.css") -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
<head>
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" type="text/css" href="{html.escape(stylesheet_href)}" />
</head>
<body>
{body}
</body>
</html>
"""


def asset_extension(asset: dict[str, Any]) -> str:
    media_type = str(asset.get("media_type") or "").lower()
    if media_type in SUPPORTED_IMAGE_TYPES:
        return SUPPORTED_IMAGE_TYPES[media_type]
    for source in [str(asset.get("file_path") or ""), *(asset.get("original_urls") or [])]:
        suffix = Path(urlparse(source).path).suffix.lower()
        if suffix in {".jpg", ".jpeg", ".png", ".gif", ".svg"}:
            return ".jpg" if suffix == ".jpeg" else suffix
    return mimetypes.guess_extension(media_type) or ""


def copy_asset(asset: dict[str, Any], out_root: Path, copied: dict[str, str]) -> str | None:
    asset_id = str(asset.get("id") or "")
    if asset_id in copied:
        return copied[asset_id]
    src = Path(str(asset.get("file_path") or ""))
    if not src.exists():
        src = Path(str(asset.get("blob_path") or ""))
    if not src.exists():
        return None
    rel = f"images/{asset_id}{asset_extension(asset)}"
    dst = out_root / "OEBPS" / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)
    copied[asset_id] = rel
    return rel


def article_asset_ids(article: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for image in article.get("images", []):
        for asset_id in image.get("asset_ids", []):
            if asset_id not in ids:
                ids.append(asset_id)
    for asset_id in article.get("assets", []):
        if asset_id not in ids:
            ids.append(asset_id)
    return ids


def render_asset_figure(
    article: dict[str, Any],
    asset_id: str,
    alt: str,
    assets: dict[str, dict[str, Any]],
    copied_assets: dict[str, str],
    out_root: Path,
    report: dict[str, Any],
) -> str | None:
    article_id = str(article["id"])
    asset = assets.get(asset_id)
    if not asset:
        report["missing_assets"].append({"article_id": article_id, "asset_id": asset_id, "reason": "asset record missing"})
        return None
    media_type = str(asset.get("media_type") or "").lower()
    if media_type not in SUPPORTED_IMAGE_TYPES:
        report["unsupported_assets"].append(
            {"article_id": article_id, "asset_id": asset_id, "media_type": media_type, "reason": "unsupported ebook media type"}
        )
        return None
    rel = copy_asset(asset, out_root, copied_assets)
    if not rel:
        report["missing_assets"].append({"article_id": article_id, "asset_id": asset_id, "reason": "local file missing"})
        return None
    caption = f"<figcaption>{html.escape(alt)}</figcaption>" if alt else ""
    return f'<figure><img src="../{html.escape(rel)}" alt="{html.escape(alt)}" />{caption}</figure>'


def build_article_page(
    article: dict[str, Any],
    article_map: dict[str, dict[str, Any]],
    assets: dict[str, dict[str, Any]],
    copied_assets: dict[str, str],
    resource_records: dict[str, dict[str, Any]],
    out_root: Path,
    report: dict[str, Any],
) -> tuple[str, list[str]]:
    article_id = str(article["id"])
    title = str(article.get("title") or article_id)
    meta_parts = []
    if article.get("byline"):
        meta_parts.append(f"By {html.escape(str(article['byline']))}")
    if article.get("published_at"):
        meta_parts.append(f"Published {html.escape(str(article['published_at']))}")
    if article.get("updated_at"):
        meta_parts.append(f"Updated {html.escape(str(article['updated_at']))}")
    meta = f'<p class="meta">{" | ".join(meta_parts)}</p>' if meta_parts else ""
    status_note = ""
    if article.get("status") == "partial":
        status_note = '<p class="recovery-note">Partial recovered article.</p>'

    body_parser = EbookBodyParser(
        article, article_map, assets, copied_assets, resource_records, out_root, report
    )
    body_parser.feed(str(article.get("body", {}).get("html") or ""))
    body_html, chapter_asset_paths, rendered_asset_ids = body_parser.finish()
    fallback_figures = []
    for asset_id in article_asset_ids(article):
        if asset_id in rendered_asset_ids:
            continue
        alt = ""
        for image in article.get("images", []):
            if asset_id in image.get("asset_ids", []):
                alt = str(image.get("alt") or "")
                break
        figure = render_asset_figure(article, asset_id, alt, assets, copied_assets, out_root, report)
        if not figure:
            continue
        fallback_figures.append(figure)
        rel = copied_assets[asset_id]
        if rel not in chapter_asset_paths:
            chapter_asset_paths.append(rel)

    internal_links = []
    external_links = []
    unresolved_internal = []
    for link in article.get("links", []):
        href = str(link.get("resolved_url") or link.get("href") or "")
        label = str(link.get("text") or href)
        target_id = article_id_from_url(href)
        if target_id == article_id:
            continue  # self-referential fragment anchor — no chapter-level target in EPUB
        if target_id and target_id in article_map:
            internal_links.append(f'<li><a href="../{chapter_href(target_id)}">{html.escape(label)}</a></li>')
        elif is_internal_url(href):
            normalized = normalize_url(href)
            if normalized in resource_records:
                report["suppressed_internal_resource_links"].append(
                    {"article_id": article_id, "href": href, "text": label, "context": "reference-list"}
                )
            else:
                report["suppressed_internal_resource_links"].append(
                    {
                        "article_id": article_id,
                        "href": href,
                        "text": label,
                        "context": "reference-list",
                        "reason": "unavailable-internal-resource",
                    }
                )
        elif href:
            external_links.append(f'<li>{html.escape(label)} <small>{html.escape(href)}</small></li>')
    report["unresolved_internal_links"].extend(unresolved_internal)

    link_sections = []
    if internal_links:
        link_sections.append("<section><h2>Internal References</h2><ul>" + "".join(internal_links) + "</ul></section>")
    if external_links:
        link_sections.append("<section><h2>External References</h2><ul>" + "".join(external_links) + "</ul></section>")

    original_url = html.escape(str(article.get("preferred_original_url") or ""))
    body = (
        f"<article><h1>{html.escape(title)}</h1>{meta}{status_note}"
        f'<p class="meta">Original URL: {original_url}</p>'
        f"{body_html}"
        f"{''.join(fallback_figures)}"
        f"{''.join(link_sections)}</article>"
    )
    return xhtml_page(title, body), chapter_asset_paths


def build_provenance(articles: list[dict[str, Any]], report: dict[str, Any]) -> str:
    items = []
    for article in articles:
        captures = article.get("provenance", {}).get("captures", [])
        capture_items = "".join(
            "<li>"
            f"{html.escape(str(c.get('wayback_timestamp', '')))} "
            f"{html.escape(str(c.get('original_url', '')))} "
            f"<code>{html.escape(str(c.get('sha256', '')))}</code>"
            "</li>"
            for c in captures
        )
        items.append(
            "<section>"
            f"<h2>{html.escape(str(article.get('title') or article['id']))}</h2>"
            f"<p class=\"meta\">Article ID: {html.escape(str(article['id']))}</p>"
            f"<ul>{capture_items}</ul>"
            "</section>"
        )
    body = (
        "<h1>Provenance</h1>"
        f"<p>Included articles: {report['included_article_count']}. Embedded assets: {report['embedded_asset_count']}.</p>"
        + "".join(items)
    )
    return xhtml_page("Provenance", body, "styles/ebook.css")


def build_nav(sections: list[dict[str, Any]], article_map: dict[str, dict[str, Any]]) -> str:
    section_items = []
    for section in sections:
        links = "".join(
            f'<li><a href="{chapter_href(item["article_id"])}">{html.escape(str(article_map[item["article_id"]].get("title") or item["article_id"]))}</a></li>'
            for item in section["items"]
        )
        section_items.append(f"<li><span>{html.escape(section['title'])}</span><ol>{links}</ol></li>")
    body = (
        '<nav epub:type="toc" id="toc"><h1>Contents</h1><ol>'
        + "".join(section_items)
        + '<li><a href="provenance.xhtml">Provenance</a></li>'
        + "</ol></nav>"
    )
    return xhtml_page("Contents", body, "styles/ebook.css")


def content_opf(manifest: list[dict[str, str]], spine: list[str], build_time: str) -> str:
    manifest_xml = "\n".join(
        f'    <item id="{item["id"]}" href="{html.escape(item["href"])}" media-type="{item["media_type"]}"{item.get("properties", "")}/>'
        for item in manifest
    )
    spine_xml = "\n".join(f'    <itemref idref="{item_id}"/>' for item_id in spine)
    return f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">urn:bullseyepistol:ebook:first-pass</dc:identifier>
    <dc:title>Bullseye Pistol</dc:title>
    <dc:language>en</dc:language>
    <dc:creator>Recovered from bullseyepistol.com canonical content</dc:creator>
    <dc:source>bullseyepistol.com</dc:source>
    <meta property="dcterms:modified">{build_time}</meta>
  </metadata>
  <manifest>
{manifest_xml}
  </manifest>
  <spine>
{spine_xml}
  </spine>
</package>
"""


def write_epub(out_root: Path, epub_path: Path) -> None:
    if epub_path.exists():
        epub_path.unlink()
    with zipfile.ZipFile(epub_path, "w") as zf:
        zf.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        for path in sorted((out_root / "META-INF").rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(out_root).as_posix(), compress_type=zipfile.ZIP_DEFLATED)
        for path in sorted((out_root / "OEBPS").rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(out_root).as_posix(), compress_type=zipfile.ZIP_DEFLATED)


def validate_epub(epub_path: Path, report: dict[str, Any]) -> None:
    checks: list[dict[str, Any]] = []
    skip_schemes = {"http", "https", "mailto", "tel", "javascript", "data"}
    checks.append({"name": "epub_exists", "passed": epub_path.exists(), "path": str(epub_path)})
    with zipfile.ZipFile(epub_path) as zf:
        names = zf.namelist()
        name_set = set(names)
        checks.append({"name": "mimetype_first", "passed": names[:1] == ["mimetype"]})
        checks.append({"name": "container_exists", "passed": "META-INF/container.xml" in names})
        checks.append({"name": "package_exists", "passed": "OEBPS/content.opf" in names})
        checks.append({"name": "nav_exists", "passed": "OEBPS/nav.xhtml" in names})
        missing_embedded = [path for path in report["embedded_asset_paths"] if f"OEBPS/{path}" not in names]
        checks.append({"name": "embedded_assets_exist", "passed": not missing_embedded, "missing": missing_embedded})
        missing_chapters = [path for path in report["chapter_paths"] if f"OEBPS/{path}" not in names]
        checks.append({"name": "chapters_exist", "passed": not missing_chapters, "missing": missing_chapters})
        broken_refs = []
        local_ref_count = 0
        external_ref_count = 0
        legacy_prewrap_chapters = []
        hard_wrap_candidates = []
        visible_asset_id_captions = []
        for name in sorted(n for n in names if n.startswith("OEBPS/") and n.endswith(".xhtml")):
            source = zf.read(name).decode("utf-8")
            if '<div class="article-text">' in source:
                legacy_prewrap_chapters.append(name)
            text_only = TAG_RE.sub("", source)
            if re.search(r"\b\w{3,}\n\w{3,}\n\w{3,}", text_only):
                hard_wrap_candidates.append(name)
            for caption in re.findall(r"<figcaption>(.*?)</figcaption>", source, flags=re.IGNORECASE | re.DOTALL):
                caption_text = clean_text(caption)
                if re.fullmatch(r"asset-[0-9a-f]{16}", caption_text):
                    visible_asset_id_captions.append({"file": name, "caption": caption_text})
            parser = ReferenceParser()
            parser.feed(source)
            base = posixpath.dirname(name)
            for ref in parser.refs:
                parsed = urlparse(ref["value"])
                if parsed.scheme in skip_schemes or parsed.netloc:
                    external_ref_count += 1
                    continue
                if not parsed.path:
                    continue
                local_ref_count += 1
                target = posixpath.normpath(posixpath.join(base, parsed.path))
                if target not in name_set:
                    broken_refs.append({"file": name, "reference": ref["value"], "target": target})
        checks.append(
            {
                "name": "local_package_references_resolve",
                "passed": not broken_refs,
                "local_reference_count": local_ref_count,
                "external_reference_count": external_ref_count,
                "broken_references": broken_refs,
            }
        )
        checks.append(
            {
                "name": "no_legacy_prewrapped_chapters",
                "passed": not legacy_prewrap_chapters,
                "chapters": legacy_prewrap_chapters,
            }
        )
        checks.append(
            {
                "name": "no_hard_wrap_candidates",
                "passed": not hard_wrap_candidates,
                "chapters": hard_wrap_candidates,
            }
        )
        checks.append(
            {
                "name": "no_visible_asset_id_captions",
                "passed": not visible_asset_id_captions,
                "captions": visible_asset_id_captions,
            }
        )

    epubcheck = shutil.which("epubcheck")
    if epubcheck:
        result = subprocess.run([epubcheck, str(epub_path)], capture_output=True, text=True, check=False)
        checks.append(
            {
                "name": "epubcheck",
                "passed": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        )
    else:
        checks.append({"name": "epubcheck_available", "passed": False, "risk": "epubcheck not installed"})
    report["validation"] = {
        "checks": checks,
        "passed": all(check["passed"] for check in checks if check["name"] != "epubcheck_available"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-index", default=str(RAW_INDEX))
    parser.add_argument("--article-index", default=str(ARTICLE_INDEX))
    parser.add_argument("--articles", default=str(ARTICLE_DIR))
    parser.add_argument("--assets", default=str(ASSET_INDEX))
    parser.add_argument("--backup-manifest", default=str(COMBINED_BACKUP))
    parser.add_argument("--canonical-report", default=str(CANONICAL_REPORT))
    parser.add_argument("--out", default=str(OUT_DIR))
    args = parser.parse_args()

    raw_index = Path(args.raw_index)
    article_index_path = Path(args.article_index)
    article_dir = Path(args.articles)
    asset_index_path = Path(args.assets)
    backup_manifest_path = Path(args.backup_manifest)
    canonical_report_path = Path(args.canonical_report)
    out = Path(args.out)
    package_root = out / "_package"

    article_index = load_json(article_index_path)
    article_map = OrderedDict(
        (item["id"], load_json(article_dir / f"{item['id']}.json"))
        for item in article_index.get("articles", [])
    )
    eligible_articles = OrderedDict(
        (article_id, article)
        for article_id, article in article_map.items()
        if article.get("status") in {"recovered", "partial"}
    )
    asset_index = load_json(asset_index_path)
    assets = {asset["id"]: asset for asset in asset_index.get("assets", [])}
    resource_records = best_resource_records(load_json(backup_manifest_path)) if backup_manifest_path.exists() else {}
    canonical_report = load_json(canonical_report_path) if canonical_report_path.exists() else {}

    if out.exists():
        shutil.rmtree(out)
    (package_root / "META-INF").mkdir(parents=True)
    (package_root / "OEBPS" / "chapters").mkdir(parents=True)
    (package_root / "OEBPS" / "styles").mkdir(parents=True)

    sections = parse_raw_index_sections(raw_index, "http://www.bullseyepistol.com/", set(eligible_articles))

    # Inject sub-articles as nested items directly under their parent within homepage sections.
    for section in sections:
        new_items: list[dict[str, Any]] = []
        for item in section["items"]:
            new_items.append(item)
            parent_id = item["article_id"]
            if parent_id in SUBGROUP_INJECTIONS:
                for sub_aid in SUBGROUP_INJECTIONS[parent_id]:
                    if sub_aid in eligible_articles:
                        new_items.append({
                            "article_id": sub_aid,
                            "label": eligible_articles[sub_aid].get("title") or sub_aid,
                            "parent_id": parent_id,
                        })
        section["items"] = new_items

    listed = OrderedDict((item["article_id"], True) for section in sections for item in section["items"])
    unlisted = {aid for aid in eligible_articles if aid not in listed}

    # Replace flat appendix with evidence-backed groups from the canonical enhanced browse layer.
    placed: set[str] = set()
    for group in canonical_report.get("enhanced_groups", []):
        group_items = [
            {"article_id": aid, "label": eligible_articles[aid].get("title") or aid}
            for aid in group.get("article_ids", [])
            if aid in unlisted and aid in eligible_articles
        ]
        if group_items:
            placed.update(item["article_id"] for item in group_items)
            sections.append({"title": group["title"], "items": group_items, "generated": True})

    remainder = [
        {"article_id": aid, "label": eligible_articles[aid].get("title") or aid}
        for aid in sorted(unlisted - placed, key=lambda a: (str(eligible_articles[a].get("title") or "").lower(), a))
    ]
    if remainder:
        sections.append({"title": "Other Recovered Articles", "items": remainder, "generated": True})

    report: dict[str, Any] = {
        "output": str(out / EPUB_NAME),
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "inputs": {
            "raw_index": str(raw_index),
            "article_index": str(article_index_path),
            "article_dir": str(article_dir),
            "asset_index": str(asset_index_path),
            "canonical_report": str(canonical_report_path),
        },
        "raw_index_source": {
            "local_path": str(raw_index),
            "canonical_report_homepage_source": canonical_report.get("homepage_source"),
            "canonical_report_homepage_matches": str(canonical_report.get("homepage_source", {}).get("local_path", "")) == str(raw_index),
        },
        "eligible_article_count": len(eligible_articles),
        "included_article_count": 0,
        "raw_index_listed_article_count": len(listed),
        "not_raw_index_listed_article_count": len(unlisted),
        "embedded_asset_count": 0,
        "embedded_asset_paths": [],
        "missing_assets": [],
        "unsupported_assets": [],
        "unresolved_internal_links": [],
        "suppressed_internal_resource_links": [],
        "chapter_paths": [],
        "chapter_groups": sections,
        "skipped_records": [],
    }

    copied_assets: dict[str, str] = {}
    manifest = [
        {"id": "nav", "href": "nav.xhtml", "media_type": "application/xhtml+xml", "properties": ' properties="nav"'},
        {"id": "style", "href": "styles/ebook.css", "media_type": "text/css"},
    ]
    spine: list[str] = []
    included_order: list[dict[str, str]] = []

    css = """
body { font-family: serif; line-height: 1.45; }
h1, h2 { font-family: sans-serif; }
.meta, .recovery-note { color: #555; font-family: sans-serif; font-size: 0.9em; }
.article-text { white-space: pre-wrap; }
figure { margin: 1em 0; }
img { max-width: 100%; height: auto; }
code { font-size: 0.9em; }
"""
    (package_root / "OEBPS" / "styles" / "ebook.css").write_text(css.strip() + "\n", encoding="utf-8")
    (out / "styles").mkdir(parents=True, exist_ok=True)
    (out / "styles" / "ebook.css").write_text(css.strip() + "\n", encoding="utf-8")
    (package_root / "META-INF" / "container.xml").write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
""",
        encoding="utf-8",
    )

    for section in sections:
        for item in section["items"]:
            article_id = item["article_id"]
            article = eligible_articles[article_id]
            chapter_body, chapter_assets = build_article_page(article, eligible_articles, assets, copied_assets, resource_records, package_root, report)
            href = chapter_href(article_id)
            (package_root / "OEBPS" / href).write_text(chapter_body, encoding="utf-8")
            manifest_id = f"chapter-{slug(article_id)}"
            manifest.append({"id": manifest_id, "href": href, "media_type": "application/xhtml+xml"})
            spine.append(manifest_id)
            report["chapter_paths"].append(href)
            included_order.append({"article_id": article_id, "chapter_group": section["title"], "href": href})
            for asset_path in chapter_assets:
                if asset_path not in report["embedded_asset_paths"]:
                    report["embedded_asset_paths"].append(asset_path)

    report["included_article_count"] = len(included_order)
    report["embedded_asset_count"] = len(report["embedded_asset_paths"])
    report["chapter_order"] = included_order

    provenance_xhtml = build_provenance([eligible_articles[item["article_id"]] for item in included_order], report)
    (package_root / "OEBPS" / "provenance.xhtml").write_text(provenance_xhtml, encoding="utf-8")
    (out / "provenance.html").write_text(provenance_xhtml, encoding="utf-8")
    manifest.append({"id": "provenance", "href": "provenance.xhtml", "media_type": "application/xhtml+xml"})
    spine.append("provenance")

    nav_xhtml = build_nav(sections, eligible_articles)
    (package_root / "OEBPS" / "nav.xhtml").write_text(nav_xhtml, encoding="utf-8")
    for asset_path in report["embedded_asset_paths"]:
        media_type = str(assets[Path(asset_path).stem].get("media_type") or "application/octet-stream")
        manifest.append({"id": f"asset-{slug(Path(asset_path).stem)}", "href": asset_path, "media_type": media_type})

    build_time = report["generated_at"]
    (package_root / "OEBPS" / "content.opf").write_text(content_opf(manifest, spine, build_time), encoding="utf-8")
    epub_path = out / EPUB_NAME
    write_epub(package_root, epub_path)
    validate_epub(epub_path, report)
    shutil.rmtree(package_root)
    (out / "_ebook-export-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Output: {epub_path}")
    print(f"Included articles: {report['included_article_count']}")
    print(f"Raw-index chapter groups: {len(sections)}")
    print(f"Embedded assets: {report['embedded_asset_count']}")
    print(f"Suppressed internal resource links: {len(report['suppressed_internal_resource_links'])}")
    print(f"Unresolved internal links: {len(report['unresolved_internal_links'])}")
    print(f"Validation passed: {report['validation']['passed']}")
    return 0 if report["validation"]["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
