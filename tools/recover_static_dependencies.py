#!/usr/bin/env python3
"""Recover internal dependencies reported missing by the raw static-site export."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.parse import urlparse

from wayback_backup import download, local_path, store_bytes, wayback_raw_url, write_csv, write_json


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    if host.endswith(":80"):
        host = host[:-3]
    path = parsed.path or "/"
    if path.lower().endswith(".html"):
        path = path[:-5] + ".htm"
    return f"http://{host}{path}"


def internal_url(url: str, domain: str) -> bool:
    host = urlparse(url).netloc.lower()
    if host.endswith(":80"):
        host = host[:-3]
    return host == domain or host.endswith(f".{domain}") or host == f"www.{domain}"


def build_inventory_index(captures: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for capture in captures:
        original = str(capture.get("original", ""))
        if not original:
            continue
        index[normalize_url(original)].append(capture)
    for rows in index.values():
        rows.sort(key=lambda row: str(row.get("timestamp", "")))
    return index


def choose_latest(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return max(rows, key=lambda row: str(row.get("timestamp", "")))


def fetch_cdx(url: str) -> list[dict[str, Any]]:
    query = "https://web.archive.org/cdx?" + urlencode(
        {
            "url": url,
            "output": "json",
            "fl": "urlkey,timestamp,original,mimetype,statuscode,digest,length",
            "filter": "statuscode:200",
        }
    )
    request = Request(query, headers={"User-Agent": "bullseye-recovery/0.1"})
    with urlopen(request, timeout=30) as response:
        rows = json.loads(response.read().decode("utf-8"))
    if not rows:
        return []
    header = rows[0]
    return [dict(zip(header, row)) for row in rows[1:]]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--domain", default="bullseyepistol.com")
    parser.add_argument("--out", default="archive/raw/wayback")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--sleep", type=float, default=1.5)
    args = parser.parse_args()

    inventory = json.loads(Path(args.inventory).read_text(encoding="utf-8"))
    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    index = build_inventory_index(inventory["captures"])
    missing_urls = sorted(
        {
            url
            for urls in report.get("missing_rewrites", {}).values()
            for url in urls
            if internal_url(url, args.domain)
        }
    )
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    files_root = Path(args.out) / "files"
    blob_root = Path(args.out) / "blobs"
    records: list[dict[str, Any]] = []

    for idx, url in enumerate(missing_urls, start=1):
        candidates = index.get(normalize_url(url), [])
        if not candidates:
            try:
                candidates = fetch_cdx(url)
                for candidate in candidates:
                    candidate["classification"] = "fallback_cdx"
            except Exception as exc:
                records.append(
                    {
                        "index": idx,
                        "run_id": run_id,
                        "status": "unresolved",
                        "original": url,
                        "resolved_url": url,
                        "reason": f"fallback_cdx_failed: {exc!r}",
                    }
                )
                continue
            if not candidates:
                records.append(
                    {
                        "index": idx,
                        "run_id": run_id,
                        "status": "unresolved",
                        "original": url,
                        "resolved_url": url,
                        "reason": "no_matching_successful_capture_in_inventory_or_cdx",
                    }
                )
                continue
        capture = dict(choose_latest(candidates))
        retrieval_url = wayback_raw_url(capture)
        status, http_status, content_type, data = download(retrieval_url, args.timeout, args.retries)
        record: dict[str, Any] = {
            "index": idx,
            "run_id": run_id,
            "status": status,
            "http_status": http_status,
            "content_type": content_type,
            "timestamp": capture.get("timestamp"),
            "original": capture.get("original"),
            "requested_url": url,
            "source_mimetype": capture.get("mimetype"),
            "source_digest": capture.get("digest"),
            "source_length": capture.get("length"),
            "classification": capture.get("classification"),
            "retrieval_url": retrieval_url,
            "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        }
        if status == "success" and data is not None:
            capture["classification"] = f"static_dependency_{capture.get('classification', 'unknown')}"
            path = local_path(files_root, run_id, capture, content_type)
            blob_path, digest, byte_length, storage_mode = store_bytes(data, path, blob_root)
            record["local_path"] = str(path)
            record["blob_path"] = str(blob_path)
            record["sha256"] = digest
            record["byte_length"] = byte_length
            record["storage_mode"] = storage_mode
        else:
            record["local_path"] = None
            record["blob_path"] = None
            record["sha256"] = None
            record["byte_length"] = 0
            record["storage_mode"] = None
        records.append(record)
        if idx % 10 == 0 or idx == len(missing_urls):
            print(f"{idx}/{len(missing_urls)} dependencies processed", flush=True)
        if args.sleep:
            time.sleep(args.sleep)

    summary = {
        "run_id": run_id,
        "inventory_manifest": args.inventory,
        "static_site_report": args.report,
        "requested_count": len(missing_urls),
        "status_counts": dict(Counter(str(record.get("status", "")).split(":", 1)[0] for record in records)),
        "records": records,
    }
    manifest_out = Path(args.out) / "manifests" / f"{run_id}-static-dependencies.json"
    csv_out = Path(args.out) / "manifests" / f"{run_id}-static-dependencies.csv"
    write_json(manifest_out, summary)
    write_csv(
        csv_out,
        records,
        [
            "index",
            "status",
            "http_status",
            "content_type",
            "timestamp",
            "original",
            "requested_url",
            "classification",
            "byte_length",
            "sha256",
            "blob_path",
            "storage_mode",
            "local_path",
            "retrieval_url",
            "retrieved_at",
            "reason",
        ],
    )
    print(f"Run: {run_id}")
    print(f"Requested: {len(missing_urls)}")
    print(f"Statuses: {summary['status_counts']}")
    print(f"Manifest: {manifest_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
