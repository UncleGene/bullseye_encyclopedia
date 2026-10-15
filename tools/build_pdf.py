#!/usr/bin/env python3
"""Build combined book PDF from canonical Bullseye content using WeasyPrint."""

from __future__ import annotations

import argparse
import html as html_module
import json
import re
import sys
from collections import OrderedDict
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urldefrag, urljoin, urlparse

import weasyprint
from pypdf import PdfReader

RAW_INDEX = Path(
    "archive/raw/wayback/files/20260522T143136Z/202508/article_candidate/"
    "www.bullseyepistol.com/20250818003737-index-5fffb450c2814c7e.html"
)
ARTICLE_INDEX = Path("content/canonical/articles.index.json")
ARTICLE_DIR = Path("content/canonical/articles")
ASSET_INDEX = Path("content/assets/assets.index.json")
CANONICAL_REPORT = Path("exports/static-site/raw/_raw-export-report.json")
OUT_DIR = Path("exports/pdf")
PDF_NAME = "bullseye-pistol.pdf"

SECTION_RE = re.compile(r'<td[^>]*class=["\']nav["\'][^>]*>(.*?)</td>', re.IGNORECASE | re.DOTALL)
ART_RE = re.compile(r'<td[^>]*class=["\']art["\'][^>]*>(.*?)</td>', re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")

_INLINE_TAGS = frozenset([
    "a", "b", "strong", "i", "em", "u", "s", "strike",
    "span", "small", "big", "sup", "sub", "tt", "code",
])

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


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self._href = html_module.unescape(href)
            self._text = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href:
            text = SPACE_RE.sub(" ", "".join(self._text)).strip()
            self.links.append({"href": self._href, "text": text or self._href})
            self._href = None
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href:
            self._text.append(data)


class PdfBodyRewriter(HTMLParser):
    """Rewrites article body HTML for PDF rendering.

    - <img src> → absolute file:// paths via asset lookup
    - <a href> to known article IDs → #chapter-{id} anchors
    - script/style elements stripped
    """

    def __init__(
        self,
        article: dict[str, Any],
        article_map: dict[str, dict[str, Any]],
        assets: dict[str, dict[str, Any]],
    ) -> None:
        super().__init__(convert_charrefs=True)
        self.article = article
        self.article_map = article_map
        self.assets = assets
        self.parts: list[str] = []
        self.skip_depth = 0
        self._font_stack: list[dict] = []  # {white: bool, heading: bool}
        self._font_skip_stack: list[bool] = []  # kept for compatibility; mirrors _font_stack white flag
        self._inline_stack: list[str] = []
        self._in_heading = False
        self._br_count = 0
        self.image_count = 0
        self.resolved_image_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag_l = tag.lower()
        if tag_l in ("script", "style"):
            self.skip_depth += 1
            return
        if tag_l == "font":
            d = {k.lower(): (v or "") for k, v in attrs}
            color = d.get("color", "").lower().replace(" ", "")
            is_white = color in {"white", "#fff", "#ffffff"}
            size_str = d.get("size", "").lstrip("+-")
            size = int(size_str) if size_str.isdigit() else 0
            is_heading = (not is_white) and (size >= 4)
            self._font_stack.append({"white": is_white, "heading": is_heading})
            self._font_skip_stack.append(is_white)
            if is_white:
                self.skip_depth += 1
            elif is_heading:
                self._in_heading = True
                self.parts.append("<h2>")
            return  # strip <font> tags entirely; content passes through
        if self.skip_depth:
            return
        if tag_l != "br":
            self._br_count = 0
        if tag_l == "img":
            self._handle_img({k.lower(): v or "" for k, v in attrs})
            return
        if tag_l == "br":
            self._br_count += 1
            if self._br_count == 1:
                self.parts.append("<br/>")
            # subsequent consecutive <br> are collapsed
            return
        if self._in_heading:
            return  # skip tags inside <font size=4+> heading — h2 already provides structure
        if tag_l == "a":
            attrs = self._rewrite_a_attrs(attrs)
        # demote <h1> in article body to avoid clash with article's own <h1>
        out_tag = "h2" if tag_l == "h1" else tag
        if tag_l in _INLINE_TAGS:
            self._inline_stack.append(out_tag)
        self.parts.append(self._rebuild(out_tag, attrs))

    def handle_endtag(self, tag: str) -> None:
        tag_l = tag.lower()
        if tag_l == "font":
            info = self._font_stack.pop() if self._font_stack else {}
            if self._font_skip_stack:
                if self._font_skip_stack.pop() and self.skip_depth > 0:
                    self.skip_depth -= 1
            if info.get("heading") and self._in_heading:
                self._in_heading = False
                self.parts.append("</h2>")
            return
        if tag_l in ("script", "style") and self.skip_depth:
            self.skip_depth -= 1
            return
        if self.skip_depth or tag_l in ("img", "br"):
            return
        if self._in_heading:
            return  # skip close tags inside heading block
        out_tag = "h2" if tag_l == "h1" else tag
        if tag_l in _INLINE_TAGS and self._inline_stack and self._inline_stack[-1] == out_tag:
            self._inline_stack.pop()
        self.parts.append(f"</{out_tag}>")

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(html_module.escape(data))

    def _rebuild(self, tag: str, attrs: list[tuple[str, str | None]]) -> str:
        parts = [tag]
        for name, value in attrs:
            if value is None:
                parts.append(f" {name}")
            else:
                parts.append(f' {name}="{html_module.escape(str(value), quote=True)}"')
        return "<" + "".join(parts) + ">"

    def _rewrite_a_attrs(self, attrs: list[tuple[str, str | None]]) -> list[tuple[str, str | None]]:
        out = []
        for name, value in attrs:
            if name.lower() == "href" and value:
                resolved = urljoin(str(self.article.get("preferred_original_url", "")), value)
                article_id = article_id_from_url(resolved)
                if article_id and article_id in self.article_map:
                    value = f"#chapter-{slug(article_id)}"
                else:
                    # Strip all non-article links — no external active content in PDF
                    continue
            out.append((name, value))
        return out

    def _handle_img(self, attrs: dict[str, str]) -> None:
        self.image_count += 1
        src = attrs.get("src", "")
        alt = attrs.get("alt", "")
        resolved = normalize_url(urljoin(str(self.article.get("preferred_original_url", "")), src))
        file_path: Path | None = None
        for image in self.article.get("images", []):
            if normalize_url(str(image.get("resolved_url", ""))) == resolved:
                for asset_id in image.get("asset_ids", []):
                    asset = self.assets.get(str(asset_id))
                    if asset:
                        p = Path(str(asset.get("file_path") or ""))
                        if not p.exists():
                            p = Path(str(asset.get("blob_path") or ""))
                        if p.exists():
                            file_path = p.resolve()
                            break
                break
        if file_path:
            self.resolved_image_count += 1
            caption = f"<figcaption>{html_module.escape(alt)}</figcaption>" if alt else ""
            self.parts.append(
                f'<figure><img src="file://{file_path}" alt="{html_module.escape(alt)}" />{caption}</figure>'
            )
        elif alt:
            self.parts.append(f'<p class="missing-image">[Image: {html_module.escape(alt)}]</p>')

    def result(self) -> str:
        for tag in reversed(self._inline_stack):
            self.parts.append(f"</{tag}>")
        self._inline_stack.clear()
        return "".join(self.parts)


def clean_text(value: str) -> str:
    return SPACE_RE.sub(" ", html_module.unescape(TAG_RE.sub(" ", value or ""))).strip()


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


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "item"


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
        items, seen = [], set()
        for link in parser.links:
            article_id = article_id_from_url(urljoin(base_url, link["href"]))
            if not article_id or article_id not in article_ids or article_id in seen:
                continue
            seen.add(article_id)
            items.append({"article_id": article_id, "label": link["text"]})
        if items:
            sections.append({"title": title, "items": items})
        pos = art_match.end()
    return sections


PDF_CSS = """
@page {
    margin: 1in;
    size: letter;
    @top-center {
        content: "Bullseye Pistol";
        font-size: 9pt;
        color: #888;
        font-family: Arial, sans-serif;
    }
    @bottom-center {
        content: counter(page);
        font-size: 9pt;
        font-family: Arial, sans-serif;
    }
}
@page :first {
    @top-center { content: none; }
    @bottom-center { content: none; }
}
@page toc-page {
    @top-center { content: "Contents"; font-size: 9pt; color: #888; font-family: Arial, sans-serif; }
}

body { font-family: Georgia, serif; font-size: 11pt; line-height: 1.5; color: #111; }
h1, h2, h3, h4 { font-family: Arial, sans-serif; }
h2 { font-size: 1.15em; margin-top: 1em; }
h3 { font-size: 1.05em; }
p { margin: 0.6em 0; }
ul, ol { margin: 0.6em 0 0.6em 1.5em; }
li { margin: 0.2em 0; }
a { color: #222; text-decoration: none; }
figure { margin: 1em 0; text-align: center; page-break-inside: avoid; }
img { max-width: 100%; height: auto; }
figcaption { font-size: 9pt; color: #666; font-style: italic; margin-top: 0.25em; }
.missing-image { font-size: 9pt; color: #999; font-style: italic; }
.recovery-note { font-size: 9pt; color: #c55; font-family: Arial, sans-serif; }
table { max-width: 100%; table-layout: fixed; border-collapse: collapse; font-size: 10pt; word-break: break-word; }
td, th { padding: 0.2em 0.4em; vertical-align: top; }
.ref-url { font-size: 8.5pt; color: #888; font-family: Arial, sans-serif; }

#cover {
    page-break-after: always;
    text-align: center;
    padding-top: 3in;
}
#cover h1 { font-size: 28pt; border: none; margin-bottom: 0.5em; }
#cover .subtitle { font-size: 14pt; color: #555; font-family: Arial, sans-serif; margin-bottom: 2em; }
#cover .meta { font-size: 10pt; color: #888; font-family: Arial, sans-serif; }

#toc { page: toc-page; page-break-after: always; }
#toc > h1 { font-size: 18pt; border-bottom: 1px solid #ccc; padding-bottom: 0.25em; margin-bottom: 1em; }
.toc-group { margin-bottom: 1em; }
.toc-group-title {
    font-weight: bold;
    font-family: Arial, sans-serif;
    font-size: 9pt;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.3em;
}
.toc-entry { font-size: 10pt; margin: 0.15em 0; }
.toc-entry a {
    text-decoration: none;
    color: #111;
}
.toc-entry a::after {
    content: leader(".") target-counter(attr(href url), page);
    font-family: Arial, sans-serif;
    font-size: 9pt;
    color: #666;
}

article { page-break-before: always; }
article > h1 {
    font-size: 16pt;
    border-bottom: 1px solid #ddd;
    padding-bottom: 0.2em;
    margin-bottom: 0.4em;
}
.chapter-group {
    font-size: 8.5pt;
    color: #999;
    font-family: Arial, sans-serif;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.25em;
}
.meta { font-size: 9.5pt; color: #666; font-family: Arial, sans-serif; margin-bottom: 0.75em; }
.original-url { font-size: 8.5pt; color: #aaa; font-family: Arial, sans-serif; margin-bottom: 1em; }
.links-section {
    margin-top: 1.5em;
    border-top: 1px solid #e8e8e8;
    padding-top: 0.75em;
    font-size: 9.5pt;
    font-family: Arial, sans-serif;
}
.links-section h2 { font-size: 10pt; margin-bottom: 0.4em; color: #555; }
.links-section ul { margin: 0.2em 0 0.2em 1.2em; }
.links-section li { margin: 0.15em 0; }
.unresolved-ref { color: #999; font-style: italic; }
"""


def build_toc(sections: list[dict[str, Any]], article_map: dict[str, dict[str, Any]]) -> str:
    groups = []
    for section in sections:
        title = html_module.escape(section["title"])
        entries = "".join(
            f'<div class="toc-entry"><a href="#chapter-{slug(item["article_id"])}">'
            f'{html_module.escape(str(article_map[item["article_id"]].get("title") or item["article_id"]))}'
            f"</a></div>"
            for item in section["items"]
        )
        groups.append(f'<div class="toc-group"><div class="toc-group-title">{title}</div>{entries}</div>')
    return '<div id="toc"><h1>Contents</h1>' + "".join(groups) + "</div>"


def build_article_section(
    article: dict[str, Any],
    article_map: dict[str, dict[str, Any]],
    assets: dict[str, dict[str, Any]],
    section_title: str,
    report: dict[str, Any],
) -> str:
    article_id = str(article["id"])
    title = str(article.get("title") or article_id)

    meta_parts = []
    if article.get("byline"):
        meta_parts.append(f"By {html_module.escape(str(article['byline']))}")
    if article.get("published_at"):
        meta_parts.append(f"Published {html_module.escape(str(article['published_at']))}")
    if article.get("updated_at"):
        meta_parts.append(f"Updated {html_module.escape(str(article['updated_at']))}")
    meta = f'<p class="meta">{" | ".join(meta_parts)}</p>' if meta_parts else ""

    status_note = ""
    if article.get("status") == "partial":
        status_note = '<p class="recovery-note">Partial recovered article.</p>'

    original_url = html_module.escape(str(article.get("preferred_original_url") or ""))
    origin_line = f'<p class="original-url">Source: {original_url}</p>' if original_url else ""

    rewriter = PdfBodyRewriter(article, article_map, assets)
    rewriter.feed(str(article.get("body", {}).get("html") or ""))
    body_html = rewriter.result()

    report["embedded_image_count"] = report.get("embedded_image_count", 0) + rewriter.resolved_image_count
    report["total_image_refs"] = report.get("total_image_refs", 0) + rewriter.image_count

    internal_links: list[str] = []
    external_refs: list[str] = []
    unresolved_internal: list[dict[str, str]] = []
    for link in article.get("links", []):
        href = str(link.get("resolved_url") or link.get("href") or "")
        label = str(link.get("text") or href)
        target_id = article_id_from_url(href)
        if target_id and target_id in article_map:
            anchor = f"#chapter-{slug(target_id)}"
            internal_links.append(
                f'<li><a href="{html_module.escape(anchor)}">{html_module.escape(label)}</a></li>'
            )
        elif is_internal_url(href):
            unresolved_internal.append({"article_id": article_id, "href": href, "text": label})
        elif href:
            # No active external links in PDF — show as plain text reference
            external_refs.append(
                f'<li>{html_module.escape(label)}'
                f'<span class="ref-url"> ({html_module.escape(href)})</span></li>'
            )
    report.setdefault("unresolved_internal_links", []).extend(unresolved_internal)

    link_parts = []
    if internal_links:
        link_parts.append("<h2>References</h2><ul>" + "".join(internal_links) + "</ul>")
    if external_refs:
        link_parts.append("<h2>Further Reading</h2><ul>" + "".join(external_refs) + "</ul>")
    links_section = f'<div class="links-section">{"".join(link_parts)}</div>' if link_parts else ""

    chapter_group = f'<div class="chapter-group">{html_module.escape(section_title)}</div>'
    return (
        f'<article id="chapter-{slug(article_id)}">'
        f"{chapter_group}"
        f"<h1>{html_module.escape(title)}</h1>"
        f"{meta}{status_note}{origin_line}"
        f"{body_html}"
        f"{links_section}"
        f"</article>"
    )


def build_html(
    sections: list[dict[str, Any]],
    article_map: dict[str, dict[str, Any]],
    assets: dict[str, dict[str, Any]],
    build_time: str,
    report: dict[str, Any],
) -> str:
    toc = build_toc(sections, article_map)
    article_sections: list[str] = []
    for section in sections:
        for item in section["items"]:
            article = article_map[item["article_id"]]
            article_sections.append(
                build_article_section(article, article_map, assets, section["title"], report)
            )

    article_count = sum(len(s["items"]) for s in sections)
    cover = (
        '<div id="cover">'
        "<h1>Bullseye Pistol</h1>"
        '<p class="subtitle">Recovered article collection from bullseyepistol.com</p>'
        f'<p class="meta">{article_count} articles &nbsp;|&nbsp; Generated {build_time[:10]}</p>'
        "</div>"
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>Bullseye Pistol</title>
<style>{PDF_CSS}</style>
</head>
<body>
{cover}
{toc}
{"".join(article_sections)}
</body>
</html>"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-index", default=str(RAW_INDEX))
    parser.add_argument("--article-index", default=str(ARTICLE_INDEX))
    parser.add_argument("--articles", default=str(ARTICLE_DIR))
    parser.add_argument("--assets", default=str(ASSET_INDEX))
    parser.add_argument("--canonical-report", default=str(CANONICAL_REPORT))
    parser.add_argument("--out", default=str(OUT_DIR))
    args = parser.parse_args()

    raw_index = Path(args.raw_index)
    article_index_path = Path(args.article_index)
    article_dir = Path(args.articles)
    asset_index_path = Path(args.assets)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    article_index = json.loads(article_index_path.read_text(encoding="utf-8"))
    article_map: OrderedDict[str, dict[str, Any]] = OrderedDict(
        (item["id"], json.loads((article_dir / f"{item['id']}.json").read_text(encoding="utf-8")))
        for item in article_index.get("articles", [])
    )
    eligible = OrderedDict(
        (aid, a)
        for aid, a in article_map.items()
        if a.get("status") in {"recovered", "partial"}
    )
    asset_index = json.loads(asset_index_path.read_text(encoding="utf-8"))
    assets = {a["id"]: a for a in asset_index.get("assets", [])}

    canonical_report = json.loads(Path(args.canonical_report).read_text(encoding="utf-8")) if Path(args.canonical_report).exists() else {}

    sections = parse_raw_index_sections(raw_index, "http://www.bullseyepistol.com/", set(eligible))

    # Inject sub-articles as nested items directly under their parent within homepage sections.
    for section in sections:
        new_items: list[dict[str, Any]] = []
        for item in section["items"]:
            new_items.append(item)
            parent_id = item["article_id"]
            if parent_id in SUBGROUP_INJECTIONS:
                for sub_aid in SUBGROUP_INJECTIONS[parent_id]:
                    if sub_aid in eligible:
                        new_items.append({
                            "article_id": sub_aid,
                            "label": eligible[sub_aid].get("title") or sub_aid,
                            "parent_id": parent_id,
                        })
        section["items"] = new_items

    listed = {item["article_id"] for section in sections for item in section["items"]}
    unlisted = {aid for aid in eligible if aid not in listed}

    placed: set[str] = set()
    for group in canonical_report.get("enhanced_groups", []):
        group_items = [
            {"article_id": aid, "label": eligible[aid].get("title") or aid}
            for aid in group.get("article_ids", [])
            if aid in unlisted and aid in eligible
        ]
        if group_items:
            placed.update(item["article_id"] for item in group_items)
            sections.append({"title": group["title"], "items": group_items, "generated": True})

    remainder = sorted(
        ({"article_id": aid, "label": eligible[aid].get("title") or aid} for aid in unlisted - placed),
        key=lambda row: (str(eligible[row["article_id"]].get("title") or "").lower(), row["article_id"]),
    )
    if remainder:
        sections.append({"title": "Other Recovered Articles", "items": remainder, "generated": True})

    build_time = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    report: dict[str, Any] = {
        "output": str(out / PDF_NAME),
        "generated_at": build_time,
        "inputs": {
            "raw_index": str(raw_index),
            "article_index": str(article_index_path),
            "article_dir": str(article_dir),
            "asset_index": str(asset_index_path),
        },
        "included_article_count": sum(len(s["items"]) for s in sections),
        "not_raw_index_listed_article_count": len(unlisted),
        "embedded_image_count": 0,
        "total_image_refs": 0,
        "unresolved_internal_links": [],
        "chapter_groups": sections,
        "chapter_order": [
            {"article_id": item["article_id"], "chapter_group": s["title"]}
            for s in sections
            for item in s["items"]
        ],
    }

    print("Building HTML document…", flush=True)
    full_html = build_html(sections, eligible, assets, build_time, report)

    pdf_path = out / PDF_NAME
    print("Rendering PDF (this may take a moment)…", flush=True)
    weasyprint.HTML(string=full_html, base_url=str(Path.cwd())).write_pdf(str(pdf_path))

    valid = pdf_path.exists() and pdf_path.read_bytes()[:4] == b"%PDF"
    report["valid_pdf"] = valid
    report["file_size_bytes"] = pdf_path.stat().st_size if valid else 0
    report["page_count"] = len(PdfReader(str(pdf_path)).pages) if valid else 0

    (out / "_pdf-export-report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(f"Output: {pdf_path}")
    print(f"Included articles: {report['included_article_count']}")
    print(f"Embedded images: {report['embedded_image_count']} / {report['total_image_refs']} refs")
    print(f"Unresolved internal links: {len(report['unresolved_internal_links'])}")
    print(f"Valid PDF: {valid}  ({report['file_size_bytes']:,} bytes)")
    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())
