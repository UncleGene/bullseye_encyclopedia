#!/usr/bin/env python3
"""Classify as-is suppressed missing URLs and unresolved rewrite pages."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


CATEGORY_ORDER = [
    "provider-artifact",
    "hosting-template-artifact",
    "owner-file-candidate",
    "site-decoration",
    "unrecovered-media",
    "unrecovered-article",
]

KNOWN_CLASSIFICATIONS: dict[str, tuple[str, str]] = {
    "http://bullseyepistol.com/advertise1.php": (
        "provider-artifact",
        "Dynamic PHP page; advertising or affiliate rotation, no archived content.",
    ),
    "http://bullseyepistol.com/advertise3.htm": (
        "provider-artifact",
        "Advertising or affiliate page referenced by site chrome, not article content.",
    ),
    "http://bullseyepistol.com/generalappc/javascripts/mydomaincom/input-fields.js": (
        "hosting-template-artifact",
        "Leftover registrar-hosting template JavaScript, not Bullseye article content.",
    ),
    "http://bullseyepistol.com/generalappc/javascripts/mydomaincom/jquery.pngfix.pack.js": (
        "hosting-template-artifact",
        "Leftover registrar-hosting template JavaScript, not Bullseye article content.",
    ),
    "http://bullseyepistol.com/generalappc/javascripts/mydomaincom/scripts.js": (
        "hosting-template-artifact",
        "Leftover registrar-hosting template JavaScript, not Bullseye article content.",
    ),
    "http://bullseyepistol.com/generalappc/javascripts/mydomaincom/superfish.js": (
        "hosting-template-artifact",
        "Leftover registrar-hosting template JavaScript, not Bullseye article content.",
    ),
    "http://bullseyepistol.com/generalappc/javascripts/mydomaincom/util-functions.js": (
        "hosting-template-artifact",
        "Leftover registrar-hosting template JavaScript, not Bullseye article content.",
    ),
    "http://bullseyepistol.com/generalappc/scriptcat/945ecf10693ad5cae76c2d8f13e34e66.1": (
        "hosting-template-artifact",
        "Registrar-hosting template asset, not part of the recovered Bullseye content set.",
    ),
    "http://bullseyepistol.com/tournamentz.htm": (
        "hosting-template-artifact",
        "Recovered as a MyDomain placeholder page rather than Bullseye content; pruned from the release-facing as-is build.",
    ),
    "http://bullseyepistol.com/tyenter.gif": (
        "hosting-template-artifact",
        "Recovered as a MyDomain placeholder page rather than a real image asset; pruned from the release-facing as-is build.",
    ),
    "http://bullseyepistol.com/tyhelp.jpg": (
        "hosting-template-artifact",
        "Recovered as a MyDomain placeholder page rather than a real image asset; pruned from the release-facing as-is build.",
    ),
    "http://bullseyepistol.com/tylewis.jpg": (
        "hosting-template-artifact",
        "Recovered as a MyDomain placeholder page rather than a real image asset; pruned from the release-facing as-is build.",
    ),
    "http://bullseyepistol.com/typix.gif": (
        "hosting-template-artifact",
        "Recovered as a MyDomain placeholder page rather than a real image asset; pruned from the release-facing as-is build.",
    ),
    "http://bullseyepistol.com/handicap.exe": (
        "owner-file-candidate",
        "Windows executable for league handicap scoring; likely owner-supplied.",
    ),
    "http://bullseyepistol.com/ilmoscorecard.pdf": (
        "owner-file-candidate",
        "Il-Mo league scorecard PDF; likely owner-supplied.",
    ),
    "http://bullseyepistol.com/midseasonscorecard.pdf": (
        "owner-file-candidate",
        "Il-Mo mid-season scorecard PDF; likely owner-supplied.",
    ),
    "http://bullseyepistol.com/newshooter.pdf": (
        "owner-file-candidate",
        "New shooter orientation PDF; likely owner-supplied.",
    ),
    "http://bullseyepistol.com/piasaapp.pdf": (
        "owner-file-candidate",
        "PIASA application PDF; likely owner-supplied.",
    ),
    "http://bullseyepistol.com/pom2004.zip": (
        "owner-file-candidate",
        "League data archive; likely owner-supplied.",
    ),
    "http://bullseyepistol.com/signupform.pdf": (
        "owner-file-candidate",
        "League signup form PDF; likely owner-supplied.",
    ),
    "http://bullseyepistol.com/teamadmin2004.zip": (
        "owner-file-candidate",
        "Team administration archive; likely owner-supplied.",
    ),
    "http://bullseyepistol.com/arpc.gif": (
        "site-decoration",
        "Club-logo image used as page decoration or navigation, not article content.",
    ),
    "http://bullseyepistol.com/canton.gif": (
        "site-decoration",
        "Club-logo image used as page decoration or navigation, not article content.",
    ),
    "http://bullseyepistol.com/dbgc.gif": (
        "site-decoration",
        "Club-logo image used as page decoration or navigation, not article content.",
    ),
    "http://bullseyepistol.com/delaware.gif": (
        "site-decoration",
        "Club-logo image used as page decoration or navigation, not article content.",
    ),
    "http://bullseyepistol.com/fadebar3.jpg": (
        "site-decoration",
        "Navigation fade-bar image; site chrome with no article value.",
    ),
    "http://bullseyepistol.com/wlgc.gif": (
        "site-decoration",
        "Club-logo image used as page decoration or navigation, not article content.",
    ),
    "http://bullseyepistol.com/bubba.wav": (
        "unrecovered-media",
        "Standalone audio file referenced by tournament pages; not present in the selected captures.",
    ),
    "http://bullseyepistol.com/chaptr10.htm": (
        "unrecovered-article",
        "Variant URL for a chapter article; content exists under a different recovered URL.",
    ),
    "http://bullseyepistol.com/gilhebar.htm": (
        "unrecovered-article",
        "Linked content page not present in the selected baseline or overlay captures.",
    ),
    "http://bullseyepistol.com/help.htm": (
        "unrecovered-article",
        "Help page linked by recovered content but not captured in the selected baseline.",
    ),
    "http://bullseyepistol.com/perchamp.htm": (
        "unrecovered-article",
        "Likely Camp Perry championship page not present in the selected captures.",
    ),
    "http://bullseyepistol.com/statoffice.htm": (
        "unrecovered-article",
        "State office page linked by recovered content but not captured in the selected baseline.",
    ),
}


def normalize_internal_url(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    if host.endswith(":80"):
        host = host[:-3]
    path = parsed.path or "/"
    return f"http://{host}{path}".lower()


def is_internal(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return False
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    if host.endswith(":80"):
        host = host[:-3]
    return host in {"", "bullseyepistol.com"}


def classify_url(url: str) -> dict[str, str]:
    normalized = normalize_internal_url(url)
    category, reason = KNOWN_CLASSIFICATIONS.get(
        normalized,
        ("unclassified", "No classification entry found; manual review needed."),
    )
    return {"url": url, "normalized_url": normalized, "category": category, "reason": reason}


def classify_suppressed_urls(urls: list[str]) -> list[dict[str, str]]:
    results = [classify_url(url) for url in urls]
    results.sort(key=lambda item: (CATEGORY_ORDER.index(item["category"]) if item["category"] in CATEGORY_ORDER else 99, item["normalized_url"]))
    return results


def classify_rewrite_pages(missing_rewrites: dict[str, list[str] | str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rewrite_pages: list[dict[str, Any]] = []
    internal_inventory: dict[str, dict[str, Any]] = {}

    for page_path, raw_urls in sorted(missing_rewrites.items()):
        urls = raw_urls if isinstance(raw_urls, list) else [raw_urls]
        internal_items = [classify_url(url) for url in urls if is_internal(url)]
        external_urls = sorted(url for url in urls if not is_internal(url))

        if internal_items and external_urls:
            page_category = "mixed"
        elif internal_items:
            page_category = "internal-only"
        else:
            page_category = "external-only"

        rewrite_pages.append(
            {
                "page": page_path,
                "category": page_category,
                "internal_ref_count": len(internal_items),
                "external_ref_count": len(external_urls),
                "internal_refs": internal_items,
                "external_ref_sample": external_urls[:5],
            }
        )

        for item in internal_items:
            bucket = internal_inventory.setdefault(
                item["normalized_url"],
                {
                    "url": item["url"],
                    "normalized_url": item["normalized_url"],
                    "category": item["category"],
                    "reason": item["reason"],
                    "ref_count": 0,
                    "pages": [],
                },
            )
            bucket["ref_count"] += 1
            bucket["pages"].append(page_path)

    internal_summary = sorted(
        internal_inventory.values(),
        key=lambda item: (
            CATEGORY_ORDER.index(item["category"]) if item["category"] in CATEGORY_ORDER else 99,
            item["normalized_url"],
        ),
    )
    return rewrite_pages, internal_summary


def write_markdown(
    suppressed: list[dict[str, Any]],
    rewrite_pages: list[dict[str, Any]],
    internal_summary: list[dict[str, Any]],
    out_path: Path,
) -> None:
    suppressed_by_category = Counter(item["category"] for item in suppressed)
    internal_by_category = Counter(item["category"] for item in internal_summary)
    page_by_category = Counter(item["category"] for item in rewrite_pages)
    total_internal_refs = sum(item["ref_count"] for item in internal_summary)
    total_external_refs = sum(item["external_ref_count"] for item in rewrite_pages)

    lines = [
        "# As-Is Missing Resource Classification",
        "",
        "Date: 2026-05-29",
        "",
        "## Scope",
        "",
        "Classifies the reader-suppressed internal missing URLs and the unresolved rewrite pages",
        "in `exports/static-site/as-is`. This is an analysis report only.",
        "",
        "## Suppressed Internal URLs",
        "",
        f"Total suppressed internal URLs: {len(suppressed)}",
        "",
        "| Category | Count |",
        "| --- | ---: |",
    ]
    for category in CATEGORY_ORDER + ["unclassified"]:
        count = suppressed_by_category.get(category, 0)
        if count:
            lines.append(f"| {category} | {count} |")
    lines.append("")

    for category in CATEGORY_ORDER + ["unclassified"]:
        items = [item for item in suppressed if item["category"] == category]
        if not items:
            continue
        lines.extend([f"### {category}", ""])
        for item in items:
            lines.extend(
                [
                    f"- `{item['url']}`",
                    f"  - Reason: {item['reason']}",
                ]
            )
        lines.append("")

    lines.extend(
        [
            "## Unresolved Rewrite Pages",
            "",
            f"Total pages with unresolved rewrites: {len(rewrite_pages)}",
            f"Total external unresolved refs: {total_external_refs}",
            f"Total internal unresolved refs: {total_internal_refs}",
            "",
            "| Page bucket | Pages |",
            "| --- | ---: |",
            f"| external-only | {page_by_category.get('external-only', 0)} |",
            f"| mixed | {page_by_category.get('mixed', 0)} |",
            f"| internal-only | {page_by_category.get('internal-only', 0)} |",
            "",
            "### Internal unresolved URL inventory",
            "",
            f"Unique internal unresolved URLs: {len(internal_summary)}",
            "",
            "| Category | Unique URLs | Reference Count |",
            "| --- | ---: | ---: |",
        ]
    )
    for category in CATEGORY_ORDER + ["unclassified"]:
        category_items = [item for item in internal_summary if item["category"] == category]
        if not category_items:
            continue
        lines.append(
            f"| {category} | {len(category_items)} | {sum(item['ref_count'] for item in category_items)} |"
        )
    lines.append("")

    for category in CATEGORY_ORDER + ["unclassified"]:
        items = [item for item in internal_summary if item["category"] == category]
        if not items:
            continue
        lines.extend([f"### Internal unresolved: {category}", ""])
        for item in items:
            page_sample = ", ".join(f"`{page}`" for page in item["pages"][:3])
            extra = ""
            if len(item["pages"]) > 3:
                extra = f" (+{len(item['pages']) - 3} more)"
            lines.extend(
                [
                    f"- `{item['url']}`",
                    f"  - Refs: {item['ref_count']}",
                    f"  - Pages: {page_sample}{extra}" if page_sample else "  - Pages: none recorded",
                    f"  - Reason: {item['reason']}",
                ]
            )
        lines.append("")

    lines.extend(
        [
            "## Findings Summary",
            "",
            f"- `as-is` suppresses `{len(suppressed)}` internal missing URLs from reader-facing pages.",
            f"- The unresolved rewrite inventory contains `{len(internal_summary)}` unique internal URLs and `{total_external_refs}` external references.",
            f"- Hosting-template artifacts account for `{internal_by_category.get('hosting-template-artifact', 0)}` unique internal unresolved URLs and are concentrated in provider-generated `pages/*` captures.",
            f"- Owner-file candidates account for `{suppressed_by_category.get('owner-file-candidate', 0)}` suppressed URLs and should be the first owner-recovery request set.",
            "",
            "## Recommended Follow-Up Slices",
            "",
            "1. **Owner-file recovery request:** Ask the site owner for the 8 PDFs, ZIPs, and EXE files still missing from recovery.",
            "2. **As-is provider-artifact cleanup:** Decide whether provider-hosting template pages and decorative unresolved assets should remain in the as-is export or be pruned from future builds.",
            "3. **Historical-gap acknowledgement:** Keep the unrecovered article/media URLs in handoff and audit docs as explicit historical gaps.",
        ]
    )

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reproduction-report", default="exports/static-site/as-is/_reproduction-report.json")
    parser.add_argument("--out-md", default="docs/recovery/as-is-missing-resource-classification.md")
    parser.add_argument("--out-json", default="exports/output-audit/as-is-missing-resource-classification.json")
    args = parser.parse_args()

    repro = json.loads(Path(args.reproduction_report).read_text(encoding="utf-8"))
    suppressed_urls = list(repro.get("silent_missing_internal_urls") or [])
    rewrite_pages, internal_summary = classify_rewrite_pages(repro.get("missing_rewrites") or {})
    suppressed = classify_suppressed_urls(suppressed_urls)

    report = {
        "suppressed_internal_url_count": len(suppressed),
        "suppressed_internal_urls": suppressed,
        "suppressed_by_category": dict(Counter(item["category"] for item in suppressed)),
        "rewrite_page_count": len(rewrite_pages),
        "rewrite_page_buckets": dict(Counter(item["category"] for item in rewrite_pages)),
        "internal_unresolved_url_count": len(internal_summary),
        "internal_unresolved_urls": internal_summary,
        "internal_unresolved_by_category": dict(Counter(item["category"] for item in internal_summary)),
        "external_unresolved_ref_count": sum(item["external_ref_count"] for item in rewrite_pages),
    }

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(suppressed, rewrite_pages, internal_summary, Path(args.out_md))

    print(f"Suppressed internal URLs: {len(suppressed)}")
    for category, count in sorted(report["suppressed_by_category"].items()):
        print(f"  suppressed {category}: {count}")
    print(f"Rewrite pages: {len(rewrite_pages)}")
    for category, count in sorted(report["rewrite_page_buckets"].items()):
        print(f"  page bucket {category}: {count}")
    print(f"Internal unresolved URLs: {len(internal_summary)}")
    for category, count in sorted(report["internal_unresolved_by_category"].items()):
        print(f"  internal {category}: {count}")
    print(f"External unresolved refs: {report['external_unresolved_ref_count']}")
    print(f"Markdown: {args.out_md}")
    print(f"JSON: {args.out_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
