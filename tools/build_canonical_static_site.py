#!/usr/bin/env python3
"""Build clean raw article site using recovered homepage navigation."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import hashlib
import shutil
import sys
from collections import OrderedDict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urldefrag, urljoin, urlparse


SECTION_RE = re.compile(r'<td[^>]*class=["\']nav["\'][^>]*>(.*?)</td>', re.IGNORECASE | re.DOTALL)
ART_RE = re.compile(r'<td[^>]*class=["\']art["\'][^>]*>(.*?)</td>', re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")
SITE_BANNER_PATH = "assets/site-banner.gif"
HISTORICAL_SITE_URL = "https://unclegene.github.io/bullseye_encyclopedia/"

# Sub-articles that belong nested under a specific parent article.
# These are injected as sub-items within the parent's homepage section rather than
# appearing as standalone peer sections. Matches the raw-site subdirectory structure.
SUBGROUP_INJECTIONS: dict[str, list[str]] = {
    # amucover is the gateway to the AMU Training Guide; all guide chapters nest under it.
    "amucover":  ["chapterf", "chapter0", "chapter1", "chapter2", "chapter3", "chapter4",
                  "chapter5", "chapter6", "chapter7", "chapter8", "chapter9", "chapter10",
                  "annex2", "glossary"],
    "amuprfil":  ["profile1", "profile2", "profile3", "profile4", "profile5", "profile6", "profile7"],
    "mikelav1":  ["mikelav2"],
    "savino2":   ["savino"],
    "wong":      ["wong1", "wong2", "wong3", "wong4", "wong5", "wong6", "wong7", "wongbio"],
    "zins":      ["zins1"],
}

ENHANCED_GROUPS: list[dict[str, Any]] = [
    {
        "title": "NRA Conventional Pistol Rules",
        "confidence": "high",
        "note": "Ordered rulebook sequence; missing sections 11–13 are absent from recovered content.",
        "article_ids": ["rulebook", "rulebook1", "rulebook2", "rulebook3", "rulebook4", "rulebook5",
                        "rulebook6", "rulebook7", "rulebook8", "rulebook9", "rulebook10",
                        "rulebook14", "rulebook15", "rulebook16", "rulebook17", "rulebook18", "rulebook19"],
    },
    {
        "title": "Il-Mo League",
        "confidence": "high",
        "note": "Shared im*/ilmo IDs and Il-Mo titles.",
        "article_ids": ["ilmo", "imadmin", "imforms", "imhist", "imnews", "imprev",
                        "imrecord", "imsoft", "imstand", "imteams"],
    },
    {
        "title": "Camp Perry / National Matches",
        "confidence": "high",
        "note": "Shared per* IDs and Camp Perry/National Matches titles; perryfaq links to perinfo.",
        "article_ids": ["perenter", "perhist", "perinfo", "permem", "perryfaq", "perrysrv", "pertriv"],
    },
    {
        "title": "Ron Porter Fundamentals",
        "confidence": "high",
        "note": "Shared ron* IDs and Fundamentals Series titles.",
        "article_ids": ["ron1", "ron2", "ron3", "ron4", "ron5", "ron6", "ron7", "ronbio"],
    },
    {
        "title": "Dave Salyer Articles",
        "confidence": "medium",
        "note": "Shared salyer* IDs; related to homepage-listed salyer1 and salyer5.",
        "article_ids": ["salyer2", "salyer3", "salyer4", "salyer6"],
    },
    {
        "title": "Site / Reference / General Index",
        "confidence": "medium",
        "note": "Site utility, reference, and index-style pages.",
        "article_ids": ["advertise", "alphadex", "legal", "links", "records",
                        "other", "techo", "why", "visualize"],
    },
]


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
            self._href = href
            self._text = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href:
            self.links.append({"href": html.unescape(self._href), "text": clean_text(" ".join(self._text))})
            self._href = None
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href:
            self._text.append(data)


def clean_text(value: str) -> str:
    return SPACE_RE.sub(" ", html.unescape(TAG_RE.sub(" ", value or ""))).strip()


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


def article_id_from_url(url: str) -> str | None:
    parsed = urlparse(url)
    if not is_internal_url(url):
        return None
    path = parsed.path
    if not path or path == "/":
        return None
    name = Path(path).name
    if not name:
        return None
    stem = re.sub(r"\.[A-Za-z0-9]{1,8}$", "", name)
    stem = re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-").lower()
    return stem or None


def is_internal_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme and parsed.scheme.lower() not in {"http", "https"}:
        return False
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    if host.endswith(":80"):
        host = host[:-3]
    if "@" in parsed.path and not Path(parsed.path).suffix:
        return False
    return not host or host == "bullseyepistol.com"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_homepage(backup: dict[str, Any]) -> dict[str, Any]:
    candidates = []
    for record in backup.get("records", []):
        if record.get("status") != "success":
            continue
        original = str(record.get("original", ""))
        normalized = normalize_url(original)
        if normalized == "http://bullseyepistol.com/index.htm":
            candidates.append(record)
    if not candidates:
        raise RuntimeError("No recovered homepage found")
    return max(candidates, key=lambda row: str(row.get("timestamp", "")))


def parse_homepage_sections(path: Path, base_url: str, article_ids: set[str]) -> list[dict[str, Any]]:
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


def site_path(article_id: str) -> str:
    return f"articles/{article_id}.html"


def copy_asset(asset: dict[str, Any], out: Path) -> str | None:
    src = Path(str(asset.get("file_path") or ""))
    if not src.exists():
        src = Path(str(asset.get("blob_path") or ""))
    if not src.exists():
        return None
    suffix = Path(urlparse((asset.get("original_urls") or [""])[0]).path).suffix or Path(str(asset.get("file_path") or "")).suffix
    rel = Path("assets") / f"{asset['id']}{suffix}"
    dst = out / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return rel.as_posix()
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)
    return rel.as_posix()


def resource_filename(original_url: str, sha256: str) -> str:
    parsed = urlparse(original_url)
    name = Path(parsed.path).name or "index.htm"
    suffix = Path(name).suffix
    stem = re.sub(r"\.[A-Za-z0-9]{1,8}$", "", name)
    stem = re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-").lower() or "resource"
    return f"{stem}-{sha256[:12]}{suffix}"


def copy_resource(record: dict[str, Any], out: Path, resource_paths: dict[str, str]) -> str | None:
    normalized = normalize_url(str(record.get("original", "")))
    if normalized in resource_paths:
        return resource_paths[normalized]
    src = Path(str(record.get("file_path") or record.get("local_path") or ""))
    if not src.exists():
        src = Path(str(record.get("blob_path") or ""))
    if not src.exists():
        return None
    sha256 = str(record.get("sha256") or hashlib.sha256(src.read_bytes()).hexdigest())
    rel = Path("resources") / resource_filename(str(record.get("original", "")), sha256)
    dst = out / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        try:
            os.link(src, dst)
        except OSError:
            shutil.copy2(src, dst)
    resource_paths[normalized] = rel.as_posix()
    return rel.as_posix()


# Dynamic or provider-owned URLs that are not content and should not generate missing notes.
PROVIDER_ARTIFACT_URLS: frozenset[str] = frozenset([
    "http://bullseyepistol.com/advertise1.php",
])


def missing_resource_anchor(normalized_url: str, missing_refs: dict[str, str]) -> str:
    anchor = missing_refs.get(normalized_url)
    if anchor:
        return anchor
    digest = hashlib.sha256(normalized_url.encode("utf-8")).hexdigest()[:12]
    parsed = urlparse(normalized_url)
    name = Path(parsed.path).name or "resource"
    stem = re.sub(r"[^A-Za-z0-9]+", "-", Path(name).stem).strip("-").lower() or "resource"
    anchor = f"{stem}-{digest}"
    missing_refs[normalized_url] = anchor
    return anchor


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


def collect_missing_artifact_contexts(article_map: dict[str, dict[str, Any]], missing_urls: set[str]) -> dict[str, list[dict[str, str]]]:
    contexts: dict[str, list[dict[str, str]]] = {url: [] for url in missing_urls}
    block_patterns = [
        re.compile(r"<tr\b[^>]*>.*?</tr>", re.IGNORECASE | re.DOTALL),
        re.compile(r"<p\b[^>]*>.*?</p>", re.IGNORECASE | re.DOTALL),
        re.compile(r"<li\b[^>]*>.*?</li>", re.IGNORECASE | re.DOTALL),
    ]

    for article_id, article in article_map.items():
        body_html = str(article.get("body", {}).get("html") or "")
        links_by_url: dict[str, list[str]] = {}
        for link in article.get("links", []):
            resolved = normalize_url(str(link.get("resolved_url") or link.get("href") or ""))
            if resolved not in missing_urls:
                continue
            links_by_url.setdefault(resolved, []).append(str(link.get("text") or "").strip())
        if not links_by_url:
            continue

        matched_blocks: dict[str, str] = {}
        for pattern in block_patterns:
            for match in pattern.finditer(body_html):
                block_html = match.group(0)
                for url in links_by_url:
                    filename = Path(urlparse(url).path).name
                    if filename and re.search(rf'href=["\'][^"\']*{re.escape(filename)}["\']', block_html, re.IGNORECASE):
                        matched_blocks.setdefault(url, clean_text(block_html))

        for url, link_texts in links_by_url.items():
            description = matched_blocks.get(url, "")
            for link_text in link_texts:
                concise = description
                if concise and link_text:
                    concise = re.sub(rf"^{re.escape(link_text)}\s*:?\s*", "", concise, flags=re.IGNORECASE).strip()
                contexts[url].append(
                    {
                        "article_id": article_id,
                        "article_title": str(article.get("title") or article_id),
                        "link_text": link_text,
                        "description": concise,
                    }
                )
    return contexts


def rewrite_article_html(
    body: str,
    article: dict[str, Any],
    article_map: dict[str, dict[str, Any]],
    asset_paths: dict[str, str],
    resource_records: dict[str, dict[str, Any]],
    resource_paths: dict[str, str],
    missing_refs: dict[str, str],
    out: Path,
) -> str:
    def replace_href(match: re.Match[str]) -> str:
        quote = match.group(1)
        href = html.unescape(match.group(2))
        resolved = urljoin(str(article.get("preferred_original_url", "")), href)
        article_id = article_id_from_url(resolved)
        if article_id and article_id in article_map:
            return f'href={quote}{os.path.relpath(site_path(article_id), start="articles").replace(os.sep, "/")}{quote}'
        if is_internal_url(resolved):
            normalized = normalize_url(resolved)
            if normalized in PROVIDER_ARTIFACT_URLS:
                return match.group(0)
            if normalized in resource_records:
                rel = copy_resource(resource_records[normalized], out, resource_paths)
                if rel:
                    return f'href={quote}{os.path.relpath(rel, start="articles").replace(os.sep, "/")}{quote}'
            anchor = missing_resource_anchor(normalized, missing_refs)
            rel = f"missing-artifacts.html#{anchor}"
            return f'href={quote}{os.path.relpath(rel, start="articles").replace(os.sep, "/")}{quote}'
        return match.group(0)

    def replace_src(match: re.Match[str]) -> str:
        quote = match.group(1)
        src = html.unescape(match.group(2))
        original_resolved = urljoin(str(article.get("preferred_original_url", "")), src)
        resolved = normalize_url(original_resolved)
        for image in article.get("images", []):
            if normalize_url(str(image.get("resolved_url", ""))) == resolved and image.get("asset_ids"):
                asset_id = image["asset_ids"][0]
                rel = asset_paths.get(asset_id)
                if rel:
                    return f'src={quote}{os.path.relpath(rel, start="articles").replace(os.sep, "/")}{quote}'
        if is_internal_url(original_resolved) and resolved in resource_records:
            rel = copy_resource(resource_records[resolved], out, resource_paths)
            if rel:
                return f'src={quote}{os.path.relpath(rel, start="articles").replace(os.sep, "/")}{quote}'
        return match.group(0)

    body = re.sub(r'href=(["\'])(.*?)\1', replace_href, body, flags=re.IGNORECASE)
    body = re.sub(r'src=(["\'])(.*?)\1', replace_src, body, flags=re.IGNORECASE)
    return body


def page(title: str, body: str, rel_root: str = ".") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{rel_root}/styles.css">
</head>
<body>
<header class="site-header">
  <a class="brand" href="{rel_root}/index.html"><img class="site-banner" src="{rel_root}/{SITE_BANNER_PATH}" width="606" height="50" alt="The Encyclopedia of Bullseye Pistol"></a>
  <nav aria-label="Site navigation"><a href="{rel_root}/articles.html">All Articles</a><a href="{rel_root}/missing-artifacts.html">Missing Artifacts</a><a data-site-variant="as-is" href="{HISTORICAL_SITE_URL}">Historical site</a></nav>
</header>
<main>
{body}
</main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backup", required=True)
    parser.add_argument("--articles", default="content/canonical/articles")
    parser.add_argument("--article-index", default="content/canonical/articles.index.json")
    parser.add_argument("--assets", default="content/assets/assets.index.json")
    parser.add_argument("--out", default="exports/static-site/raw")
    args = parser.parse_args()

    backup = load_json(Path(args.backup))
    article_index = load_json(Path(args.article_index))
    article_map = {
        item["id"]: load_json(Path(args.articles) / f"{item['id']}.json")
        for item in article_index["articles"]
    }
    assets_index = load_json(Path(args.assets))
    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    (out / "articles").mkdir(parents=True, exist_ok=True)
    (out / "sections").mkdir(parents=True, exist_ok=True)

    asset_paths = {}
    for asset in assets_index.get("assets", []):
        rel = copy_asset(asset, out)
        if rel:
            asset_paths[asset["id"]] = rel
    resource_records = best_resource_records(backup)
    banner_record = resource_records.get(normalize_url("http://bullseyepistol.com/banner2.gif"))
    if banner_record is None:
        raise SystemExit("Recovered site banner is missing from the backup manifest.")
    banner_source = Path(str(banner_record.get("blob_path") or banner_record["local_path"]))
    if hashlib.sha256(banner_source.read_bytes()).hexdigest() != banner_record["sha256"]:
        raise SystemExit("Recovered site banner checksum does not match the backup manifest.")
    (out / "assets").mkdir(exist_ok=True)
    shutil.copyfile(banner_source, out / SITE_BANNER_PATH)
    resource_paths: dict[str, str] = {}
    missing_refs: dict[str, str] = {}

    home = latest_homepage(backup)
    sections = parse_homepage_sections(Path(str(home["local_path"])), str(home["original"]), set(article_map))
    placed: OrderedDict[str, str] = OrderedDict()
    for section in sections:
        for item in section["items"]:
            placed.setdefault(item["article_id"], section["title"])

    # Inject sub-articles as nested items directly under their parent within homepage sections.
    for section in sections:
        new_items = []
        for item in section["items"]:
            new_items.append(item)
            parent_id = item["article_id"]
            if parent_id in SUBGROUP_INJECTIONS:
                for sub_aid in SUBGROUP_INJECTIONS[parent_id]:
                    if sub_aid in article_map:
                        new_items.append({
                            "article_id": sub_aid,
                            "label": article_map[sub_aid]["title"],
                            "parent_id": parent_id,
                        })
                        placed.setdefault(sub_aid, section["title"])
        section["items"] = new_items

    homepage_unplaced = {aid for aid in article_map if aid not in placed}
    group_placed: set[str] = set()
    for group in ENHANCED_GROUPS:
        group_ids = [aid for aid in group["article_ids"] if aid in homepage_unplaced and aid in article_map]
        if group_ids:
            group_placed.update(group_ids)
            sections.append({"title": group["title"], "items": [{"article_id": aid, "label": article_map[aid]["title"]} for aid in group_ids]})
    unplaced = sorted(homepage_unplaced - group_placed)
    if unplaced:
        sections.append({"title": "Other Recovered Articles", "items": [{"article_id": aid, "label": article_map[aid]["title"]} for aid in unplaced]})

    css = """
:root { color-scheme: light; --ink:#1f2933; --muted:#5d6b78; --line:#d7dde3; --paper:#fbfbf8; --accent:#1f5f8b; }
body { margin:0; font-family: Georgia, 'Times New Roman', serif; color:var(--ink); background:var(--paper); line-height:1.55; }
a { color:var(--accent); }
.site-header { border-bottom:1px solid var(--line); padding:14px 22px; display:flex; flex-wrap:wrap; justify-content:space-between; gap:16px; align-items:center; font-family: Arial, sans-serif; background:#fff; position:sticky; top:0; z-index:1; }
.brand { display:block; min-width:0; max-width:606px; flex:0 1 606px; }
.site-banner { display:block; width:100%; height:auto; }
nav { display:flex; flex-wrap:wrap; gap:10px 14px; }
nav a { font-size:14px; }
main { max-width:960px; margin:0 auto; padding:28px 22px 56px; }
.article { max-width:760px; }
.meta { color:var(--muted); font-family: Arial, sans-serif; font-size:14px; }
.sections { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:22px; }
.section { border-top:3px solid var(--accent); padding-top:10px; }
.section h2 { font-family:Arial,sans-serif; font-size:18px; }
.section li { margin:7px 0; }
.subitem { padding-left:16px; }
.subitem a::before { content:"↳ "; color:var(--muted); font-size:12px; }
img { max-width:100%; height:auto; }
pre, code { white-space:pre-wrap; }
.browse-note { font-size:13px; margin:4px 0 8px; }
.conf-medium { font-weight:normal; font-size:14px; color:var(--muted); }
.missing-list { padding-left: 20px; }
.missing-list li { margin: 10px 0; }
"""
    (out / "styles.css").write_text(css.strip() + "\n", encoding="utf-8")

    for article_id, article in article_map.items():
        body_html = rewrite_article_html(
            article["body"]["html"],
            article,
            article_map,
            asset_paths,
            resource_records,
            resource_paths,
            missing_refs,
            out,
        )
        meta = f"<p class=\"meta\">{html.escape(article.get('byline') or '')}</p>" if article.get("byline") else ""
        original = html.escape(str(article.get("preferred_original_url", "")))
        content = f"<article class=\"article\"><h1>{html.escape(article['title'])}</h1>{meta}<p class=\"meta\">Original URL: {original}</p>{body_html}</article>"
        (out / site_path(article_id)).write_text(page(article["title"], content, ".."), encoding="utf-8")

    missing_contexts = collect_missing_artifact_contexts(article_map, set(missing_refs))
    missing_items = []
    for normalized_url, anchor in sorted(missing_refs.items()):
        original = html.escape(normalized_url)
        label = html.escape(Path(urlparse(normalized_url).path).name or normalized_url)
        context_html = ""
        if missing_contexts.get(normalized_url):
            parts = []
            for context in missing_contexts[normalized_url]:
                article_href = site_path(context["article_id"])
                source = f'<a href="{html.escape(article_href)}">{html.escape(context["article_title"])}</a>'
                summary = context["description"] or context["link_text"] or "Referenced from article content."
                parts.append(f'<div class="meta">From {source}: {html.escape(summary)}</div>')
            context_html = "".join(parts)
        missing_items.append(
            f'<li id="{anchor}"><strong>{label}</strong><br/><span class="meta">{original}</span>{context_html}</li>'
        )
    missing_body = (
        "<h1>Missing Artifacts</h1>"
        "<p class=\"meta\">Internal resources referenced by recovered article content that are not present in the current local recovery set.</p>"
        + ("<ol class=\"missing-list\">" + "".join(missing_items) + "</ol>" if missing_items else "<p>No missing artifacts are currently recorded.</p>")
    )
    (out / "missing-artifacts.html").write_text(page("Missing Artifacts", missing_body), encoding="utf-8")

    def render_section_items(items: list[dict], path_prefix: str) -> str:
        parts = []
        for item in items:
            aid = item["article_id"]
            title = html.escape(article_map[aid]["title"])
            cls = ' class="subitem"' if item.get("parent_id") else ""
            parts.append(f'<li{cls}><a href="{path_prefix}{site_path(aid)}">{title}</a></li>')
        return "\n".join(parts)

    section_cards = []
    for idx, section in enumerate(sections, start=1):
        slug = re.sub(r"[^a-z0-9]+", "-", section["title"].lower()).strip("-") or f"section-{idx}"
        links_sec = render_section_items(section["items"], "../")
        section_body = f"<h1>{html.escape(section['title'])}</h1><ol>{links_sec}</ol>"
        (out / "sections" / f"{slug}.html").write_text(page(section["title"], section_body, ".."), encoding="utf-8")
        links_idx = render_section_items(section["items"], "")
        section_cards.append(f'<section class="section"><h2><a href="sections/{slug}.html">{html.escape(section["title"])}</a></h2><ol>{links_idx}</ol></section>')

    home_body = "<h1>Bullseye Pistol</h1><p class=\"meta\">Recovered article site generated from normalized records. Navigation follows the recovered homepage structure as closely as possible.</p><div class=\"sections\">" + "\n".join(section_cards) + "</div>"
    (out / "index.html").write_text(page("Bullseye Pistol", home_body), encoding="utf-8")

    placed_in_groups: set[str] = set()
    enhanced_group_records: list[dict[str, Any]] = []
    group_cards: list[str] = []
    for group in ENHANCED_GROUPS:
        ids = [aid for aid in group["article_ids"] if aid in article_map]
        if not ids:
            continue
        placed_in_groups.update(ids)
        links = "\n".join(
            f'<li><a href="{site_path(aid)}">{html.escape(article_map[aid]["title"])}</a></li>'
            for aid in ids
        )
        note_html = f'<p class="meta browse-note">{html.escape(group["note"])}</p>' if group.get("note") else ""
        conf_label = ' <span class="conf-medium">(inferred)</span>' if group["confidence"] != "high" else ""
        group_cards.append(
            f'<section class="section"><h2>{html.escape(group["title"])}{conf_label}</h2>'
            f'{note_html}<ol>{links}</ol></section>'
        )
        enhanced_group_records.append({
            "title": group["title"],
            "confidence": group["confidence"],
            "article_count": len(ids),
            "article_ids": ids,
        })
    all_subgroup_ids = {aid for ids in SUBGROUP_INJECTIONS.values() for aid in ids}
    browse_residual_order: list[str] = []
    for aid in sorted(article_map):
        if aid in placed_in_groups or aid in all_subgroup_ids:
            continue
        browse_residual_order.append(aid)
        if aid in SUBGROUP_INJECTIONS:
            for sub_aid in SUBGROUP_INJECTIONS[aid]:
                if sub_aid in article_map:
                    browse_residual_order.append(sub_aid)
    if browse_residual_order:
        residual_links = []
        for aid in browse_residual_order:
            title = html.escape(article_map[aid]["title"])
            is_sub = aid in all_subgroup_ids
            cls = ' class="subitem"' if is_sub else ""
            residual_links.append(f'<li{cls}><a href="{site_path(aid)}">{title}</a></li>')
        group_cards.append(
            '<section class="section"><h2>Recovered Homepage Articles</h2>'
            '<p class="meta browse-note">Articles covered by the recovered homepage navigation. '
            '<a href="./index.html">See original section groupings</a>.</p>'
            f'<ol>{"".join(residual_links)}</ol></section>'
        )
    browse_intro = (
        "<h1>Browse All Articles</h1>"
        '<p class="meta">Enhanced recovered browse groups, backed by article IDs, titles, '
        "internal links, and recovered index evidence. "
        "This is a browsing aid — it is not the original homepage navigation. "
        '<a href="./index.html">See recovered homepage navigation</a>.</p>'
    )
    browse_body = browse_intro + '<div class="sections">' + "\n".join(group_cards) + "</div>"
    (out / "articles.html").write_text(page("Browse All Articles", browse_body), encoding="utf-8")

    report = {
        "output": str(out),
        "article_count": len(article_map),
        "article_pages_written": len(article_map),
        "section_count": len(sections),
        "asset_count": len(asset_paths),
        "linked_resource_count": len(resource_paths),
        "missing_internal_reference_count": len(missing_refs),
        "linked_resources": resource_paths,
        "historical_site_url": HISTORICAL_SITE_URL,
        "site_banner": {"output_path": SITE_BANNER_PATH, "capture": banner_record},
        "missing_internal_references": sorted(missing_refs),
        "missing_artifacts_page": "missing-artifacts.html",
        "missing_artifact_anchors": {url: anchor for url, anchor in sorted(missing_refs.items())},
        "missing_artifact_contexts": missing_contexts,
        "homepage_source": {"original": home["original"], "timestamp": home["timestamp"], "local_path": home["local_path"]},
        "navigation_model": "exact_original_homepage_with_unplaced_fallback",
        "unplaced_article_count": len(unplaced),
        "unplaced_articles": unplaced,
        "sections": sections,
        "articles_page_model": "enhanced_browse_with_evidence_groups",
        "enhanced_group_count": len(enhanced_group_records),
        "enhanced_group_article_count": sum(g["article_count"] for g in enhanced_group_records),
        "enhanced_browse_homepage_article_count": len(browse_residual_order),
        "enhanced_groups": enhanced_group_records,
    }
    (out / "_raw-export-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Output: {out}")
    print(f"Articles: {len(article_map)}")
    print(f"Sections (homepage): {len(sections)}")
    print(f"Unplaced (homepage fallback): {len(unplaced)}")
    print(f"Enhanced groups: {len(enhanced_group_records)}")
    print(f"Enhanced group articles: {sum(g['article_count'] for g in enhanced_group_records)}")
    print(f"Browse residual: {len(browse_residual_order)}")
    print(f"Assets: {len(asset_paths)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
