#!/usr/bin/env python3
"""Combine image recovery manifests, preferring successful downloads."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from wayback_backup import write_json


def rank(record: dict[str, Any]) -> tuple[int, int]:
    status = str(record.get("status", ""))
    if status == "success":
        return (3, int(record.get("byte_length") or 0))
    if status == "unresolved":
        return (1, 0)
    return (2, 0)


def key(record: dict[str, Any]) -> tuple[str, str, str]:
    if record.get("status") == "unresolved":
        return (
            "unresolved",
            str(record.get("article_original", "")),
            str(record.get("resolved_url", "")),
        )
    return (
        "capture",
        str(record.get("article_original", "")),
        str(record.get("original", "")),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("manifests", nargs="+")
    args = parser.parse_args()

    combined: dict[tuple[str, str, str], dict[str, Any]] = {}
    sources = []
    for manifest in args.manifests:
        sources.append(manifest)
        data = json.loads(Path(manifest).read_text(encoding="utf-8"))
        for record in data.get("records", []):
            record_key = key(record)
            previous = combined.get(record_key)
            if previous is None or rank(record) > rank(previous):
                combined[record_key] = record

    records = sorted(
        combined.values(),
        key=lambda row: (str(row.get("status", "")), str(row.get("article_original", "")), str(row.get("original", ""))),
    )
    summary = {
        "run_id": dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "kind": "combined_image_recovery",
        "sources": sources,
        "status_counts": dict(Counter(str(record.get("status", "")).split(":", 1)[0] for record in records)),
        "records": records,
    }
    write_json(Path(args.out), summary)
    print(f"Combined records: {len(records)}")
    print(f"Statuses: {summary['status_counts']}")
    print(f"Output: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
