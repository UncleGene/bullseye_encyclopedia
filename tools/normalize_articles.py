#!/usr/bin/env python3
"""Extract canonical article records from recovered Bullseye Pistol HTML."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import re
import sys
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urldefrag, urljoin, urlparse

from wayback_backup import write_json


ARTICLE_BEGIN_RE = re.compile(r"<!--\s*=+\s*ARTICLE BEGINS HERE\s*=+\s*-->", re.IGNORECASE)
ARTICLE_END_RE = re.compile(r"<!--\s*=+\s*ARTICLE ENDS HERE\s*=+\s*-->", re.IGNORECASE)
HEADER_RE = re.compile(r"header\(\s*(['\"])(.*?)\1\s*,\s*(['\"])(.*?)\3\s*,\s*(['\"])(.*?)\5\s*\)", re.IGNORECASE | re.DOTALL)
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".ico"}


class TextAndRefsParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.text_parts: list[str] = []
        self.links: list[dict[str, str]] = []
        self.images: list[dict[str, str]] = []
        self._link_stack: list[str] = []
        self._current_link_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = {name.lower(): value or "" for name, value in attrs}
        if tag.lower() == "a" and attrs_map.get("href"):
            self._link_stack.append(attrs_map["href"])
            self._current_link_text = []
        if tag.lower() == "img" and attrs_map.get("src"):
            self.images.append(
                {
                    "src": html.unescape(attrs_map["src"].strip()),
                    "alt": html.unescape(attrs_map.get("alt", "").strip()),
                }
            )
        if tag.lower() in {"p", "br", "div", "tr", "li", "h1", "h2", "h3", "blockquote"}:
            self.text_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._link_stack:
            href = self._link_stack.pop()
            text = clean_text(" ".join(self._current_link_text))
            self.links.append({"href": html.unescape(href.strip()), "text": text})
            self._current_link_text = []
        if tag.lower() in {"p", "div", "tr", "li", "h1", "h2", "h3", "blockquote"}:
            self.text_parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not data:
            return
        self.text_parts.append(data)
        if self._link_stack:
            self._current_link_text.append(data)


def clean_text(value: str) -> str:
    return SPACE_RE.sub(" ", html.unescape(value or "")).strip()


def html_to_text(value: str) -> str:
    parser = TextAndRefsParser()
    parser.feed(value)
    lines = [clean_text(line) for line in "".join(parser.text_parts).splitlines()]
    return "\n".join(line for line in lines if line)


def parse_refs(value: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    parser = TextAndRefsParser()
    parser.feed(value)
    return parser.links, parser.images


def normalize_original_url(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    if host.endswith(":80"):
        host = host[:-3]
    path = parsed.path or "/"
    if path == "/":
        path = "/index.htm"
    return f"http://{host}{path}"


def article_id_for(url: str) -> str:
    parsed = urlparse(normalize_original_url(url))
    path = parsed.path.strip("/") or "index.htm"
    stem = re.sub(r"\.[A-Za-z0-9]{1,8}$", "", path)
    stem = re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-").lower()
    return stem or "index"


def capture_id(record: dict[str, Any]) -> str:
    digest_source = f"{record.get('timestamp')} {record.get('original')} {record.get('sha256')}"
    return hashlib.sha1(digest_source.encode("utf-8")).hexdigest()[:16]


def extract_title_metadata(text: str) -> dict[str, str | None]:
    header_match = HEADER_RE.search(text)
    title = None
    byline = None
    parent = None
    if header_match:
        title = clean_text(header_match.group(2))
        byline = clean_text(header_match.group(4)) or None
        parent = clean_text(header_match.group(6)) or None
    title_match = TITLE_RE.search(text)
    html_title = clean_text(TAG_RE.sub("", title_match.group(1))) if title_match else None
    return {"title": title or html_title, "byline": byline, "parent_url": parent, "html_title": html_title}


def extract_body(raw_html: str) -> tuple[str, str, list[str]]:
    omitted = ["head", "script header/footer", "global style"]
    begin = ARTICLE_BEGIN_RE.search(raw_html)
    end = ARTICLE_END_RE.search(raw_html)
    if begin and end and end.start() > begin.end():
        return raw_html[begin.end() : end.start()].strip(), "recovered", omitted
    if begin:
        tail = raw_html[begin.end() :]
        footer_pos = tail.lower().find("<script>footer()")
        if footer_pos != -1:
            tail = tail[:footer_pos]
        body_end = tail.lower().find("</body>")
        if body_end != -1:
            tail = tail[:body_end]
        return tail.strip(), "partial", omitted + ["missing ARTICLE ENDS marker"]
    return "", "not_article", omitted + ["no ARTICLE BEGINS marker"]


def build_image_index(image_manifest: dict[str, Any]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    index: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in image_manifest.get("records", []):
        if record.get("status") != "success":
            continue
        key = (str(record.get("article_original", "")), normalize_url(str(record.get("resolved_url") or record.get("original", ""))))
        index[key].append(record)
    return index


def normalize_url(url: str) -> str:
    resolved, _fragment = urldefrag(url)
    parsed = urlparse(resolved)
    scheme = parsed.scheme.lower() or "http"
    host = parsed.netloc.lower()
    if host.endswith(":80"):
        host = host[:-3]
    path = parsed.path or "/"
    return f"{scheme}://{host}{path}"


def resolve_ref(base_url: str, ref: str) -> str:
    resolved, _fragment = urldefrag(urljoin(base_url, ref.strip()))
    return resolved


def asset_id_for(record: dict[str, Any]) -> str:
    sha = str(record.get("sha256", ""))
    if sha:
        return f"asset-{sha[:16]}"
    fallback = hashlib.sha1(str(record).encode("utf-8")).hexdigest()[:16]
    return f"asset-{fallback}"


def choose_best(records: list[dict[str, Any]]) -> dict[str, Any]:
    article_records = [record for record in records if record.get("article_status") in {"recovered", "partial"}]
    candidates = article_records or records
    return max(candidates, key=lambda record: str(record.get("wayback_timestamp", "")))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backup", required=True)
    parser.add_argument("--images", required=True)
    parser.add_argument("--out", default="content/canonical")
    parser.add_argument("--normalized-out", default="archive/normalized")
    args = parser.parse_args()

    backup = json.loads(Path(args.backup).read_text(encoding="utf-8"))
    image_manifest = json.loads(Path(args.images).read_text(encoding="utf-8"))
    image_index = build_image_index(image_manifest)
    out = Path(args.out)
    articles_dir = out / "articles"
    shells_dir = out / "page-shells"
    assets_dir = Path("content/assets")
    articles_dir.mkdir(parents=True, exist_ok=True)
    shells_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    shells: list[dict[str, Any]] = []
    assets: dict[str, dict[str, Any]] = {}

    for record in backup.get("records", []):
        if record.get("status") != "success" or record.get("classification") != "article_candidate":
            continue
        local_path = Path(str(record.get("local_path", "")))
        if not local_path.exists():
            continue
        raw_html = local_path.read_text(encoding="utf-8", errors="ignore")
        body_html, article_status, omitted = extract_body(raw_html)
        metadata = extract_title_metadata(raw_html)
        normalized_original = normalize_original_url(str(record.get("original", "")))
        article_id = article_id_for(str(record.get("original", "")))
        links, images = parse_refs(body_html)
        resolved_links = [
            {
                "href": link["href"],
                "resolved_url": resolve_ref(str(record.get("original", "")), link["href"]),
                "text": link["text"],
            }
            for link in links
        ]
        resolved_images: list[dict[str, Any]] = []
        for image_ref in images:
            resolved = resolve_ref(str(record.get("original", "")), image_ref["src"])
            image_records = image_index.get((str(record.get("original", "")), normalize_url(resolved)), [])
            asset_ids: list[str] = []
            for image_record in image_records:
                asset_id = asset_id_for(image_record)
                asset_ids.append(asset_id)
                assets[asset_id] = {
                    "id": asset_id,
                    "original_urls": sorted({str(image_record.get("original", "")), str(image_record.get("resolved_url", ""))}),
                    "file_path": image_record.get("local_path"),
                    "blob_path": image_record.get("blob_path"),
                    "media_type": image_record.get("content_type"),
                    "checksum": image_record.get("sha256"),
                    "provenance": {
                        "wayback_timestamp": image_record.get("timestamp"),
                        "parent_article_original": image_record.get("article_original"),
                        "parent_article_timestamp": image_record.get("article_timestamp"),
                        "retrieval_url": image_record.get("retrieval_url"),
                    },
                    "status": "recovered",
                }
            resolved_images.append(
                {
                    "src": image_ref["src"],
                    "alt": image_ref["alt"],
                    "resolved_url": resolved,
                    "asset_ids": sorted(set(asset_ids)),
                    "status": "recovered" if asset_ids else "unresolved",
                }
            )
        capture = {
            "capture_id": capture_id(record),
            "article_id": article_id,
            "normalized_original_url": normalized_original,
            "original_url": record.get("original"),
            "wayback_timestamp": record.get("timestamp"),
            "local_path": record.get("local_path"),
            "blob_path": record.get("blob_path"),
            "sha256": record.get("sha256"),
            "retrieval_url": record.get("retrieval_url"),
            "title": metadata["title"],
            "byline": metadata["byline"],
            "parent_url": metadata["parent_url"],
            "html_title": metadata["html_title"],
            "article_status": article_status,
            "body_html": body_html,
            "body_text": html_to_text(body_html),
            "links": resolved_links,
            "images": resolved_images,
            "omitted_chrome": omitted,
        }
        if article_status in {"recovered", "partial"}:
            groups[article_id].append(capture)
        else:
            shells.append(capture)

    article_index: list[dict[str, Any]] = []
    for article_id, captures in sorted(groups.items()):
        best = choose_best(captures)
        text_hashes = Counter(hashlib.sha256(capture["body_text"].encode("utf-8")).hexdigest() for capture in captures)
        original_urls = sorted({str(capture["original_url"]) for capture in captures})
        article = {
            "id": article_id,
            "status": "recovered" if best["article_status"] == "recovered" else "partial",
            "title": best["title"] or article_id.replace("-", " ").title(),
            "byline": best["byline"],
            "published_at": None,
            "updated_at": None,
            "original_urls": original_urls,
            "preferred_original_url": best["original_url"],
            "body": {"format": "html", "html": best["body_html"], "text": best["body_text"]},
            "context": {
                "parent_url": best["parent_url"],
                "html_title": best["html_title"],
            },
            "omitted_chrome": best["omitted_chrome"],
            "assets": sorted({asset_id for image in best["images"] for asset_id in image["asset_ids"]}),
            "images": best["images"],
            "links": best["links"],
            "provenance": {
                "selected_capture_id": best["capture_id"],
                "capture_count": len(captures),
                "captures": [
                    {
                        "capture_id": capture["capture_id"],
                        "original_url": capture["original_url"],
                        "wayback_timestamp": capture["wayback_timestamp"],
                        "local_path": capture["local_path"],
                        "sha256": capture["sha256"],
                        "article_status": capture["article_status"],
                    }
                    for capture in sorted(captures, key=lambda row: str(row["wayback_timestamp"]))
                ],
                "body_variant_count": len(text_hashes),
            },
        }
        write_json(articles_dir / f"{article_id}.json", article)
        article_index.append(
            {
                "id": article_id,
                "title": article["title"],
                "status": article["status"],
                "preferred_original_url": article["preferred_original_url"],
                "capture_count": len(captures),
                "body_variant_count": len(text_hashes),
                "asset_count": len(article["assets"]),
                "link_count": len(article["links"]),
            }
        )

    shell_index: list[dict[str, Any]] = []
    for shell in shells:
        shell_record = {
            "id": shell["article_id"],
            "source_capture_id": shell["capture_id"],
            "original_url": shell["original_url"],
            "wayback_timestamp": shell["wayback_timestamp"],
            "local_path": shell["local_path"],
            "template_markers": ["no ARTICLE BEGINS/ENDS marker"],
            "navigation_links": shell["links"],
            "excluded_regions": shell["omitted_chrome"],
            "status": "page_shell",
        }
        shell_path = shells_dir / f"{shell['article_id']}-{shell['wayback_timestamp']}.json"
        write_json(shell_path, shell_record)
        shell_index.append({"id": shell_record["id"], "original_url": shell_record["original_url"], "path": str(shell_path)})

    write_json(out / "articles.index.json", {"count": len(article_index), "articles": article_index})
    write_json(out / "page-shells.index.json", {"count": len(shell_index), "page_shells": shell_index})
    write_json(assets_dir / "assets.index.json", {"count": len(assets), "assets": sorted(assets.values(), key=lambda row: row["id"])})

    report = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "backup_manifest": args.backup,
        "image_manifest": args.images,
        "article_records": len(article_index),
        "page_shell_records": len(shell_index),
        "asset_records": len(assets),
        "article_status_counts": dict(Counter(item["status"] for item in article_index)),
        "articles_with_variants": sum(1 for item in article_index if item["body_variant_count"] > 1),
        "articles_with_assets": sum(1 for item in article_index if item["asset_count"] > 0),
        "notes": [
            "Article bodies are extracted from ARTICLE BEGINS/ENDS comment regions when present.",
            "Header/footer JavaScript, global styles, and template wrapper markup are omitted from canonical article bodies.",
            "Records without article markers are retained as page shells, not canonical articles.",
        ],
    }
    normalized_out = Path(args.normalized_out)
    write_json(normalized_out / "article-normalization-report.json", report)
    print(f"Articles: {len(article_index)}")
    print(f"Page shells: {len(shell_index)}")
    print(f"Assets: {len(assets)}")
    print(f"Articles with variants: {report['articles_with_variants']}")
    print(f"Report: {normalized_out / 'article-normalization-report.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
