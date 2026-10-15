# Backup Report

Date: 2026-05-22

## Inventory

- Inventory manifest: `archive/raw/wayback/manifests/20260522T135739Z-inventory.json`
- CDX records retrieved: `96,074`
- Deduped captures inventoried: `15,809`
- Selected baseline/overlay periods: `201009`, `201502`, `202303`, `202501`, `202508`

## Raw Backup

- Combined raw backup manifest: `archive/raw/wayback/manifests/20260522T-combined-backup-blobs.json`
- Selected captures: `884`
- Successful captures: `884`
- Failed captures: `0`

Successful capture classes:

- Article candidates: `473`
- Assets: `387`
- Active/dynamic evidence: `20`
- Non-content evidence: `4`

## Article Image Recovery

- Combined image recovery manifest: `archive/raw/wayback/manifests/20260522T-combined-image-recovery.json`
- Articles scanned: `471`
- Image references scanned: `1,044`
- Unique recovered article-image records: `809`
- Failed image downloads: `0`
- Unresolved references: `7`

All unresolved references are external counter URLs:

- `http://counter.digits.com/wc/-d/4/bullseyepistol`

These had no matching capture in the inventory and are not article images needed for restored reading.

## Deduplicated Storage

- Successful file references across raw backup and image recovery: `1,693`
- Unique SHA-256 blobs referenced: `536`
- Duplicate file references deduplicated through shared blobs: `1,157`
- Missing blob references: `0`

Storage contract:

- Blob store: `archive/raw/wayback/blobs/sha256`
- Capture paths: `archive/raw/wayback/files`
- Manifests record `sha256`, `blob_path`, `local_path`, and `storage_mode`.

## Site Engine

- Report: `docs/recovery/site-engine-analysis.md`
- HTML files scanned: `493`
- Likely engine: static HTML authored with Microsoft FrontPage/WordPad.
- Evidence includes `.htm` file structure, `Microsoft FrontPage Express 2.0` generator tags, `Microsoft Wordpad (by Hand)` generator tags, and absence of local CMS path markers.

## Remaining Work

1. Normalize recovered article HTML into canonical article records without site chrome.
2. Build the deployable navigable static-site export from canonical articles and recovered local assets.
3. Build ebook and DB import/export contracts after the canonical article model is validated.

