# Validation Plan

## Scope

Validate the recovery workflow for R1 Wayback Inventory, R2 Raw Capture Backup, R3 Canonical Content Normalization, R4 Multi-Target Export Contracts, and R5 Active Content Triage.

## Test Cases

### Inventory Completeness

- Run discovery for apex and `www` variants.
- Verify raw query outputs are stored unchanged.
- Verify manifest counts match raw inventory records.
- Verify status code and MIME type summaries are generated.
- Verify article candidate URLs are separated from assets, index/navigation pages, active/dynamic pages, duplicates, and non-content.

### Idempotency

- Run inventory twice.
- Confirm unchanged records are stable.
- Confirm new records appear as explicit additions, not duplicates.

### Raw File Provenance

- For each downloaded file, verify manifest path, original URL, Wayback timestamp, retrieval URL, checksum, byte length, and retrieval time.
- Verify failed downloads have a manifest entry with reason.
- Verify successful downloads reference a SHA-256 blob path and storage mode.
- Verify identical SHA-256 values reuse the same blob path instead of storing duplicate bytes.

### Missing Asset Handling

- Use sampled pages with images, stylesheets, scripts, and linked documents.
- Confirm missing assets are searched across alternate timestamps.
- Confirm unresolved assets are recorded as missing rather than silently removed.

### Article Image Recovery

- Extract image references from sampled downloaded article HTML.
- Confirm relative images resolve against the original article URL.
- Confirm matching Wayback image captures are downloaded with parent article provenance.
- Confirm unresolved image references are listed with reason.
- Confirm repeated image bytes across articles or periods share the same blob path.

### Site Engine Detection

- Scan recovered HTML for generator meta tags, comments, script/style paths, CMS directory markers, and URL extension patterns.
- Confirm the report distinguishes positive evidence from absence of evidence.
- Confirm the conclusion is updated after additional raw pages are recovered.

### Canonical Traceability

- For sampled canonical articles, verify original URL, source capture ID, normalized title, content blocks, links, and assets against raw HTML.
- Confirm duplicate URL variants map to one canonical article when content is equivalent.

### Article Body Extraction

- Sample articles across different historical snapshots or templates.
- Confirm canonical article bodies exclude recurring header, footer, sidebar, ad, widget, provider, and unrelated navigation chrome.
- Confirm meaningful article context is retained outside the body when relevant, including category, series, breadcrumb, byline, date, captions, and adjacent-article links.

### Active Content Triage

- Sample forms, scripts, comments, search pages, widgets, or other dynamic fragments discovered during inventory.
- Confirm raw evidence is preserved.
- Confirm active behavior is listed separately and does not block article backup.

### Export Reproducibility

- Generate a sample ebook, static page, and DB import file from the same canonical records.
- Delete generated output and rebuild it.
- Confirm generated output is not the source of truth.
- Open the generated static site locally and verify article navigation works without Wayback-hosted resources.
- Verify static site image references point to local recovered assets or explicit missing-asset placeholders.
- Verify the `as-is` static site preserves original recovered page layout/chrome while using local files for recovered dependencies.
- Verify the `raw` article static site excludes unnecessary site chrome from article bodies.
- Verify the `raw` article static site has a `Missing Artifacts` section and every unavailable internal-resource link targets that section.
- Verify the `as-is`, EPUB, and PDF outputs avoid standalone reader-facing missing-resource pages or missing-resource prose where practical.
- Verify the EPUB OPF manifest contains only EPUB-reader-safe packaged media types.

## Release Gates

- Discovery and backup scripts run without unhandled errors.
- Manifests validate against files on disk.
- Recovery report lists complete, partial, duplicate, missing, and unresolved items.
- Canonical records pass traceability spot checks.
- Article body extraction passes chrome-exclusion spot checks.
- Static site export is self-contained, navigable, and deployable as-is.
- The `raw` article static site exposes missing artifacts in one dedicated section.
- The `as-is`, EPUB, and PDF outputs avoid reader-facing missing-resource notes where practical while preserving omission evidence in reports.
- EPUB contains no packaged PDF, MP3, ZIP, EXE, arbitrary HTML, or other non-reader-safe supplemental resources.
- Documentation is updated when the content contract changes.

## Current Test Commands

Use these commands for the current generated artifacts:

```sh
python3 -m py_compile tools/*.py
python3 tools/validate_static_site.py exports/static-site/as-is --report exports/static-site/as-is/_validation-report.json
python3 tools/validate_static_site.py exports/static-site/raw --expect-articles 150 --require-all-articles --report exports/static-site/raw/_validation-report.json
python3 - <<'PY'
import zipfile, xml.etree.ElementTree as ET
allowed = {
    "application/xhtml+xml",
    "text/css",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/svg+xml",
}
with zipfile.ZipFile("exports/ebook/bullseye-pistol.epub") as zf:
    root = ET.fromstring(zf.read("OEBPS/content.opf"))
bad = []
for item in root.findall(".//{http://www.idpf.org/2007/opf}item"):
    media_type = item.attrib.get("media-type")
    href = item.attrib.get("href")
    if media_type not in allowed:
        bad.append((media_type, href))
if bad:
    raise SystemExit(f"Non-reader-safe EPUB resources: {bad}")
PY
```
