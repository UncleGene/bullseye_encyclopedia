# Requirements

## R1: Wayback Inventory

Status: complete for first recovery pass

Type: data-integrity

Priority: high

Pain or value: The site is down, and unknown pages may be lost unless recoverable URLs are discovered quickly.

Functional behavior:

- Query Wayback for `bullseyepistol.com`, `www.bullseyepistol.com`, HTTP, HTTPS, and discovered subdomains.
- Capture successful, redirected, failed, duplicate, and non-HTML records.
- Preserve the original URL, Wayback timestamp, status code, MIME type, digest, and source host.
- Classify discovered URLs as article, asset, index/navigation, active/dynamic, duplicate, or non-content when evidence supports it.
- Collapse duplicates only after the raw inventory has been saved.

Scenarios:

- Given Wayback has archived pages, when discovery runs, then the URL inventory includes every recoverable URL variant returned by CDX or wildcard search.
- Given a URL has multiple captures, when discovery runs, then all candidate timestamps are retained before a best snapshot is selected.
- Given a URL returns only errors, when discovery runs, then the failures are logged as recovery evidence.

Acceptance criteria:

- Inventory files exist under `archive/raw/wayback/cdx`.
- A manifest lists counts by host, status, MIME type, and timestamp range.
- A content classification summary lists article candidates separately from site chrome, index pages, assets, and active/dynamic URLs.
- Re-running discovery produces stable records or explicit diffs.

## R2: Raw Capture Backup

Status: complete for selected baseline/overlay periods

Type: data-integrity

Priority: high

Pain or value: The fastest path to safety is preserving raw recovered files before cleanup.

Functional behavior:

- Download raw archived files using retrieval URLs that avoid Wayback viewer injection where possible.
- Store files under a timestamped raw snapshot tree.
- Record retrieval time, source URL, archive URL, checksum, byte length, content type, and HTTP result.
- Rate-limit requests, stagger retries, checkpoint progress, and resume partial runs safely.
- Store downloaded bytes in a content-addressed blob store and reference or hardlink captures to those blobs to avoid duplicate storage across dumps.
- Prefer completeness over speed when Wayback throttles, refuses connections, or times out.

Scenarios:

- Given a URL has a selected successful capture, when backup runs, then the raw file is stored and linked from the manifest.
- Given an asset is referenced by HTML but missing from that timestamp, when backup runs, then alternate timestamps are searched and the missing status is recorded.
- Given a file was already downloaded unchanged, when backup reruns, then it is not duplicated.

Acceptance criteria:

- Every downloaded file has a manifest entry and checksum.
- Identical downloaded bytes are stored once in the blob store even when referenced by multiple periods or retry runs.
- Missing assets have explicit records under the same manifest.
- A recovery report separates complete, partial, missing, and unresolved items.

## R2A: Article Image Recovery

Status: complete for selected backup

Type: data-integrity

Priority: high

Pain or value: Articles are incomplete if their embedded images are not recoverable.

Functional behavior:

- Extract image references from recovered article HTML, including `img`, `srcset`, lazy-load attributes, and CSS `url(...)` references.
- Resolve relative image references against the original article URL.
- Locate matching Wayback captures across the full inventory, not only the selected article baseline period.
- Download recoverable images into the deduplicated blob store.
- Record unresolved image references with article URL, article timestamp, original reference, resolved URL, and reason.

Acceptance criteria:

- Image recovery manifest lists scanned articles, image references, successful image downloads, deduplicated blob paths, and unresolved references.
- Every recovered image has checksum, content type, source capture, and parent article provenance.
- Article-image recovery can be rerun without duplicating bytes.

## R3: Canonical Content Normalization

Status: complete for first normalization pass

Type: core

Priority: high

Pain or value: The site is primarily a collection of articles, and raw HTML includes layout chrome that should not become article content.

Functional behavior:

- Extract each article into canonical content records with stable IDs, original URL, title, author/date if available, body blocks, media references, links, and provenance.
- Remove recurring site chrome from canonical article bodies, including provider wrappers, global headers, footers, repeated sidebars, ads, sharing widgets, and unrelated navigation.
- Preserve useful article context separately when it affects ordering, taxonomy, breadcrumbs, article series, or internal links.
- Normalize internal links and asset references.
- Preserve original HTML as evidence while allowing edited canonical markdown or structured records later.
- Flag conflicts where different snapshots contain meaningfully different content.

Acceptance criteria:

- Canonical records exist under `content/canonical`.
- Each record references at least one raw capture.
- Each article record distinguishes `body` from extracted `context` and omitted `chrome`.
- Link and media catalogs can be generated from canonical records.

## R4: Multi-Target Export Contracts

Status: evolving; first-pass exports exist, but release-facing naming and missing-artifact policy must be updated

Type: export

Priority: high

Pain or value: The same restored articles need to serve multiple presentation forms without three separate content sources.

Functional behavior:

- Define export contracts for ebook, static HTML, and DB seed/import output.
- Static HTML export must produce a self-contained navigable website that can be deployed as-is on any static host.
- Static HTML export must use recovered local assets and internal links, not Wayback-hosted dependencies.
- Static HTML export must include usable navigation for the article collection even when original site chrome is not reused as canonical article content.
- Static HTML exports must include two tracks: an `as-is` site reproduction from recovered pages and a `raw` article site generated from normalized canonical articles.
- The `as-is` static export must use a non-flat deployable structure: article pages grouped by canonical top-page groups, subarticles grouped under their parent article where canonical article links prove that relationship, article-specific images stored with the corresponding grouped article, and site-wide images stored under a shared images folder.
- The `raw` article site navigation must preserve recovered original homepage sections where possible and may add provenance-backed enhanced browse groups when that improves article discovery.
- Both static variants must provide visible links to the other published version. The historical homepage must include a prominent **Read the Clean Edition** entry below its banner, explaining that it offers the same recovered articles in a simpler reading layout; the link should fit the recovered green-and-cream style. The `raw` header must use the recovered encyclopedia banner with capture provenance retained.
- The `raw` article site must include a dedicated `Missing Artifacts` section for unavailable internal resources that may be found later.
- Links in the `raw` article site that target unavailable internal resources must point to the relevant `Missing Artifacts` entry.
- The `as-is` site, EPUB, and PDF should avoid reader-facing missing-resource pages or missing-resource prose where practical; omissions must still be recorded in machine reports.
- EPUB output must package only EPUB-reader-safe resources: XHTML, CSS, JPEG, PNG, GIF, SVG, and required EPUB metadata/container files. PDF, MP3, ZIP, EXE, arbitrary HTML, and other non-reader-safe recovered resources must not be embedded in the EPUB.
- Keep generated output under `exports`.
- Publish the website variants online without distributing website ZIPs. Keep the generated site directories for reproducible Pages deployment; downloadable final editions are EPUB and PDF.
- Do not hand-edit generated outputs as the source of truth.

Acceptance criteria:

- Ebook, static site, and DB export schemas are documented before implementation.
- Export outputs can be regenerated from canonical content.
- Static site output can be opened locally or deployed to a generic static host and navigated article-to-article.
- Cross-variant links target the current published homepages (historical at root, articles at `/raw/`). Published switches use same-origin relative paths so changing the serving domain does not break them; standalone exports may use absolute published URLs. Verify the recovered banner checksum and per-page navigation against the generated exports and reports.
- The `as-is` static site output preserves original page layout/chrome as much as possible while rewriting recovered local dependencies.
- The `raw` article site has a visible `Missing Artifacts` section and all unavailable internal-resource links target that section.
- The EPUB package manifest contains no PDF, MP3, ZIP, EXE, arbitrary HTML, or other non-reader-safe supplemental resources.
- Generated-reader outputs other than the `raw` site's `Missing Artifacts` section do not create standalone missing-resource pages for unavailable files.
- URL redirects and missing asset substitutions are documented.

## R5: Active Content Triage

Status: static-site control repair authorized on 2026-10-15

Type: core

Priority: medium

Pain or value: Minimal active content may exist, but restoring articles is more important than recreating inactive forms or scripts.

Functional behavior:

- Identify active or dynamic features discovered in archived pages, such as forms, search, comments, embedded widgets, calculators, or scripts.
- Preserve raw evidence of active content.
- Exclude active behavior from canonical article content unless it is required to understand the article.
- Record optional restoration decisions for later presentation work.
- In the historical static site, retain working topic navigation and search; repair generated JavaScript links and make search usable without cookies, including keyboard submission and safely displayed queries.
- Remove the expired 2015 Camp Perry countdown rather than invent an upcoming date. Link to the official National Matches page instead.
- Replace obsolete lookup, range, weather and directions forms with links to current services. Remove newsletter, counter, feed, purchasing and advertising controls whose original service is not restored, and slideshow controls for unrecovered images.
- Apply these repairs only during export, with decisions recorded in the reproduction report. Preserve raw captures and canonical article content.
- Both static exports use the verified final forum destination `https://www.bullseyeforum.net/`, including JavaScript navigation and copied HTML redirects, while original captures retain their source URLs.

Acceptance criteria:

- Active/dynamic URLs and page fragments are listed in the recovery report.
- Article backup is not blocked by unrecoverable active behavior.
- Any active feature selected for restoration has a separate requirement before implementation.
- Search handles empty, matching, nonmatching and markup-containing queries; internal links emitted by scripts resolve within the export. Both published variants remain reachable.

## R6: Site Engine Detection

Status: complete for recovered evidence

Type: reference

Priority: medium

Pain or value: Knowing the prior engine or platform affects how much behavior can be restored and how to interpret recovered files.

Functional behavior:

- Inspect recovered raw HTML, URL patterns, scripts, stylesheets, generator meta tags, comments, and common CMS path markers.
- Record whether evidence supports static HTML, a named CMS, a site builder, or insufficient evidence.
- Keep the conclusion evidence-based and update it as more raw pages are recovered.

Acceptance criteria:

- Site-engine analysis report exists under `docs/recovery`.
- The report lists scanned files, positive markers, negative CMS evidence, and a concise conclusion.
