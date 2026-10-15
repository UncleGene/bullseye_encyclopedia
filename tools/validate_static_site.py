#!/usr/bin/env python3
"""Validate generated static-site links and asset references."""

from __future__ import annotations

import argparse
import html
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse


SKIP_SCHEMES = {"http", "https", "mailto", "tel", "javascript", "data"}


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


def is_local(value: str) -> bool:
    parsed = urlparse(value)
    if parsed.scheme.lower() in SKIP_SCHEMES:
        return False
    if parsed.netloc:
        return False
    return bool(parsed.path)


def target_path(root: Path, html_file: Path, value: str) -> Path:
    parsed = urlparse(value)
    raw_path = unquote(parsed.path)
    if raw_path.startswith("/"):
        return root / raw_path.lstrip("/")
    return (html_file.parent / raw_path).resolve()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("site_root")
    parser.add_argument("--expect-articles", type=int)
    parser.add_argument("--require-all-articles", action="store_true")
    parser.add_argument("--report", default="")
    args = parser.parse_args()

    root = Path(args.site_root).resolve()
    if not root.exists():
        raise SystemExit(f"Site root does not exist: {root}")

    html_files = sorted(root.rglob("*.html"))
    broken: list[dict[str, str]] = []
    local_refs = 0
    external_refs = 0

    for html_file in html_files:
        parser_obj = ReferenceParser()
        parser_obj.feed(html_file.read_text(encoding="utf-8", errors="ignore"))
        for ref in parser_obj.refs:
            value = ref["value"].strip()
            if not is_local(value):
                external_refs += 1
                continue
            local_refs += 1
            target = target_path(root, html_file, value)
            try:
                target.relative_to(root)
            except ValueError:
                broken.append({"file": str(html_file), "reference": value, "reason": "outside site root"})
                continue
            if not target.exists():
                broken.append({"file": str(html_file), "reference": value, "reason": "missing target"})

    article_pages = sorted((root / "articles").glob("*.html")) if (root / "articles").exists() else []
    checks: list[dict[str, Any]] = [
        {"name": "site_root_exists", "passed": root.exists()},
        {"name": "index_exists", "passed": (root / "index.html").exists()},
        {"name": "no_broken_local_refs", "passed": not broken, "broken_count": len(broken)},
    ]
    if args.require_all_articles:
        checks.append({"name": "all_articles_exists", "passed": (root / "articles.html").exists()})
    if args.expect_articles is not None:
        checks.append(
            {
                "name": "expected_article_count",
                "passed": len(article_pages) == args.expect_articles,
                "expected": args.expect_articles,
                "actual": len(article_pages),
            }
        )

    report = {
        "site_root": str(root),
        "html_file_count": len(html_files),
        "article_page_count": len(article_pages),
        "local_reference_count": local_refs,
        "external_reference_count": external_refs,
        "broken_local_references": broken,
        "checks": checks,
        "passed": all(check["passed"] for check in checks),
    }
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
