#!/usr/bin/env python3
"""Combine backup manifests, keeping the best status per period+URL."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from wayback_backup import write_json


def record_rank(record: dict[str, Any]) -> tuple[int, int]:
    status = record.get("status")
    if status == "success":
        return (3, int(record.get("byte_length") or 0))
    if status == "dry_run":
        return (1, 0)
    return (2, 0)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("manifests", nargs="+")
    args = parser.parse_args()

    combined: dict[tuple[str, str], dict[str, Any]] = {}
    sources: list[str] = []
    for manifest in args.manifests:
        path = Path(manifest)
        sources.append(str(path))
        data = json.loads(path.read_text(encoding="utf-8"))
        for record in data.get("records", []):
            if record.get("status") == "dry_run":
                continue
            key = (str(record.get("period", "")), str(record.get("original", "")))
            previous = combined.get(key)
            if previous is None or record_rank(record) > record_rank(previous):
                combined[key] = record

    records = sorted(combined.values(), key=lambda row: (str(row.get("period", "")), str(row.get("timestamp", "")), str(row.get("original", ""))))
    summary = {
        "run_id": dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "kind": "combined_backup",
        "sources": sources,
        "selected_count": len(records),
        "status_counts": dict(Counter(str(record.get("status", "")).split(":", 1)[0] for record in records)),
        "classification_counts": dict(Counter(str(record.get("classification", "")) for record in records)),
        "period_counts": dict(Counter(str(record.get("period", "")) for record in records)),
        "records": records,
    }
    write_json(Path(args.out), summary)
    print(f"Combined records: {len(records)}")
    print(f"Statuses: {summary['status_counts']}")
    print(f"Output: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
