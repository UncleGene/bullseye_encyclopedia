#!/usr/bin/env python3
"""Build a deployable as-is static copy from recovered Wayback captures."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urljoin, urlparse

ARTICLE_SITE_URL = "https://unclegene.github.io/bullseye_encyclopedia/raw/"
ARTICLE_SITE_LABEL = "Read the Clean Edition"

ASSET_EXTENSIONS = {
    ".css",
    ".js",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".svg",
    ".ico",
    ".pdf",
    ".mp3",
    ".wav",
    ".zip",
}
URL_ATTR_RE = re.compile(r"""(?P<prefix>\b(?P<attr>src|href|background|action)\s*=\s*["'])(?P<url>[^"']+)(?P<suffix>["'])""", re.IGNORECASE)
OPTION_VALUE_RE = re.compile(r"""(?P<prefix><option\b[^>]*\bvalue\s*=\s*["'])(?P<url>[^"']+)(?P<suffix>["'])""", re.IGNORECASE)
CSS_URL_RE = re.compile(r"""url\((?P<quote>["']?)(?P<url>[^)'"]+)(?P=quote)\)""", re.IGNORECASE)
SCRIPT_TAG_RE = re.compile(
    r"""(?P<before><script\b[^>]*?\bsrc\s*=\s*)(?P<quote>["'])(?P<src>[^"']+)(?P=quote)(?P<after>[^>]*)>\s*</script>""",
    re.IGNORECASE,
)
JS_STRING_URL_RE = re.compile(
    r"""(?P<quote>["'])(?P<url>(?:(?:https?:)?//(?:www\.)?bullseyepistol\.com/)?[A-Za-z0-9._%/\-]+(?:\.(?:htm|html|js|jpg|jpeg|gif|png|ico|cur|pdf|mp3|wav|zip))(?:\?[^"'#]*)?(?:#[^"']*)?)(?P=quote)""",
    re.IGNORECASE,
)
DYNAMIC_JS_ASSET_PREFIXES = (
    "premium1.jpg?v=",
    "premium2.jpg?v=",
    "premium3.jpg?v=",
)

# Provider-template placeholder captures that do not belong in the release-facing
# as-is site. Preserve them in the raw archive, but do not publish them here.
PRUNED_AS_IS_URLS = {
    "http://bullseyepistol.com/generalappc/scriptcat/945ecf10693ad5cae76c2d8f13e34e66.1",
    "http://bullseyepistol.com/generalappc/javascripts/mydomaincom/input-fields.js",
    "http://bullseyepistol.com/generalappc/javascripts/mydomaincom/jquery.pngfix.pack.js",
    "http://bullseyepistol.com/generalappc/javascripts/mydomaincom/scripts.js",
    "http://bullseyepistol.com/generalappc/javascripts/mydomaincom/superfish.js",
    "http://bullseyepistol.com/generalappc/javascripts/mydomaincom/util-functions.js",
    "http://bullseyepistol.com/helpfile_files/screen7.gif",
    "http://bullseyepistol.com/tournamentz.htm",
    "http://bullseyepistol.com/tyenter.gif",
    "http://bullseyepistol.com/tyhelp.jpg",
    "http://bullseyepistol.com/tylewis.jpg",
    "http://bullseyepistol.com/typix.gif",
}


def load(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
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


def internal_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme and parsed.scheme.lower() not in {"http", "https"}:
        return False
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    if host.endswith(":80"):
        host = host[:-3]
    return not host or host == "bullseyepistol.com" or host.endswith(".bullseyepistol.com")


def url_stem(url: str) -> str:
    parsed = urlparse(url)
    name = Path(unquote(parsed.path or "/")).name or "index"
    stem = re.sub(r"\.[A-Za-z0-9]{1,8}$", "", name)
    return re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-").lower() or "index"


def clean_filename(url: str, content_type: str | None = None) -> str:
    parsed = urlparse(url)
    path = unquote(parsed.path or "/")
    name = Path(path).name or "index"
    suffix = Path(name).suffix
    if not suffix:
        guessed = mimetypes.guess_extension((content_type or "").split(";", 1)[0].strip())
        suffix = guessed or ".bin"
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", Path(name).stem).strip("-") or "file"
    return f"{stem}{suffix.lower()}"


def slugify(value: str, fallback: str = "item") -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return slug or fallback


def article_id_from_url(url: str) -> str | None:
    if not internal_url(url):
        return None
    parsed = urlparse(url)
    name = Path(unquote(parsed.path or "")).name
    if not name:
        return None
    stem = re.sub(r"\.[A-Za-z0-9]{1,8}$", "", name)
    return slugify(stem, "")


def short_article_slug(title: str, article_id: str) -> str:
    value = re.sub(r"\s+by\s+.*$", "", title, flags=re.IGNORECASE)
    value = re.sub(r"\s+for\s+(?:bullseye\s+)?pistol\s+shooters$", "", value, flags=re.IGNORECASE)
    value = re.sub(r"\s+for\s+pistol\s+competition$", "", value, flags=re.IGNORECASE)
    return slugify(value, article_id)


def load_canonical_sections(path: str) -> list[dict[str, Any]]:
    report_path = Path(path)
    if not report_path.exists():
        return []
    data = load(str(report_path))
    return list(data.get("sections", []))


def build_article_paths(
    article_index: dict[str, Any],
    sections: list[dict[str, Any]],
    articles_dir: Path,
) -> tuple[dict[str, Path], dict[str, Any]]:
    article_titles = {str(item["id"]): str(item.get("title") or item["id"]) for item in article_index.get("articles", [])}
    article_ids = set(article_titles)
    section_by_article: dict[str, str] = {}
    label_by_article: dict[str, str] = {}
    non_fallback_articles: set[str] = set()
    fallback_title = "Other Recovered Articles"

    for section in sections:
        title = str(section.get("title") or fallback_title)
        is_fallback = title == fallback_title
        for item in section.get("items", []):
            article_id = str(item.get("article_id", ""))
            if article_id not in article_ids:
                continue
            section_by_article.setdefault(article_id, title)
            label_by_article.setdefault(article_id, str(item.get("label") or article_titles[article_id]))
            if not is_fallback:
                non_fallback_articles.add(article_id)

    child_parent: dict[str, str] = {}
    for parent_id in sorted(non_fallback_articles):
        article_path = articles_dir / f"{parent_id}.json"
        if not article_path.exists():
            continue
        article = load(str(article_path))
        for link in article.get("links", []):
            child_id = article_id_from_url(str(link.get("resolved_url") or link.get("href") or ""))
            if (
                child_id
                and child_id in article_ids
                and child_id != parent_id
                and child_id not in non_fallback_articles
                and child_id not in child_parent
            ):
                child_parent[child_id] = parent_id

    article_paths: dict[str, Path] = {}
    used_dirs: set[Path] = set()
    groups: dict[str, dict[str, Any]] = {}

    def reserve(path: Path, article_id: str) -> Path:
        directory = path.parent
        if directory in used_dirs:
            directory = directory.with_name(f"{directory.name}-{article_id}")
            path = directory / "index.html"
        used_dirs.add(directory)
        return path

    def group_path(section_title: str) -> Path:
        return Path("articles") / slugify(section_title, "other-recovered-articles")

    for article_id, title in sorted(article_titles.items()):
        if article_id in child_parent:
            parent_id = child_parent[article_id]
            section_title = section_by_article.get(parent_id, fallback_title)
            parent_label = label_by_article.get(parent_id, article_titles[parent_id])
            parent_slug = short_article_slug(parent_label, parent_id)
            article_slug = short_article_slug(title, article_id)
            path = group_path(section_title) / parent_slug / article_slug / "index.html"
            groups.setdefault(section_title, {"section": section_title, "articles": [], "subgroups": {}})
            groups[section_title]["subgroups"].setdefault(parent_id, {"article_id": parent_id, "title": article_titles[parent_id], "children": []})
            groups[section_title]["subgroups"][parent_id]["children"].append(article_id)
        else:
            section_title = section_by_article.get(article_id, fallback_title)
            article_slug = short_article_slug(label_by_article.get(article_id, title), article_id)
            path = group_path(section_title) / article_slug / "index.html"
            groups.setdefault(section_title, {"section": section_title, "articles": [], "subgroups": {}})
            groups[section_title]["articles"].append(article_id)
        article_paths[article_id] = reserve(path, article_id)

    group_report = {
        "section_count": len(groups),
        "subgroup_count": sum(len(group["subgroups"]) for group in groups.values()),
        "child_article_count": len(child_parent),
        "sections": [
            {
                "title": section_title,
                "path": group_path(section_title).as_posix(),
                "article_count": len(group["articles"]),
                "subgroups": list(group["subgroups"].values()),
            }
            for section_title, group in sorted(groups.items())
        ],
    }
    return article_paths, group_report


def site_path_for(url: str, content_type: str | None = None, article_paths: dict[str, Path] | None = None) -> Path:
    parsed = urlparse(url)
    path = unquote(parsed.path or "/")
    if path.endswith("/"):
        path += "index.html"
    name = Path(path).name
    suffix = Path(name).suffix
    if not suffix:
        if content_type and "html" in content_type:
            path = path.rstrip("/") + "/index.html"
        else:
            guessed = mimetypes.guess_extension((content_type or "").split(";", 1)[0].strip())
            path = path + (guessed or ".bin")
    if path.lower().endswith(".htm"):
        path = path[:-4] + ".html"
    lowered_suffix = Path(path).suffix.lower()
    stem = url_stem(url)
    is_html = lowered_suffix in {".html", ".htm"} or (content_type and "html" in content_type)
    if is_html:
        if stem == "index":
            return Path("index.html")
        if article_paths and stem in article_paths:
            return article_paths[stem]
        return Path("pages") / stem / "index.html"
    if lowered_suffix == ".js" or (content_type and "javascript" in content_type):
        return Path("shared") / "scripts" / clean_filename(url, content_type)
    if lowered_suffix == ".css" or (content_type and "css" in content_type):
        return Path("shared") / "styles" / clean_filename(url, content_type)
    if lowered_suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico", ".cur"} or (
        content_type and content_type.startswith("image/")
    ):
        return Path("shared") / "images" / clean_filename(url, content_type)
    return Path("shared") / "files" / clean_filename(url, content_type)


def choose_latest_success(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    for record in records:
        if record.get("status") != "success":
            continue
        original = str(record.get("original", ""))
        key = normalize_url(original)
        if key in PRUNED_AS_IS_URLS:
            continue
        previous = selected.get(key)
        if previous is None or str(record.get("timestamp", "")) > str(previous.get("timestamp", "")):
            selected[key] = record
    return selected


def unique_path(path: Path, record: dict[str, Any], used: set[Path]) -> Path:
    if path not in used:
        used.add(path)
        return path
    timestamp = str(record.get("timestamp", "capture"))
    if path.name == "index.html":
        if str(path.parent) == ".":
            candidate = Path(f"index-{timestamp}.html")
        else:
            candidate = path.parent.with_name(f"{path.parent.name}-{timestamp}") / "index.html"
    else:
        candidate = path.with_name(f"{path.stem}-{timestamp}{path.suffix}")
    while candidate in used:
        candidate = candidate.with_name(f"{candidate.stem}-copy{candidate.suffix}")
    used.add(candidate)
    return candidate


def build_url_map(
    backup: dict[str, Any],
    images: dict[str, Any],
    article_paths: dict[str, Path],
) -> tuple[dict[str, dict[str, Any]], dict[str, Path]]:
    all_records = [record for record in backup.get("records", []) if record.get("status") == "success"]
    all_records.extend(record for record in images.get("records", []) if record.get("status") == "success")
    selected = choose_latest_success(all_records)
    path_map: dict[str, Path] = {}
    used: set[Path] = set()
    for key, record in sorted(selected.items()):
        path = site_path_for(
            str(record.get("original")),
            str(record.get("content_type") or record.get("source_mimetype") or ""),
            article_paths,
        )
        path = unique_path(path, record, used)
        path_map[key] = path
    return selected, path_map


def local_url_for(base_original: str, raw_url: str, path_map: dict[str, Path], from_path: Path) -> str | None:
    if raw_url.startswith(("mailto:", "javascript:", "#", "data:")):
        return raw_url
    resolved = urljoin(base_original, raw_url)
    key = normalize_url(resolved)
    target = path_map.get(key)
    if target is None:
        return None
    rel = os.path.relpath(target, start=from_path.parent)
    local = rel.replace(os.sep, "/")
    parsed = urlparse(resolved)
    if parsed.query:
        local += f"?{parsed.query}"
    if parsed.fragment:
        local += f"#{parsed.fragment}"
    return local


def is_generated_script_url(raw_url: str) -> bool:
    parsed = urlparse(raw_url)
    if parsed.scheme or parsed.netloc:
        return False
    return "_scripts" in Path(unquote(parsed.path)).parts


def is_image_record(record: dict[str, Any] | None) -> bool:
    if not record:
        return False
    content_type = str(record.get("content_type") or record.get("source_mimetype") or "").lower()
    suffix = Path(urlparse(str(record.get("original", ""))).path).suffix.lower()
    return content_type.startswith("image/") or suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico", ".cur"}


def article_image_path(article_id: str, record: dict[str, Any], article_paths: dict[str, Path], used: set[Path]) -> Path:
    filename = clean_filename(str(record.get("original", "")), str(record.get("content_type") or record.get("source_mimetype") or ""))
    article_path = article_paths.get(article_id, Path("articles") / article_id / "index.html")
    path = article_path.parent / "images" / filename
    return unique_path(path, record, used)


def copy_record(record: dict[str, Any], dst: Path) -> bool:
    src = Path(str(record.get("local_path", "")))
    if not src.exists():
        src = Path(str(record.get("blob_path", "")))
    if not src.exists():
        return False
    copy_or_link(src, dst)
    return True


def article_specific_image_url(
    base_original: str,
    raw_url: str,
    from_path: Path,
    selected: dict[str, dict[str, Any]],
    out: Path,
    article_id: str | None,
    article_paths: dict[str, Path],
    article_image_paths: dict[tuple[str, str], Path],
    used_article_image_paths: set[Path],
) -> str | None:
    if not article_id:
        return None
    resolved = urljoin(base_original, raw_url)
    key = normalize_url(resolved)
    record = selected.get(key)
    if not is_image_record(record):
        return None
    image_key = (article_id, key)
    rel_path = article_image_paths.get(image_key)
    if rel_path is None:
        rel_path = article_image_path(article_id, record, article_paths, used_article_image_paths)
        article_image_paths[image_key] = rel_path
        copy_record(record, out / rel_path)
    return os.path.relpath(rel_path, start=from_path.parent).replace(os.sep, "/")


def is_script_record(record: dict[str, Any] | None) -> bool:
    if not record:
        return False
    content_type = str(record.get("content_type") or record.get("source_mimetype") or "").lower()
    suffix = Path(urlparse(str(record.get("original", ""))).path).suffix.lower()
    if "html" in content_type:
        return False
    return "javascript" in content_type or (not content_type and suffix == ".js")


def page_script_url(
    base_original: str,
    raw_url: str,
    from_path: Path,
    path_map: dict[str, Path],
    selected: dict[str, dict[str, Any]],
    out: Path,
    missing_notes: dict[str, Path],
    page_scripts: dict[tuple[str, str], Path],
) -> str | None:
    resolved = urljoin(base_original, raw_url)
    key = normalize_url(resolved)
    record = selected.get(key)
    if not is_script_record(record):
        return None
    script_key = (from_path.as_posix(), key)
    rel_path = page_scripts.get(script_key)
    if rel_path is None:
        filename = clean_filename(str(record.get("original", "")), str(record.get("content_type") or record.get("source_mimetype") or ""))
        rel_path = from_path.parent / "_scripts" / filename
        page_scripts[script_key] = rel_path
        src = Path(str(record.get("local_path", "")))
        if not src.exists():
            src = Path(str(record.get("blob_path", "")))
        if src.exists():
            text = src.read_text(encoding="utf-8", errors="ignore")
            rewritten, _missing = rewrite_js(text, str(record.get("original", "")), path_map, from_path, missing_notes)
            dst = out / rel_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                dst.unlink()
            dst.write_text(rewritten, encoding="utf-8")
    version = hashlib.sha256((out / rel_path).read_bytes()).hexdigest()[:12]
    return os.path.relpath(rel_path, start=from_path.parent).replace(os.sep, "/") + f"?v={version}"


def missing_local_url(resolved_url: str, from_path: Path, attr: str, missing_notes: dict[str, Path]) -> str:
    if attr.lower() in {"src", "background"}:
        target = Path("_missing") / "missing-asset.svg"
        return os.path.relpath(target, start=from_path.parent).replace(os.sep, "/")
    normalized = normalize_url(resolved_url)
    missing_notes.setdefault(normalized, Path())
    return resolved_url


def rewrite_urls_in_text(
    text: str,
    base_original: str,
    path_map: dict[str, Path],
    from_path: Path,
    missing_notes: dict[str, Path],
    selected: dict[str, dict[str, Any]],
    out: Path,
    article_id: str | None,
    article_paths: dict[str, Path],
    article_image_paths: dict[tuple[str, str], Path],
    used_article_image_paths: set[Path],
    page_scripts: dict[tuple[str, str], Path],
) -> tuple[str, list[str]]:
    missing: list[str] = []

    def replace_attr(match: re.Match[str]) -> str:
        raw_url = match.group("url")
        if is_generated_script_url(raw_url):
            return match.group(0)
        if match.group("attr").lower() == "src":
            script_local = page_script_url(
                base_original,
                raw_url,
                from_path,
                path_map,
                selected,
                out,
                missing_notes,
                page_scripts,
            )
            if script_local:
                return f"{match.group('prefix')}{script_local}{match.group('suffix')}"
        if match.group("attr").lower() in {"src", "background"}:
            article_local = article_specific_image_url(
                base_original,
                raw_url,
                from_path,
                selected,
                out,
                article_id,
                article_paths,
                article_image_paths,
                used_article_image_paths,
            )
            if article_local:
                return f"{match.group('prefix')}{article_local}{match.group('suffix')}"
        local = local_url_for(base_original, raw_url, path_map, from_path)
        if local is None:
            resolved = urljoin(base_original, raw_url)
            missing.append(resolved)
            if internal_url(resolved):
                local_missing = missing_local_url(resolved, from_path, match.group("attr"), missing_notes)
                return f"{match.group('prefix')}{local_missing}{match.group('suffix')}"
            return match.group(0)
        return f"{match.group('prefix')}{local}{match.group('suffix')}"

    def replace_css(match: re.Match[str]) -> str:
        raw_url = match.group("url")
        local = local_url_for(base_original, raw_url, path_map, from_path)
        if local is None:
            resolved = urljoin(base_original, raw_url)
            missing.append(resolved)
            if internal_url(resolved):
                local_missing = missing_local_url(resolved, from_path, "src", missing_notes)
                return f"url({local_missing})"
            return match.group(0)
        return f"url({local})"

    text = URL_ATTR_RE.sub(replace_attr, text)
    text = CSS_URL_RE.sub(replace_css, text)
    return text, sorted(set(missing))


def rewrite_html(
    text: str,
    base_original: str,
    path_map: dict[str, Path],
    from_path: Path,
    missing_notes: dict[str, Path],
    selected: dict[str, dict[str, Any]],
    out: Path,
    article_id: str | None,
    article_paths: dict[str, Path],
    article_image_paths: dict[tuple[str, str], Path],
    used_article_image_paths: set[Path],
    page_scripts: dict[tuple[str, str], Path],
) -> tuple[str, list[str]]:
    script_missing: list[str] = []
    if url_stem(base_original) == "pi-a":
        member_info = re.search(r'rfram\[1\] = "(.*?)";', text, re.DOTALL)
        if not member_info:
            raise ValueError("Expected recovered club membership description")
        description = member_info.group(1).split("<br><br>Select the")[0]
        text = re.sub(r'<script\b[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\s+onLoad="mStation\(1\)"', '', text, flags=re.IGNORECASE)
        text = re.sub(r'(<div id="rtext">).*?(</div>)', lambda m: m[1] + description + m[2], text, flags=re.DOTALL)

    def replace_script_tag(match: re.Match[str]) -> str:
        raw_url = match.group("src")
        script_local = page_script_url(
            base_original,
            raw_url,
            from_path,
            path_map,
            selected,
            out,
            missing_notes,
            page_scripts,
        )
        if script_local:
            return (
                f"{match.group('before')}{match.group('quote')}{script_local}"
                f"{match.group('quote')}{match.group('after')}></script>"
            )
        resolved = urljoin(base_original, raw_url)
        if internal_url(resolved):
            script_missing.append(resolved)
        return ""

    text = SCRIPT_TAG_RE.sub(replace_script_tag, text)
    text, missing = rewrite_urls_in_text(
        text,
        base_original,
        path_map,
        from_path,
        missing_notes,
        selected,
        out,
        article_id,
        article_paths,
        article_image_paths,
        used_article_image_paths,
        page_scripts,
    )
    missing.extend(script_missing)

    def replace_option(match: re.Match[str]) -> str:
        raw_url = match.group("url")
        # Skip plain form values (numbers, single words) that aren't URL-shaped.
        # urljoin would resolve "5" as bullseyepistol.com/5 and incorrectly mark it missing.
        if raw_url and not any(c in raw_url for c in (".", "/", ":", "?")):
            return match.group(0)
        local = local_url_for(base_original, raw_url, path_map, from_path)
        if local is None:
            resolved = urljoin(base_original, raw_url)
            if raw_url and internal_url(resolved):
                missing.append(resolved)
                local = missing_local_url(resolved, from_path, "href", missing_notes)
                return f"{match.group('prefix')}{local}{match.group('suffix')}"
            return match.group(0)
        return f"{match.group('prefix')}{local}{match.group('suffix')}"

    text = OPTION_VALUE_RE.sub(replace_option, text)
    # Header arguments are navigation URLs, but are not HTML attributes.
    text = re.sub(
        r"\bheader\([^;\n]*\)",
        lambda m: rewrite_js(m.group(0), base_original, path_map, from_path, missing_notes)[0],
        text,
    )
    text = repair_static_controls(text)
    return text, sorted(set(missing))


def rewrite_js(
    text: str,
    base_original: str,
    path_map: dict[str, Path],
    from_path: Path,
    missing_notes: dict[str, Path],
) -> tuple[str, list[str]]:
    missing: list[str] = []

    def replace_string(match: re.Match[str]) -> str:
        raw_url = match.group("url")
        local = local_url_for(base_original, raw_url, path_map, from_path)
        if local is None:
            resolved = urljoin(base_original, raw_url)
            missing.append(resolved)
            if internal_url(resolved):
                local = missing_local_url(resolved, from_path, "href", missing_notes)
                return f"{match.group('quote')}{local}{match.group('quote')}"
            return match.group(0)
        return f"{match.group('quote')}{local}{match.group('quote')}"

    # Two recovered search entries omit the extension, unlike their captures.
    text = text.replace('href="rangecmd"', 'href="rangecmd.htm"').replace('href="links#products"', 'href="links.htm#products"')
    text = text.replace('chaptr10.htm', 'chapter10.htm')
    text = re.sub(r'<a href="(?:https?://(?:www\.)?bullseyepistol\.com/)?bulseyel\.htm">([^<]+)</a>',
                  r'\1 (<a href="https://www.bullseyeforum.net/">current forum</a>)', text, flags=re.IGNORECASE)
    text = re.sub(r'https?://(?:www\.)?bullseyepistol\.forumotion\.com/?', 'https://www.bullseyeforum.net/', text)
    rewritten = JS_STRING_URL_RE.sub(replace_string, text)
    rewritten = re.sub(r'https?://(?:www\.)?nrahq\.org/compete/RuleBooks/Pistol/[^\s\'"<>]+',
                       'https://competitions.nra.org/competition-resources/rule-books/', rewritten, flags=re.IGNORECASE)
    for raw_prefix in DYNAMIC_JS_ASSET_PREFIXES:
        local = local_url_for(base_original, raw_prefix, path_map, from_path)
        if local is not None:
            rewritten = rewritten.replace(raw_prefix, local)
    return repair_static_scripts(rewritten), sorted(set(missing))


def repair_static_scripts(text: str) -> str:
    """Repair recovered client behavior without changing capture bytes."""
    def search(match: re.Match[str]) -> str:
        target = re.search(r'window.location.href\s*=\s*["\']([^"\']+)', match.group(0))
        if not target:
            raise ValueError("Recovered Search function has no destination")
        return (
            'function Search(field) {\n'
            'var query = field.findit.value.trim();\n'
            f'window.location.href = {json.dumps(target.group(1))} + "?q=" + encodeURIComponent(query);\n'
            '}')

    text = re.sub(r'function Search\(field\)\s*\{.*?\n\}', search, text, flags=re.DOTALL)
    text = enable_keyboard_search(text)
    text = re.sub(r'''<a href='" \+ ad[123] \+ "'>(<img[^>]+>)</a>''', r'\1', text)
    text = text.replace("<form action='NOACTION'>", "<form onsubmit='Search(this); return false;'>")
    # These services are replaced by ordinary links on the homepage.
    for name in ("showtime", "mapQuest", "weatherUnderground", "rangeSearch", "nraLook", "bac", "frw"):
        text = re.sub(rf'function {name}\([^)]*\)\s*\{{.*?\n\}}', '', text, flags=re.DOTALL)
    if 'function findTopic()' in text:
        text = text[:text.index('function getCookie(')] + '''function findTopic() {
var query = (new URLSearchParams(window.location.search).get("q") || "").trim().toUpperCase();
if (!query) {
document.write("Enter a word in Search This Site to search the recovered topic index.");
return;
}
var safeQuery = query.replace(/[&<>"']/g, function(c) {
return {"&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"}[c];
});
document.write("Search results for query: <strong>" + safeQuery + "</strong><ol>");
var results = 0;
for (var x = 1; x <= 135; x++) {
if (it[x].indexOf(query) !== -1) {
document.write("<li>" + it[x] + fd[x] + "</li>");
results++;
}
}
document.write("</ol>" + (results ? results + " matching topics." : "There were no matches."));
}
'''
    return text


def enable_keyboard_search(text: str) -> str:
    # Several recovered forms sit between table tags; Enter needs an explicit
    # input handler because browsers repair that invalid nesting differently.
    return re.sub(r'(<input\b[^>]*\bname=["\']findit["\'])',
                  r"\1 onkeydown='if(event.keyCode===13){Search(this.form);return false;}'", text,
                  flags=re.IGNORECASE)


def repair_static_controls(text: str) -> str:
    original = text
    text = re.sub(r'''(?:\s*\|\s*)?<a\b[^>]*href=["']https?://(?:www\.)?facebook\.com/bullseyepistol/?["'][^>]*>.*?</a>''',
                  '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'https?://(?:www\.)?bullseyepistol\.forumotion\.com/?', 'https://www.bullseyeforum.net/', text)
    text = enable_keyboard_search(text)
    text = text.replace('outsideSearch();', '')
    text = re.sub(r'https?://(?:www\.)?(?:nrahq\.org/compete/RuleBooks/Pistol/|compete\.nra\.org/documents/pdf/compete/RuleBooks/Pistol/)[^\s\'"<>]+',
                  'https://competitions.nra.org/competition-resources/rule-books/', text, flags=re.IGNORECASE)
    text = re.sub(r'<form>(?=\s*<td[^>]*[\s\S]{0,120}name="findit")',
                  '<form onsubmit="Search(this); return false;">', text)
    # Retain historical descriptions; remove controls that submit to absent services.
    text = re.sub(r'<form\b[^>]*>.*?</form>',
                  lambda m: '' if any(service in m.group(0).lower() for service in
                      ('paypal.com', 'formmailto.com', 'advertise1.php')) else m.group(0),
                  text, flags=re.IGNORECASE | re.DOTALL)
    return re.sub(r'^[ \t]+$', '', text, flags=re.MULTILINE) if text != original else text


def repair_homepage(text: str) -> str:
    """Keep the recovered visual language while removing inactive services."""
    replacements = {
        "News and Updates": None,
        "Website Statistics": None,
        "Bullseye Twitter Feed": None,
        "Sponsor Our Website": None,
        "Souvenirs and Apparel": None,
        "NRA Classification Lookup": '<a href="https://competitor.nra.org/">Open NRA Competitor Classification Lookup</a>',
        "Find Shooting Ranges": '<a href="https://www.wheretoshoot.org/">Find a range with Where To Shoot</a>',
        "Match Preparations": '<a href="https://www.weather.gov/">Weather forecasts from the National Weather Service</a><br><br><a href="https://www.google.com/maps/dir/">Plan your travel with Google Maps</a>',
    }
    # These widgets have no nested tables; block() emits their opening table.
    for title, body in replacements.items():
        pattern = r'<script[^>]*>block\("' + re.escape(title) + r'"\);</script>.*?</tbody>\s*</table>'
        replacement = '' if body is None else (
            f'<script type="text/javascript">block("{title}");</script>'
            f'<tr><td class="giz" colspan="2">{body}</td></tr></tbody></table>\n')
        text, count = re.subn(pattern, lambda m: replacement, text, count=1, flags=re.DOTALL)
        if count != 1:
            raise ValueError(f"Expected one homepage widget: {title}")
    text, count = re.subn(
        r'<td\s+style="background-color: #22952d; width:336px;">.*?</td>',
        '<td style="background-color:#22952d; width:336px; text-align:center;">'
        '<a style="color:#debea1; font:bold 16px Tahoma,Arial;" '
        'href="https://thecmp.org/cmp-national-matches/">Camp Perry National Matches</a></td>',
        text, count=1, flags=re.DOTALL)
    if count != 1:
        raise ValueError("Expected one expired countdown")
    text = re.sub(r'<td><a href="javascript:(?:bac|frw)\(\);".*?</td>', '', text, flags=re.DOTALL)
    text = text.replace('New material was last added:', 'Recovered homepage capture:')
    text = re.sub(r'<i>Daily</i> Twitter.*?new material is added\.', '', text, flags=re.DOTALL)
    text = text.replace('http://www.nrahq.org/compete/nm_campperry.asp', 'https://thecmp.org/cmp-national-matches/')
    return re.sub(r'^[ \t]+$', '', text, flags=re.MULTILINE)


def rewrite_css(
    text: str,
    base_original: str,
    path_map: dict[str, Path],
    from_path: Path,
    missing_notes: dict[str, Path],
) -> tuple[str, list[str]]:
    return rewrite_urls_in_text(text, base_original, path_map, from_path, missing_notes, {}, Path("."), None, {}, {}, set(), {})


def copy_or_link(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        dst.unlink()
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


_INDEX_TABLE_OLD = 'style="text-align: left; width: 940px;"'
_INDEX_TABLE_NEW = 'style="text-align: left; width: 940px; table-layout: fixed;"'

_LAST_MODIFIED_SCRIPT = re.compile(
    r"""<script\b[^>]*>\s*document\.write\s*\(\s*document\.lastModified\s*\)\s*</script>""",
    re.IGNORECASE,
)
_INDEX_CAPTURE_DATE = "08/18/2025 00:37:37"

_INLINE_EXTERNAL_SCRIPTS = re.compile(
    r"""<script>(?:(?!</script>).)*?(?:"""
    r"""connect\.facebook\.net|platform\.twitter\.com"""
    r""")(?:(?!</script>).)*?</script>""",
    re.DOTALL | re.IGNORECASE,
)
_FB_ROOT_DIV = re.compile(r'<div\s+id=["\']fb-root["\']>\s*</div>\s*', re.IGNORECASE)


def fix_index_table_layout(html: str) -> str:
    """Enforce layout and remove external social-SDK inline loaders from the index page.

    1. Adds table-layout:fixed to the main 3-column content table so form elements in
       the first column cannot override the 260/420/260 px split in modern browsers.
    2. Strips inline scripts that load external social media SDKs (Facebook, Twitter).
       The build script already removes <script src> external scripts; these inline
       loaders use the same pattern but slip through because they have no src attribute.
       Removing them prevents live third-party dependencies in the deployable copy and
       stops the Twitter timeline widget from creating an oversized iframe that overflows
       the first column.
    """
    html = html.replace(_INDEX_TABLE_OLD, _INDEX_TABLE_NEW, 1)
    html = _INLINE_EXTERNAL_SCRIPTS.sub("", html)
    html = _FB_ROOT_DIV.sub("", html)
    html = _LAST_MODIFIED_SCRIPT.sub(_INDEX_CAPTURE_DATE, html)
    return html


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backup", required=True)
    parser.add_argument("--images", required=True)
    parser.add_argument("--article-index", default="content/canonical/articles.index.json")
    parser.add_argument("--articles-dir", default="content/canonical/articles")
    parser.add_argument("--canonical-report", default="exports/static-site/raw/_raw-export-report.json")
    parser.add_argument("--extra-manifest", action="append", default=[])
    parser.add_argument("--out", default="exports/static-site/as-is")
    args = parser.parse_args()

    backup = load(args.backup)
    images = load(args.images)
    article_index = load(args.article_index)
    article_paths, article_group_report = build_article_paths(
        article_index,
        load_canonical_sections(args.canonical_report),
        Path(args.articles_dir),
    )
    extra = {"records": []}
    for path in args.extra_manifest:
        extra["records"].extend(load(path).get("records", []))
    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    selected, path_map = build_url_map({"records": backup.get("records", []) + extra["records"]}, images, article_paths)
    missing_by_page: dict[str, list[str]] = {}
    missing_notes: dict[str, Path] = {}
    article_image_paths: dict[tuple[str, str], Path] = {}
    used_article_image_paths: set[Path] = set()
    page_scripts: dict[tuple[str, str], Path] = {}
    written = 0

    for key, record in sorted(selected.items()):
        src = Path(str(record.get("local_path", "")))
        if not src.exists():
            continue
        dst = out / path_map[key]
        content_type = str(record.get("content_type") or record.get("source_mimetype") or "")
        if "html" in content_type or dst.suffix.lower() in {".html", ".htm"}:
            text = src.read_text(encoding="utf-8", errors="ignore")
            stem = url_stem(str(record.get("original", "")))
            article_id = stem if article_paths.get(stem) == path_map[key] else None
            rewritten, missing = rewrite_html(
                text,
                str(record.get("original")),
                path_map,
                path_map[key],
                missing_notes,
                selected,
                out,
                article_id,
                article_paths,
                article_image_paths,
                used_article_image_paths,
                page_scripts,
            )
            if path_map[key] == Path("index.html"):
                rewritten = fix_index_table_layout(rewritten)
                rewritten = repair_homepage(rewritten)
                callout = (
                    '<div class="edition-callout" style="box-sizing:border-box; width:942px; max-width:100%; '
                    'margin:12px auto; padding:16px 20px; border:2px solid #debea1; background:#103d16; '
                    'color:#fff; text-align:center; font:14px/1.5 Tahoma,Arial,sans-serif;">'
                    f'<a data-site-variant="raw" href="{ARTICLE_SITE_URL}" style="display:inline-block; '
                    'padding:10px 20px; background:#debea1; color:#103d16; '
                    f'font-weight:bold; font-size:20px;">{ARTICLE_SITE_LABEL}</a>'
                    '<p style="margin:8px 0 0; color:#fff;">The same recovered articles, with simpler navigation '
                    'and an uncluttered reading layout.</p></div>'
                )
                rewritten = rewritten.replace("<!-- Bottom Main Table -->", callout + "\n<!-- Bottom Main Table -->", 1)
            version_navigation = (
                '<nav aria-label="Site versions" style="display:block; padding:6px 12px; '
                'background:#22952d; color:#debea1; font:bold 12px/1.5 Tahoma,Arial,sans-serif; text-align:center;">'
                f'<a data-site-variant="raw" href="{ARTICLE_SITE_URL}" style="color:#debea1;">{ARTICLE_SITE_LABEL}</a>'
                ' <span aria-hidden="true"> | </span> '
                '<span aria-current="page">Historical site</span></nav>'
            )
            if path_map[key] != Path("index.html") and not re.search(r"<body\b[^>]*>\s*</body\s*>", rewritten, re.IGNORECASE):
                rewritten, navigation_added = re.subn(
                    r"(<body\b[^>]*>(?:<center>)?[ \t]*\n)",
                    lambda m: m.group(1) + version_navigation + "\n",
                    rewritten, count=1, flags=re.IGNORECASE,
                )
                if not navigation_added:
                    rewritten = re.sub(r"(<body\b[^>]*>)", lambda m: m.group(1) + version_navigation, rewritten, count=1, flags=re.IGNORECASE)
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                dst.unlink()
            dst.write_text(rewritten, encoding="utf-8")
            if missing:
                missing_by_page[str(path_map[key])] = missing
        elif "javascript" in content_type or dst.suffix.lower() == ".js":
            text = src.read_text(encoding="utf-8", errors="ignore")
            rewritten, missing = rewrite_js(text, str(record.get("original")), path_map, path_map[key], missing_notes)
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                dst.unlink()
            dst.write_text(rewritten, encoding="utf-8")
            if missing:
                missing_by_page[str(path_map[key])] = missing
        elif "css" in content_type or dst.suffix.lower() == ".css":
            text = src.read_text(encoding="utf-8", errors="ignore")
            rewritten, missing = rewrite_css(text, str(record.get("original")), path_map, path_map[key], missing_notes)
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                dst.unlink()
            dst.write_text(rewritten, encoding="utf-8")
            if missing:
                missing_by_page[str(path_map[key])] = missing
        else:
            copy_or_link(src, dst)
        written += 1

    missing_dir = out / "_missing"
    missing_dir.mkdir(parents=True, exist_ok=True)
    (missing_dir / "missing-asset.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"></svg>\n',
        encoding="utf-8",
    )
    index_source = None
    for candidate in [
        "http://bullseyepistol.com/",
        "http://bullseyepistol.com/index.htm",
        "http://www.bullseyepistol.com/",
        "https://www.bullseyepistol.com/",
    ]:
        target = path_map.get(normalize_url(candidate))
        if target and (out / target).exists():
            index_source = target
            break
    if index_source and index_source != Path("index.html"):
        copy_or_link(out / index_source, out / "index.html")

    report = {
        "backup_manifest": args.backup,
        "image_manifest": args.images,
        "extra_manifests": args.extra_manifest,
        "output": str(out),
        "article_site_url": ARTICLE_SITE_URL,
        "active_content_policy": {
            "repaired": ["JavaScript header links", "cookie-free escaped topic search", "keyboard search submission"],
            "replaced_with_service_links": ["2015 Camp Perry countdown", "NRA classification", "range search", "weather", "directions"],
            "removed": ["newsletter subscription", "live counter", "embedded social feed", "advertising orders", "PayPal purchases", "souvenir store", "slideshow arrows", "unrecovered club member login", "empty ad redirect links"],
            "unrecovered_slideshow_images": [f"http://www.bullseyepistol.com/image{i}.jpg" for i in range(2, 16)],
            "source_captures_modified": False,
        },
        "records_selected": len(selected),
        "files_written": written,
        "index_source": str(index_source) if index_source else None,
        "pruned_release_artifact_url_count": len(PRUNED_AS_IS_URLS),
        "pruned_release_artifact_urls": sorted(PRUNED_AS_IS_URLS),
        "pages_with_unresolved_local_rewrites": len(missing_by_page),
        "missing_rewrites": missing_by_page,
        "missing_note_count": 0,
        "missing_notes": {},
        "silent_missing_internal_url_count": len(missing_notes),
        "silent_missing_internal_urls": sorted(missing_notes),
        "structure": {
            "articles": "articles/<canonical-section>/<article-or-subgroup>/index.html",
            "sub_articles": "articles/<canonical-section>/<parent-article>/<sub-article>/index.html",
            "article_images": "images/ beside the corresponding grouped article page",
            "shared_images": "shared/images/",
            "shared_scripts": "shared/scripts/",
            "shared_files": "shared/files/",
        },
        "article_groups": article_group_report,
        "article_specific_image_count": len(article_image_paths),
        "notes": [
            "This is the as-is site copy, preserving recovered pages and layout rather than the normalized article presentation.",
            "Recovered local assets and article images are used where a matching capture exists.",
            "External scripts are removed from HTML to avoid live third-party dependencies in the deployable copy.",
        ],
    }
    (out / "_reproduction-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Output: {out}")
    print(f"Files written: {written}")
    print(f"Pages with unresolved rewrites: {len(missing_by_page)}")
    print(f"Report: {out / '_reproduction-report.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
