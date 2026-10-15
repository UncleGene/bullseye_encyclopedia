#!/usr/bin/env python3
"""Migrate manifest local files into the content-addressed blob store."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from wayback_backup import store_bytes, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--blob-root", default="archive/raw/wayback/blobs")
    args = parser.parse_args()

    data = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    migrated = 0
    missing = 0
    already = 0
    for record in data.get("records", []):
        if record.get("status") != "success":
            continue
        local_path_value = record.get("local_path")
        if not local_path_value:
            missing += 1
            continue
        local_path = Path(str(local_path_value))
        if not local_path.exists():
            missing += 1
            continue
        if record.get("blob_path") and Path(str(record["blob_path"])).exists():
            already += 1
            continue
        blob_path, digest, byte_length, storage_mode = store_bytes(
            local_path.read_bytes(),
            local_path,
            Path(args.blob_root),
        )
        record["blob_path"] = str(blob_path)
        record["sha256"] = digest
        record["byte_length"] = byte_length
        record["storage_mode"] = f"migrated_{storage_mode}"
        migrated += 1

    data["blob_migration"] = {
        "source_manifest": args.manifest,
        "migrated": migrated,
        "already_had_blob": already,
        "missing_local_file": missing,
    }
    write_json(Path(args.out), data)
    print(f"Migrated: {migrated}")
    print(f"Already: {already}")
    print(f"Missing: {missing}")
    print(f"Output: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
