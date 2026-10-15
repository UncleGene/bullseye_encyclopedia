#!/usr/bin/env python3
"""
Detect likely site engine/platform from recovered raw HTML and URL patterns.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ENGINE_PATTERNS = {
    "WordPress": [r"wp-content", r"wp-includes", r"wp-json", r"xmlrpc\.php"],
    "Joomla": [r"/components/com_", r"/templates/[^/]+/", r"Joomla!"],
    "Drupal": [r"/sites/default/", r"Drupal\.settings", r"content=\"Drupal"],
    "Microsoft FrontPage": [r"Microsoft FrontPage", r"GENERATOR\" content=\"Microsoft", r"_vti_"],
    "Dreamweaver": [r"Dreamweaver", r"MM_preloadImages", r"MM_swapImage"],
    "Blogger": [r"blogger\.com", r"blogspot\.com", r"blogger-templates"],
    "Wix": [r"wixstatic\.com", r"X-Wix"],
    "Squarespace": [r"squarespace", r"static1\.squarespace\.com"],
    "Weebly": [r"weebly\.com", r"weeblycloud"],
}


class EvidenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.generators: list[str] = []
        self.scripts: list[str] = []
        self.stylesheets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {name.lower(): value or "" for name, value in attrs}
        if tag.lower() == "meta" and attr_map.get("name", "").lower() == "generator":
            self.generators.append(attr_map.get("content", ""))
        if tag.lower() == "script" and attr_map.get("src"):
            self.scripts.append(attr_map["src"])
        if tag.lower() == "link" and attr_map.get("rel", "").lower() == "stylesheet" and attr_map.get("href"):
            self.stylesheets.append(attr_map["href"])


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def local_html_records(backup: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        record
        for record in backup.get("records", [])
        if record.get("status") == "success"
        and record.get("local_path")
        and (
            str(record.get("content_type", "")).lower().startswith("text/html")
            or str(record.get("source_mimetype", "")).lower() == "text/html"
        )
    ]


def detect(backup: dict[str, Any]) -> dict[str, Any]:
    html_records = local_html_records(backup)
    suffix_counts = Counter()
    path_markers = Counter()
    scripts = Counter()
    stylesheets = Counter()
    generators = Counter()
    engine_hits: dict[str, list[str]] = {engine: [] for engine in ENGINE_PATTERNS}

    for record in html_records:
        original = str(record.get("original", ""))
        parsed = urlparse(original)
        suffix_counts[Path(parsed.path).suffix.lower() or "[none]"] += 1
        for marker in ("wp-content", "wp-includes", "_vti_", "cgi-bin", "aspnet_client"):
            if marker in original.lower():
                path_markers[marker] += 1

        path = Path(str(record["local_path"]))
        if not path.exists():
            continue
        text = read_text(path)
        parser = EvidenceParser()
        parser.feed(text)
        generators.update(value for value in parser.generators if value)
        scripts.update(parser.scripts)
        stylesheets.update(parser.stylesheets)
        local_evidence = "\n".join([original, *parser.generators, *parser.scripts, *parser.stylesheets])
        for engine, patterns in ENGINE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, local_evidence, flags=re.IGNORECASE):
                    engine_hits[engine].append(f"{original} matched {pattern}")
                    break

    positive_hits = {engine: hits[:20] for engine, hits in engine_hits.items() if hits}
    static_score = suffix_counts[".htm"] + suffix_counts[".html"] + suffix_counts["[none]"]
    cms_score = sum(len(hits) for hits in positive_hits.values())

    frontpage_or_wordpad = sum(
        count
        for generator, count in generators.items()
        if "frontpage" in generator.lower() or "wordpad" in generator.lower()
    )
    if frontpage_or_wordpad and not any(engine for engine in positive_hits if engine != "Microsoft FrontPage"):
        conclusion = "likely_static_html_microsoft_authored"
        likely_engine = "Static HTML authored with Microsoft FrontPage/WordPad"
    elif positive_hits:
        conclusion = "mixed_or_cms_indicators_found"
        likely_engine = max(positive_hits.items(), key=lambda item: len(item[1]))[0]
    elif static_score and cms_score == 0:
        conclusion = "likely_static_html"
        likely_engine = "Static hand-authored HTML or static-site file tree"
    else:
        conclusion = "insufficient_evidence"
        likely_engine = "Unknown"

    return {
        "likely_engine": likely_engine,
        "conclusion": conclusion,
        "html_files_scanned": len(html_records),
        "suffix_counts": dict(suffix_counts),
        "path_markers": dict(path_markers),
        "generator_meta": dict(generators),
        "top_scripts": scripts.most_common(25),
        "top_stylesheets": stylesheets.most_common(25),
        "engine_hits": positive_hits,
        "interpretation": [
            "Many .htm/.html files with no CMS markers supports a static HTML conclusion.",
            "Generator meta tags, CMS paths, or vendor script markers override the static conclusion when present.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backup", required=True)
    parser.add_argument("--out", default="docs/recovery/site-engine-analysis.md")
    args = parser.parse_args()

    backup = json.loads(Path(args.backup).read_text(encoding="utf-8"))
    result = detect(backup)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Site Engine Analysis",
        "",
        f"Backup manifest: `{args.backup}`",
        "",
        f"Likely engine: **{result['likely_engine']}**",
        "",
        f"Conclusion: `{result['conclusion']}`",
        "",
        f"HTML files scanned: `{result['html_files_scanned']}`",
        "",
        "## Evidence",
        "",
        f"- File suffix counts: `{result['suffix_counts']}`",
        f"- Path markers: `{result['path_markers']}`",
        f"- Generator meta tags: `{result['generator_meta']}`",
        f"- Top scripts: `{result['top_scripts'][:10]}`",
        f"- Top stylesheets: `{result['top_stylesheets'][:10]}`",
        "",
        "## Engine Hits",
        "",
    ]
    if result["engine_hits"]:
        for engine, hits in result["engine_hits"].items():
            lines.append(f"### {engine}")
            lines.append("")
            for hit in hits[:10]:
                lines.append(f"- {hit}")
            lines.append("")
    else:
        lines.append("No WordPress, Joomla, Drupal, FrontPage, Dreamweaver, Blogger, Wix, Squarespace, or Weebly markers were found in the scanned raw HTML.")
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            *[f"- {item}" for item in result["interpretation"]],
            "",
        ]
    )
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Likely engine: {result['likely_engine']}")
    print(f"Conclusion: {result['conclusion']}")
    print(f"HTML files scanned: {result['html_files_scanned']}")
    print(f"Report: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
