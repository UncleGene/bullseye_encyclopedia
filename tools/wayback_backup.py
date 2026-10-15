#!/usr/bin/env python3
"""
Download selected Wayback captures from an inventory manifest.

The downloader preserves raw evidence. It does not decide what becomes
canonical article content.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import mimetypes
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


DEFAULT_PERIODS = ["201009", "201502", "202303", "202501", "202508"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def capture_period(capture: dict[str, Any]) -> str:
    return str(capture["timestamp"])[:6]


def select_captures(
    captures: list[dict[str, Any]],
    periods: set[str],
    classes: set[str] | None,
) -> list[dict[str, Any]]:
    selected: dict[tuple[str, str], dict[str, Any]] = {}
    for capture in captures:
        period = capture_period(capture)
        if period not in periods:
            continue
        if classes is not None and capture.get("classification") not in classes:
            continue
        key = (period, str(capture.get("original", "")))
        previous = selected.get(key)
        if previous is None or str(capture["timestamp"]) > str(previous["timestamp"]):
            selected[key] = capture
    return sorted(selected.values(), key=lambda row: (capture_period(row), row["timestamp"], row["original"]))


def extension_for(original: str, content_type: str | None) -> str:
    path_suffix = Path(urlparse(original).path).suffix
    if path_suffix and re.fullmatch(r"\.[A-Za-z0-9]{1,8}", path_suffix):
        return path_suffix.lower()
    if content_type:
        media_type = content_type.split(";", 1)[0].strip().lower()
        guessed = mimetypes.guess_extension(media_type)
        if guessed:
            if guessed == ".jpe":
                return ".jpg"
            return guessed
    return ".bin"


def local_path(base: Path, run_id: str, capture: dict[str, Any], content_type: str | None = None) -> Path:
    period = capture_period(capture)
    classification = str(capture.get("classification", "unknown"))
    parsed = urlparse(str(capture["original"]))
    host = re.sub(r"[^A-Za-z0-9._-]+", "_", parsed.netloc.lower() or "unknown-host")
    digest = hashlib.sha1(
        f"{capture['timestamp']} {capture['original']}".encode("utf-8")
    ).hexdigest()[:16]
    suffix = extension_for(str(capture["original"]), content_type)
    raw_name = Path(parsed.path).name or "index"
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(raw_name).stem or "index")[:80]
    return base / run_id / period / classification / host / f"{capture['timestamp']}-{stem}-{digest}{suffix}"


def wayback_raw_url(capture: dict[str, Any]) -> str:
    original = quote(str(capture["original"]), safe=":/@!$&'()*+,;=")
    return f"https://web.archive.org/web/{capture['timestamp']}id_/{original}"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def store_bytes(
    data: bytes,
    capture_path: Path,
    blob_root: Path,
) -> tuple[Path, str, int, str]:
    digest = sha256_bytes(data)
    blob_path = blob_root / "sha256" / digest[:2] / digest
    blob_path.parent.mkdir(parents=True, exist_ok=True)
    if not blob_path.exists():
        blob_path.write_bytes(data)
        storage_mode = "blob_created_hardlink"
    else:
        existing_digest = sha256_bytes(blob_path.read_bytes())
        if existing_digest != digest:
            blob_path.write_bytes(data)
            storage_mode = "blob_repaired_hardlink"
        else:
            storage_mode = "blob_reused_hardlink"

    capture_path.parent.mkdir(parents=True, exist_ok=True)
    if capture_path.exists():
        capture_path.unlink()
    try:
        os.link(blob_path, capture_path)
    except OSError:
        capture_path.write_bytes(data)
        storage_mode = storage_mode.replace("hardlink", "copy")
    return blob_path, digest, len(data), storage_mode


def download(url: str, timeout: int, retries: int) -> tuple[str, int | None, str | None, bytes | None]:
    last_error = ""
    for attempt in range(1, retries + 1):
        try:
            request = Request(url, headers={"User-Agent": "bullseye-recovery/0.1"})
            with urlopen(request, timeout=timeout) as response:
                data = response.read()
                content_type = response.headers.get("Content-Type")
                return "success", response.status, content_type, data
        except HTTPError as exc:
            last_error = f"HTTPError {exc.code}: {exc.reason}"
            if 400 <= exc.code < 500:
                return "failed", exc.code, exc.headers.get("Content-Type"), None
        except (URLError, TimeoutError) as exc:
            last_error = repr(exc)
        if attempt < retries:
            time.sleep(1.5 * attempt)
    return f"failed: {last_error}", None, None, None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--period", action="append", dest="periods", default=[])
    parser.add_argument("--class", action="append", dest="classes", default=[])
    parser.add_argument("--out", default="archive/raw/wayback")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--sleep", type=float, default=0.15)
    parser.add_argument("--checkpoint-every", type=int, default=25)
    parser.add_argument("--retry-failed-from")
    parser.add_argument("--skip-success-from", action="append", default=[])
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    inventory = load_json(manifest_path)
    periods = set(args.periods or DEFAULT_PERIODS)
    classes = set(args.classes) if args.classes else None
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = Path(args.out)

    selected = select_captures(inventory["captures"], periods, classes)
    if args.retry_failed_from:
        previous = load_json(Path(args.retry_failed_from))
        failed_keys = {
            (str(record.get("period", "")), str(record.get("original", "")))
            for record in previous.get("records", [])
            if record.get("status") != "success"
        }
        selected = [
            capture
            for capture in selected
            if (capture_period(capture), str(capture.get("original", ""))) in failed_keys
        ]
    if args.skip_success_from:
        success_keys: set[tuple[str, str]] = set()
        for path in args.skip_success_from:
            previous = load_json(Path(path))
            success_keys.update(
                (str(record.get("period", "")), str(record.get("original", "")))
                for record in previous.get("records", [])
                if record.get("status") == "success"
            )
        selected = [
            capture
            for capture in selected
            if (capture_period(capture), str(capture.get("original", ""))) not in success_keys
        ]
    if args.limit is not None:
        selected = selected[: args.limit]

    records: list[dict[str, object]] = []
    files_root = out / "files"
    blob_root = out / "blobs"
    started_at = dt.datetime.now(dt.timezone.utc).isoformat()
    manifest_out = out / "manifests" / f"{run_id}-backup.json"
    csv_out = out / "manifests" / f"{run_id}-backup.csv"

    def summary_payload() -> dict[str, object]:
        status_counts = Counter(str(record["status"]).split(":", 1)[0] for record in records)
        class_counts = Counter(str(record["classification"]) for record in records)
        period_counts = Counter(str(record["period"]) for record in records)
        return {
            "run_id": run_id,
            "inventory_manifest": str(manifest_path),
            "started_at": started_at,
            "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "periods": sorted(periods),
            "classes": sorted(classes) if classes else "all",
            "selected_count": len(selected),
            "status_counts": dict(status_counts),
            "classification_counts": dict(class_counts),
            "period_counts": dict(period_counts),
            "records": records,
        }

    for index, capture in enumerate(selected, start=1):
        retrieval_url = wayback_raw_url(capture)
        expected_path = local_path(files_root, run_id, capture)
        record: dict[str, object] = {
            "index": index,
            "run_id": run_id,
            "period": capture_period(capture),
            "classification": capture.get("classification"),
            "timestamp": capture.get("timestamp"),
            "original": capture.get("original"),
            "source_mimetype": capture.get("mimetype"),
            "source_digest": capture.get("digest"),
            "source_length": capture.get("length"),
            "retrieval_url": retrieval_url,
            "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        }

        if args.dry_run:
            record.update({"status": "dry_run", "local_path": str(expected_path)})
            records.append(record)
            continue

        status, http_status, content_type, data = download(retrieval_url, args.timeout, args.retries)
        record["status"] = status
        record["http_status"] = http_status
        record["content_type"] = content_type

        if status == "success" and data is not None:
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
        if index % 10 == 0 or index == len(selected):
            print(f"{index}/{len(selected)} processed", flush=True)
        if args.checkpoint_every and (index % args.checkpoint_every == 0):
            write_json(manifest_out, summary_payload())
        if args.sleep:
            time.sleep(args.sleep)

    summary = summary_payload()
    status_counts = Counter(str(record["status"]).split(":", 1)[0] for record in records)
    class_counts = Counter(str(record["classification"]) for record in records)
    period_counts = Counter(str(record["period"]) for record in records)
    write_json(manifest_out, summary)
    write_csv(
        csv_out,
        records,
        [
            "index",
            "period",
            "classification",
            "timestamp",
            "original",
            "status",
            "http_status",
            "content_type",
            "byte_length",
            "sha256",
            "blob_path",
            "storage_mode",
            "local_path",
            "retrieval_url",
            "retrieved_at",
        ],
    )

    print(f"Run: {run_id}")
    print(f"Selected: {len(selected)}")
    print(f"Statuses: {dict(status_counts)}")
    print(f"Classes: {dict(class_counts)}")
    print(f"Periods: {dict(period_counts)}")
    print(f"Manifest: {manifest_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
