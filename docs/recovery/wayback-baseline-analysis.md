# Wayback Baseline Analysis

Run ID: `20260522T135739Z`

Manifest: `archive/raw/wayback/manifests/20260522T135739Z-inventory.json`

## Summary

The Wayback inventory found `96,074` CDX records and deduped them to `15,809` local capture records.

Capture range:

- Earliest: `19990125093846`
- Latest: `20260519170553`

Classification counts:

- Article candidates: `8,013`
- Assets: `6,696`
- Non-content: `947`
- Active/dynamic: `153`

There is no single capture period that is both most recent and most complete. The best recovery strategy is to use a complete older period as the baseline, then overlay newer captures for articles or assets that appear later.

## Recommended Baseline Strategy

### Primary Completeness Baseline: September 2010

Use September 2010 as the first restoration baseline.

Evidence:

- Month: `201009`
- Latest capture in month: `20100929015147`
- Unique URLs: `336`
- Article candidates: `163`
- Assets: `171`
- Top complete day: `20100918`
- Top day article candidates: `141`
- Top day assets: `161`

This is the strongest combined article-plus-asset period in the inventory.

### Article Overlay: February 2015

Use February 2015 to catch article pages that exist later than the 2010 baseline.

Evidence:

- Month: `201502`
- Latest capture in month: `20150226151832`
- Unique URLs: `169`
- Article candidates: `162`
- Assets: `3`

This is nearly as strong as September 2010 for article count, but weak for assets, so it should not be the only restoration source.

### Recent Article Overlay: March 2023

Use March 2023 as the strongest recent article overlay.

Evidence:

- Month: `202303`
- Latest capture in month: `20230329142547`
- Unique URLs: `85`
- Article candidates: `78`
- Assets: `5`

This is the most recent high-article-count period found so far. It is useful for detecting later page versions, but not sufficient for asset recovery.

### Recent Mixed Overlay: January and August 2025

Use January and August 2025 as recent mixed overlays, not as the baseline.

Evidence:

- `202501`: `43` article candidates, `55` assets, `111` unique URLs.
- `202508`: `27` article candidates, `153` assets, `183` unique URLs.

These periods are newer and may help recover recent file variants, but their article coverage is far below the 2010, 2015, and 2023 candidates.

## Most Recent Captures Are Not Complete

The latest captures in 2026 contain only a small number of articles or assets:

- `202604`: `1` article candidate, `5` assets.
- `202603`: `3` article candidates, `1` asset.
- `202602`: `3` article candidates, `27` assets.
- `202601`: `7` article candidates, `35` assets.

These are useful for provenance and late changes, but they should not drive the restoration baseline.

## Top Month Candidates

| Period | Article Candidates | Assets | Unique URLs | Latest Capture |
|---|---:|---:|---:|---|
| `201009` | 163 | 171 | 336 | `20100929015147` |
| `201502` | 162 | 3 | 169 | `20150226151832` |
| `200611` | 148 | 13 | 163 | `20061128071130` |
| `201011` | 130 | 149 | 280 | `20101130162430` |
| `201110` | 130 | 59 | 192 | `20111030004736` |
| `200706` | 128 | 47 | 175 | `20070630141212` |
| `201201` | 124 | 13 | 142 | `20120129154007` |
| `201205` | 114 | 172 | 291 | `20120531183347` |
| `200606` | 113 | 148 | 262 | `20060627025241` |
| `200805` | 118 | 2 | 122 | `20080520115138` |

## Pareto-Relevant Recent/Complete Months

These months are not dominated by another month that is both newer and at least as complete by article and asset counts:

| Period | Article Candidates | Assets | Unique URLs | Latest Capture |
|---|---:|---:|---:|---|
| `202604` | 1 | 5 | 6 | `20260415080836` |
| `202603` | 3 | 1 | 4 | `20260322022126` |
| `202602` | 3 | 27 | 30 | `20260223071442` |
| `202601` | 7 | 35 | 42 | `20260126062136` |
| `202508` | 27 | 153 | 183 | `20250829020021` |
| `202501` | 43 | 55 | 111 | `20250131145717` |
| `202303` | 78 | 5 | 85 | `20230329142547` |
| `202012` | 37 | 204 | 242 | `20201223092237` |
| `201908` | 30 | 264 | 294 | `20190831223147` |
| `201907` | 51 | 109 | 160 | `20190731022849` |
| `201601` | 104 | 115 | 225 | `20160131200021` |
| `201502` | 162 | 3 | 169 | `20150226151832` |
| `201205` | 114 | 172 | 291 | `20120531183347` |
| `201009` | 163 | 171 | 336 | `20100929015147` |

## Next Backup Targets

1. Download raw captures for all September 2010 article candidates and assets.
2. Download February 2015 article candidates and compare against September 2010 by canonical URL and digest.
3. Download March 2023 article candidates to identify newer or changed article bodies.
4. Download January and August 2025 captures for late variants and asset recovery.
5. Preserve 2026 captures as low-coverage recent evidence, but do not use them as the baseline.

