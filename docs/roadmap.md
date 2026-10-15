# Roadmap

## M0: Planning Bootstrap

Status: complete

Triggered by: user request on 2026-05-22.

Done criteria:

- Project goals recorded.
- Requirements recorded.
- Recovery spec recorded.
- Roadmap recorded.
- Output-neutral directory structure created.

## M1: Wayback Inventory

Status: complete

Purpose: Discover the recoverable surface area before downloading or normalizing content.

Scope:

- Query apex, `www`, HTTP, HTTPS, and discovered subdomain variants.
- Store raw inventory responses.
- Generate a URL manifest and summary report.
- Classify URLs as article, asset, index/navigation, active/dynamic, duplicate, or non-content.
- Identify candidate "best" snapshots without discarding alternates.

Done criteria:

- `archive/raw/wayback/cdx` contains raw inventory outputs.
- A manifest records unique URLs, status codes, MIME types, timestamps, and digests.
- Article candidate URLs are separated from site chrome, index pages, assets, and active/dynamic content.
- The report identifies gaps, redirects, duplicate pages, and candidate restoration eras.
- The process can be rerun without corrupting prior inventory.

Validation:

- Compare inventory counts by host and MIME type.
- Spot-check representative Wayback URLs in a browser.
- Confirm failures are recorded, not ignored.

## M2: Raw Backup

Status: complete for selected baseline/overlay periods

Purpose: Preserve all recoverable pages and assets locally.

Scope:

- Download raw HTML, CSS, JavaScript, images, PDFs, and other files from selected captures.
- Follow referenced assets and query alternate timestamps for missing assets.
- Store checksums and retrieval metadata.
- Preserve full raw pages as evidence even when canonical extraction later omits chrome.
- Use staggered, checkpointed retries; completeness is preferred to speed.
- Store duplicate bytes only once through content-addressed blobs and per-capture references or hardlinks.
- Extract and recover article image references from downloaded article HTML.
- Detect the prior site engine/platform from recovered evidence.
- Produce completeness and missing-asset reports.

Done criteria:

- Every attempted URL has a manifest entry.
- Every successful file has a checksum.
- Identical bytes across dumps are deduplicated in storage.
- Article image recovery has a manifest of saved and unresolved images.
- Site-engine analysis report exists.
- Missing or partial assets are listed with reason and next action.
- Re-running the backup skips unchanged files and reports diffs.

Completion evidence:

- Combined raw backup manifest: `archive/raw/wayback/manifests/20260522T-combined-backup-blobs.json`
- Combined image recovery manifest: `archive/raw/wayback/manifests/20260522T-combined-image-recovery.json`
- Backup report: `docs/recovery/backup-report.md`
- Selected raw captures: `884` successful, `0` failed.
- Article images: `809` unique recovered records, `0` failed downloads, `7` unresolved external counter references.

Validation:

- Check manifest entries against files on disk.
- Verify MIME type and extension mismatches.
- Open sampled pages locally from raw capture files.
- Verify duplicate SHA-256 blobs are not stored multiple times.
- Verify sampled article images resolve to local recovered files or explicit unresolved records.

## M3: Canonical Normalization

Status: complete for first pass

Purpose: Convert raw capture material into reusable article source content.

Scope:

- Extract article title, byline/date when available, body, useful context, media references, links, and metadata.
- Remove recurring site chrome from canonical article bodies.
- Assign stable canonical IDs.
- Normalize internal links and asset references.
- Flag conflicting snapshots and duplicate pages for review.

Done criteria:

- Canonical article and asset records exist under `content/canonical` and `content/assets`.
- Each canonical record traces to raw capture provenance.
- Each article distinguishes body content from context and omitted chrome.
- Link and media catalogs can be generated.
- Conflicts and manual review needs are reported.

Completion evidence:

- Normalization report: `docs/recovery/normalization-report.md`
- Canonical article index: `content/canonical/articles.index.json`
- Page shell index: `content/canonical/page-shells.index.json`
- Asset index: `content/assets/assets.index.json`
- First pass produced `150` canonical articles, `27` page shells, and `165` article asset records.

Validation:

- Sample canonical records against raw HTML.
- Confirm sampled article bodies do not include repeated headers, footers, sidebars, provider wrappers, or unrelated navigation.
- Confirm every canonical asset points to a local file or explicit missing marker.
- Confirm duplicate URL variants converge without duplicate pages.

## M4: Export Contracts

Status: complete for current release-facing policy

Purpose: Define how canonical content feeds ebook, static site, and DB outputs.

Scope:

- Define ebook ordering and metadata.
- Define `as-is` static site route, dependency rewrite, navigation, local asset, and redirect strategy.
- Define `as-is` static layout so articles are grouped by canonical top-page groups, linked subarticles live under their parent article group, article images live with their grouped article, and site-wide images live in a shared images folder.
- Define `raw` article static site route, navigation, local asset, missing-artifact section, and redirect strategy.
- Define DB import schema or seed contract.

Done criteria:

- Export contracts are documented.
- Each contract maps from canonical records without requiring hand-edited generated output.
- Static HTML contract defines a deployable, self-contained, navigable copy of the website.
- Static HTML contract distinguishes `as-is` reproduction from the normalized `raw` article site.
- The `raw` article site contract defines a `Missing Artifacts` section and requires unavailable internal-resource links to target it.
- The EPUB contract excludes non-reader-safe supplemental resources from the package.
- Known limitations are recorded.

Validation:

- Dry-run export on a small sample.
- Confirm generated output can be deleted and rebuilt.

Completion evidence so far:

- Ebook export contract: `docs/recovery/ebook-export-contract.md`
- Ebook export report: `docs/recovery/ebook-export-report.md`
- As-is static site report: `docs/recovery/raw-static-site-report.md`
- As-is static validation report: `exports/static-site/as-is/_validation-report.json`
- Raw article site report: `docs/recovery/canonical-static-site-report.md`
- Raw article site validation report: `exports/static-site/raw/_validation-report.json`
- Canonical navigation refinement report: `docs/recovery/canonical-navigation-refinement.md`
- Shared output audit report: `docs/recovery/output-audit-report.md`
- Shared output audit machine report: `exports/output-audit/_output-audit-report.json`

## M5: Presentation Implementations

Status: in progress; release-facing export policy implemented and external EPUB validation passed; remaining work requires explicit scope selection

Purpose: Build actual generated outputs after preservation and canonical normalization are stable.

Scope:

- Ebook generation with only EPUB-reader-safe packaged resources.
- As-is static HTML generation as a deployable navigable copy of the recovered website.
- Raw article static HTML generation as a deployable navigable article site with a `Missing Artifacts` section.
- DB-backed content import.

Done criteria:

- Each output builds from canonical content.
- Static site can be opened locally and deployed as-is to any static host.
- Static site has working internal navigation and local recovered image references.
- The `raw` article site routes unavailable internal-resource links to `Missing Artifacts`.
- The `as-is`, EPUB, and PDF outputs avoid reader-facing missing-resource notes where practical.
- Visual or structural QA is documented for each target.
- Release notes describe missing historical content and substitutions.

Completion evidence so far:

- Current as-is static output: `exports/static-site/as-is/index.html`
- Current raw article static output: `exports/static-site/raw/index.html`
- Ebook output: `exports/ebook/bullseye-pistol.epub`
- Final single-file release bundle: `exports/final/`
- Raw as-is output contains canonical-grouped article folders, `10` top-level sections, `2` detected sub-article groups, `161` article-specific image files, `295` shared image files, `0` broken local references, and `0` bad page-local scripts across `295` checked files.
- Canonical output contains `150` article pages, `165` recovered article assets, `21` additional recovered linked resources, and `0` broken local references after validation.
- Current ebook output contains `150` article chapters, `160` embedded recovered image assets, and `0` non-reader-safe packaged resources; `59` internal non-article resource links are suppressed from reader-facing output.
- The 2026-05-29 shared output audit records `0` blocking findings, `3` improvement candidates, and `1` deferred release risk. That EPUB validation risk was closed on 2026-10-15: EPUBCheck 5.4.0 passed with `0` errors and warnings; see `docs/recovery/ebook-export-report.md`.
- Enhanced browsing is already implemented in the raw article site while preserving recovered homepage navigation.
- PDF release QA on 2026-10-15 confirms `574` pages, all `150` article destinations, and `838` working local link annotations. Sampled visual review and missing-resource policy checks passed without PDF changes; evidence, limitations, and PDF release notes are in `docs/recovery/pdf-export-report.md`.
- GitHub Pages workflow prepared on 2026-10-15: normalized `raw` at root, historical `as-is` under `/as-is/`. Local staging validates with `351` HTML files and `0` broken local references. Repository Pages activation and live deployment verification remain outstanding; see `docs/recovery/github-pages.md`.

## M6: Release-Facing Artifact Alignment

Status: complete

Purpose: Align generated artifacts with the user-approved release policy.

Scope:

- Rename the clean article static export from `canonical` to `raw`.
- Rename the historical full-page reproduction from `raw-as-is` to `as-is`.
- Add a `Missing Artifacts` section to the `raw` article site.
- Rewrite unavailable internal-resource links in the `raw` article site to the matching `Missing Artifacts` entry.
- Remove standalone missing-resource pages/prose from `as-is`, EPUB, and PDF where practical while preserving machine-report evidence.
- Rebuild EPUB without PDF, MP3, ZIP, arbitrary HTML, EXE, or other non-reader-safe supplemental resources.
- Refresh output audit reports and documentation with current counts.

Done criteria:

- `exports/static-site/raw/index.html` exists and validates with `150` article pages, `0` broken local references, and a `Missing Artifacts` section.
- `exports/static-site/as-is/index.html` exists and validates with `0` broken local references.
- The EPUB OPF manifest contains only EPUB-reader-safe media types.
- Generated reports record excluded or unavailable resources without surfacing missing-resource pages in non-raw reader outputs.
- Project docs no longer claim stale counts or old output names as current release targets.
