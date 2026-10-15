#!/usr/bin/env python3
"""
Discover Wayback captures for bullseyepistol.com and score likely restoration
baseline periods by recency and capture completeness.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen


CDX_URL = "https://web.archive.org/cdx"
FIELDS = ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]
ARTICLE_EXTENSIONS = {"", ".html", ".htm", ".php", ".asp", ".aspx", ".jsp", ".shtml"}
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
    ".doc",
    ".docx",
    ".zip",
    ".mp3",
    ".mp4",
    ".mov",
}
ACTIVE_HINTS = {
    "search",
    "comment",
    "comments",
    "feed",
    "rss",
    "atom",
    "wp-login",
    "wp-admin",
    "xmlrpc",
    "contact",
}
INDEX_HINTS = {
    "category",
    "tag",
    "author",
    "page",
    "archive",
    "archives",
    "topics",
}


@dataclass(frozen=True)
class Capture:
    urlkey: str
    timestamp: str
    original: str
    mimetype: str
    statuscode: str
    digest: str
    length: str
    source_query: str
    classification: str


def fetch_cdx(query: str, limit: int | None, retries: int = 3) -> list[dict[str, str]]:
    params = {
        "url": query,
        "output": "json",
        "fl": ",".join(FIELDS),
        "filter": "statuscode:200",
    }
    if limit:
        params["limit"] = str(limit)
    url = f"{CDX_URL}?{urlencode(params)}"
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            request = Request(url, headers={"User-Agent": "bullseye-recovery/0.1"})
            with urlopen(request, timeout=60) as response:
                payload = response.read().decode("utf-8")
            rows = json.loads(payload)
            if not rows:
                return []
            header = rows[0]
            return [dict(zip(header, row)) for row in rows[1:]]
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(2 * attempt)
    raise RuntimeError(f"CDX query failed for {query}: {last_error}")


def classify(record: dict[str, str]) -> str:
    original = record.get("original", "")
    parsed = urlparse(original)
    path = parsed.path.lower()
    suffix = Path(path).suffix
    mimetype = record.get("mimetype", "").lower()
    parts = {part for part in re.split(r"[^a-z0-9]+", path) if part}

    if suffix in ASSET_EXTENSIONS:
        return "asset"
    if mimetype and not any(token in mimetype for token in ("html", "text/plain")):
        return "asset"
    if parts & ACTIVE_HINTS or parsed.query:
        return "active_dynamic"
    if parts & INDEX_HINTS:
        return "index_navigation"
    if suffix in ARTICLE_EXTENSIONS:
        return "article_candidate"
    return "non_content"


def normalize_capture(row: dict[str, str], source_query: str) -> Capture:
    return Capture(
        urlkey=row.get("urlkey", ""),
        timestamp=row.get("timestamp", ""),
        original=row.get("original", ""),
        mimetype=row.get("mimetype", ""),
        statuscode=row.get("statuscode", ""),
        digest=row.get("digest", ""),
        length=row.get("length", ""),
        source_query=source_query,
        classification=classify(row),
    )


def dedupe_captures(captures: Iterable[Capture]) -> list[Capture]:
    seen: set[tuple[str, str, str]] = set()
    unique: list[Capture] = []
    for capture in captures:
        key = (capture.timestamp, capture.original, capture.digest)
        if key in seen:
            continue
        seen.add(key)
        unique.append(capture)
    return unique


def period_for(timestamp: str, granularity: str) -> str:
    if granularity == "day":
        return timestamp[:8]
    if granularity == "month":
        return timestamp[:6]
    raise ValueError(f"Unsupported granularity: {granularity}")


def parse_timestamp(timestamp: str) -> dt.datetime:
    return dt.datetime.strptime(timestamp[:14], "%Y%m%d%H%M%S")


def score_periods(captures: list[Capture], granularity: str) -> list[dict[str, object]]:
    periods: dict[str, list[Capture]] = defaultdict(list)
    for capture in captures:
        if capture.timestamp:
            periods[period_for(capture.timestamp, granularity)].append(capture)

    latest_ts = max((parse_timestamp(c.timestamp) for c in captures if c.timestamp), default=None)
    rows: list[dict[str, object]] = []
    for period, items in periods.items():
        unique_urls = {item.original for item in items}
        unique_articles = {
            item.original
            for item in items
            if item.classification in {"article_candidate", "index_navigation"}
        }
        article_candidates = {
            item.original for item in items if item.classification == "article_candidate"
        }
        assets = {item.original for item in items if item.classification == "asset"}
        latest_in_period = max(parse_timestamp(item.timestamp) for item in items if item.timestamp)
        days_old = (latest_ts - latest_in_period).days if latest_ts else 0
        recency_score = max(0.0, 1.0 - min(days_old, 3650) / 3650)
        coverage_score = len(article_candidates) * 5 + len(unique_articles) * 2 + len(assets) * 0.25
        score = coverage_score + recency_score * 10
        rows.append(
            {
                "period": period,
                "granularity": granularity,
                "score": round(score, 3),
                "latest_capture": latest_in_period.strftime("%Y%m%d%H%M%S"),
                "unique_urls": len(unique_urls),
                "article_candidates": len(article_candidates),
                "article_or_index": len(unique_articles),
                "assets": len(assets),
                "active_dynamic": len(
                    {item.original for item in items if item.classification == "active_dynamic"}
                ),
                "non_content": len(
                    {item.original for item in items if item.classification == "non_content"}
                ),
                "days_from_latest": days_old,
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            float(row["score"]),
            int(row["article_candidates"]),
            int(row["unique_urls"]),
            str(row["latest_capture"]),
        ),
        reverse=True,
    )


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", default="bullseyepistol.com")
    parser.add_argument("--out", default="archive/raw/wayback")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--granularity", choices=["day", "month"], default="month")
    args = parser.parse_args()

    out = Path(args.out)
    queries = [
        args.domain,
        f"{args.domain}/*",
        f"www.{args.domain}",
        f"www.{args.domain}/*",
        f"http://{args.domain}/*",
        f"https://{args.domain}/*",
        f"http://www.{args.domain}/*",
        f"https://www.{args.domain}/*",
    ]

    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    all_captures: list[Capture] = []
    query_summaries: list[dict[str, object]] = []

    for query in queries:
        rows = fetch_cdx(query, args.limit)
        query_hash = hashlib.sha1(query.encode("utf-8")).hexdigest()[:10]
        write_json(out / "cdx" / f"{run_id}-{query_hash}.json", {"query": query, "rows": rows})
        captures = [normalize_capture(row, query) for row in rows]
        all_captures.extend(captures)
        query_summaries.append(
            {
                "query": query,
                "records": len(rows),
                "classifications": dict(Counter(c.classification for c in captures)),
            }
        )

    unique = dedupe_captures(all_captures)
    captures_dicts = [asdict(capture) for capture in unique]
    classification_counts = Counter(capture.classification for capture in unique)
    mimetype_counts = Counter(capture.mimetype for capture in unique)
    host_counts = Counter(urlparse(capture.original).netloc.lower() for capture in unique)
    month_scores = score_periods(unique, "month")
    day_scores = score_periods(unique, "day")

    manifest = {
        "run_id": run_id,
        "domain": args.domain,
        "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "queries": query_summaries,
        "total_records_before_dedupe": len(all_captures),
        "total_records_after_dedupe": len(unique),
        "classification_counts": dict(classification_counts),
        "mimetype_counts": dict(mimetype_counts),
        "host_counts": dict(host_counts),
        "latest_capture": max((c.timestamp for c in unique), default=None),
        "earliest_capture": min((c.timestamp for c in unique), default=None),
        "top_months": month_scores[:20],
        "top_days": day_scores[:20],
        "captures": captures_dicts,
    }

    write_json(out / "manifests" / f"{run_id}-inventory.json", manifest)
    write_csv(
        out / "manifests" / f"{run_id}-top-months.csv",
        month_scores[:50],
        [
            "period",
            "granularity",
            "score",
            "latest_capture",
            "unique_urls",
            "article_candidates",
            "article_or_index",
            "assets",
            "active_dynamic",
            "non_content",
            "days_from_latest",
        ],
    )
    write_csv(
        out / "manifests" / f"{run_id}-top-days.csv",
        day_scores[:50],
        [
            "period",
            "granularity",
            "score",
            "latest_capture",
            "unique_urls",
            "article_candidates",
            "article_or_index",
            "assets",
            "active_dynamic",
            "non_content",
            "days_from_latest",
        ],
    )

    print(f"Run: {run_id}")
    print(f"Records: {len(all_captures)} before dedupe, {len(unique)} after dedupe")
    print(f"Classifications: {dict(classification_counts)}")
    print("Top month candidates:")
    for row in month_scores[:10]:
        print(
            f"  {row['period']}: score={row['score']} articles={row['article_candidates']} "
            f"article_or_index={row['article_or_index']} assets={row['assets']} "
            f"latest={row['latest_capture']} days_from_latest={row['days_from_latest']}"
        )
    print("Top day candidates:")
    for row in day_scores[:10]:
        print(
            f"  {row['period']}: score={row['score']} articles={row['article_candidates']} "
            f"article_or_index={row['article_or_index']} assets={row['assets']} "
            f"latest={row['latest_capture']} days_from_latest={row['days_from_latest']}"
        )
    print(f"Manifest: {out / 'manifests' / f'{run_id}-inventory.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
