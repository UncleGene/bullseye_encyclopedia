#!/usr/bin/env python3
"""
Recover images referenced by downloaded article HTML.

This pass reads a raw backup manifest, extracts image references from
successful article HTML files, resolves them against the original article URL,
finds the closest matching Wayback capture in the full inventory, downloads it,
and records unresolved image references explicitly.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import time
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urldefrag, urljoin, urlparse

from wayback_backup import download, local_path, store_bytes, wayback_raw_url, write_csv, write_json


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".ico"}


class ImageReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {name.lower(): value or "" for name, value in attrs}
        for attr in ("src", "data-src", "data-original"):
            value = attr_map.get(attr)
            if value:
                self.refs.append(html.unescape(value.strip()))
        for attr in ("srcset", "data-srcset"):
            value = attr_map.get(attr)
            if value:
                self.refs.extend(parse_srcset(value))


def parse_srcset(value: str) -> list[str]:
    refs: list[str] = []
    for part in value.split(","):
        candidate = part.strip().split()
        if candidate:
            refs.append(html.unescape(candidate[0]))
    return refs


def extract_css_urls(text: str) -> list[str]:
    refs: list[str] = []
    for match in re.finditer(r"url\(([^)]+)\)", text, flags=re.IGNORECASE):
        value = match.group(1).strip().strip("'\"")
        if value:
            refs.append(html.unescape(value))
    return refs


def image_refs_from_file(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    parser = ImageReferenceParser()
    parser.feed(text)
    refs = parser.refs + extract_css_urls(text)
    return [ref for ref in refs if is_candidate_ref(ref)]


def is_candidate_ref(ref: str) -> bool:
    lowered = ref.strip().lower()
    if not lowered or lowered.startswith(("data:", "mailto:", "javascript:", "#")):
        return False
    parsed = urlparse(lowered)
    suffix = Path(parsed.path).suffix
    return suffix in IMAGE_EXTENSIONS or not suffix


def normalize_url_key(url: str) -> str:
    parsed = urlparse(url)
    scheme = "http"
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    if host.endswith(":80"):
        host = host[:-3]
    path = parsed.path or "/"
    return f"{scheme}://{host}{path}"


def resolve_ref(base_url: str, ref: str) -> str:
    resolved, _fragment = urldefrag(urljoin(base_url, ref.strip()))
    return resolved


def build_inventory_index(captures: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for capture in captures:
        original = str(capture.get("original", ""))
        if not original:
            continue
        mimetype = str(capture.get("mimetype", "")).lower()
        suffix = Path(urlparse(original).path.lower()).suffix
        if capture.get("classification") != "asset" and not mimetype.startswith("image/") and suffix not in IMAGE_EXTENSIONS:
            continue
        index[normalize_url_key(original)].append(capture)
    for rows in index.values():
        rows.sort(key=lambda row: str(row.get("timestamp", "")))
    return index


def choose_capture(
    rows: list[dict[str, Any]],
    article_timestamp: str,
    article_period: str,
) -> dict[str, Any]:
    def score(row: dict[str, Any]) -> tuple[int, int, int]:
        timestamp = str(row.get("timestamp", ""))
        same_period = 1 if timestamp.startswith(article_period) else 0
        not_after = 1 if timestamp <= article_timestamp else 0
        distance = abs(int(timestamp[:14]) - int(article_timestamp[:14])) if timestamp and article_timestamp else 10**14
        return same_period, not_after, -distance

    return max(rows, key=score)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", required=True)
    parser.add_argument("--backup", required=True)
    parser.add_argument("--out", default="archive/raw/wayback")
    parser.add_argument("--timeout", type=int, default=12)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--sleep", type=float, default=0.05)
    parser.add_argument("--retry-failed-from")
    parser.add_argument("--skip-success-from", action="append", default=[])
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    inventory = json.loads(Path(args.inventory).read_text(encoding="utf-8"))
    backup = json.loads(Path(args.backup).read_text(encoding="utf-8"))
    image_index = build_inventory_index(inventory["captures"])
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    files_root = Path(args.out) / "files"
    blob_root = Path(args.out) / "blobs"

    article_records = [
        record
        for record in backup["records"]
        if record.get("status") == "success"
        and record.get("classification") == "article_candidate"
        and record.get("local_path")
    ]

    image_jobs: dict[tuple[str, str, str], dict[str, Any]] = {}
    unresolved: list[dict[str, Any]] = []
    refs_scanned = 0

    for article in article_records:
        article_path = Path(str(article["local_path"]))
        refs = image_refs_from_file(article_path)
        refs_scanned += len(refs)
        for ref in refs:
            resolved = resolve_ref(str(article["original"]), ref)
            key = normalize_url_key(resolved)
            candidates = image_index.get(key, [])
            if not candidates:
                unresolved.append(
                    {
                        "status": "unresolved",
                        "article_original": article["original"],
                        "article_timestamp": article["timestamp"],
                        "image_ref": ref,
                        "resolved_url": resolved,
                        "reason": "no_matching_capture_in_inventory",
                    }
                )
                continue
            chosen = choose_capture(candidates, str(article["timestamp"]), str(article["period"]))
            job_key = (str(chosen["timestamp"]), str(chosen["original"]), str(article["original"]))
            image_jobs[job_key] = {
                "capture": chosen,
                "article_original": article["original"],
                "article_timestamp": article["timestamp"],
                "image_ref": ref,
                "resolved_url": resolved,
            }

    jobs = list(image_jobs.values())
    if args.retry_failed_from:
        previous = json.loads(Path(args.retry_failed_from).read_text(encoding="utf-8"))
        failed = {
            (str(record.get("original", "")), str(record.get("article_original", "")))
            for record in previous.get("records", [])
            if str(record.get("status", "")).startswith("failed")
        }
        jobs = [
            job
            for job in jobs
            if (str(job["capture"].get("original", "")), str(job["article_original"])) in failed
        ]
    if args.skip_success_from:
        successes: set[tuple[str, str]] = set()
        for manifest in args.skip_success_from:
            previous = json.loads(Path(manifest).read_text(encoding="utf-8"))
            successes.update(
                (str(record.get("original", "")), str(record.get("article_original", "")))
                for record in previous.get("records", [])
                if record.get("status") == "success"
            )
        jobs = [
            job
            for job in jobs
            if (str(job["capture"].get("original", "")), str(job["article_original"])) not in successes
        ]
    if args.limit is not None:
        jobs = jobs[: args.limit]

    records: list[dict[str, Any]] = []
    for index, job in enumerate(jobs, start=1):
        capture = dict(job["capture"])
        retrieval_url = wayback_raw_url(capture)
        status, http_status, content_type, data = download(retrieval_url, args.timeout, args.retries)
        record = {
            "index": index,
            "run_id": run_id,
            "status": status,
            "http_status": http_status,
            "content_type": content_type,
            "timestamp": capture.get("timestamp"),
            "original": capture.get("original"),
            "source_mimetype": capture.get("mimetype"),
            "source_digest": capture.get("digest"),
            "source_length": capture.get("length"),
            "retrieval_url": retrieval_url,
            "article_original": job["article_original"],
            "article_timestamp": job["article_timestamp"],
            "image_ref": job["image_ref"],
            "resolved_url": job["resolved_url"],
            "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        }
        if status == "success" and data is not None:
            path_capture = dict(capture)
            path_capture["classification"] = "referenced_image"
            path = local_path(files_root, run_id, path_capture, content_type)
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
        if index % 10 == 0 or index == len(jobs):
            print(f"{index}/{len(jobs)} image captures processed", flush=True)
        if args.sleep:
            time.sleep(args.sleep)

    all_records = records + unresolved
    summary = {
        "run_id": run_id,
        "inventory_manifest": args.inventory,
        "backup_manifest": args.backup,
        "article_records_scanned": len(article_records),
        "image_refs_scanned": refs_scanned,
        "image_jobs_selected": len(jobs),
        "status_counts": dict(Counter(str(record["status"]).split(":", 1)[0] for record in all_records)),
        "records": all_records,
    }

    manifest_out = Path(args.out) / "manifests" / f"{run_id}-image-recovery.json"
    csv_out = Path(args.out) / "manifests" / f"{run_id}-image-recovery.csv"
    write_json(manifest_out, summary)
    write_csv(
        csv_out,
        all_records,
        [
            "index",
            "status",
            "http_status",
            "content_type",
            "timestamp",
            "original",
            "article_original",
            "article_timestamp",
            "image_ref",
            "resolved_url",
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
    print(f"Articles scanned: {len(article_records)}")
    print(f"Image refs scanned: {refs_scanned}")
    print(f"Image jobs selected: {len(jobs)}")
    print(f"Statuses: {summary['status_counts']}")
    print(f"Manifest: {manifest_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
