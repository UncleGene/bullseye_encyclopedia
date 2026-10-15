# Content Structure

## Directory Roles

```text
archive/
  raw/
    wayback/
      cdx/              # source inventories and query outputs
      files/            # downloaded raw files from archive URLs
      manifests/        # retrieval attempts, checksums, status, provenance
  normalized/           # intermediate extraction output, before editorial review

content/
  canonical/            # source of truth for reusable restored articles
  assets/               # recovered media with stable IDs and provenance

exports/
  final/                # final single-file release artifacts and zipped site bundles
  ebook/                # generated ebook output
  static-site/          # generated static HTML output
    as-is/              # deployable reproduction of recovered pages/chrome
    raw/                # clean article-first generated site
  db-engine/            # generated import files, fixtures, or migrations

tools/                  # recovery and transformation scripts
docs/                   # goals, roadmap, specs, validation, and reports
```

## Record Types

### Article

- `id`: stable canonical identifier.
- `original_urls`: one or more historical URLs.
- `title`: recovered title or explicit missing marker.
- `byline`: author or source attribution when available.
- `published_at`: recovered publication date when available.
- `updated_at`: recovered update date when available.
- `body`: normalized content blocks.
- `context`: useful non-body article context, such as category, series, breadcrumb, or adjacent-article links.
- `omitted_chrome`: repeated page elements intentionally excluded from the article body.
- `assets`: referenced canonical asset IDs.
- `links`: internal and external link records.
- `provenance`: raw capture IDs and confidence notes.
- `status`: recovered, partial, duplicate, conflict, or missing.

### Page Shell

Page shells are raw or intermediate records used to analyze templates and recurring chrome. They are not canonical article content.

- `id`: stable shell identifier.
- `source_capture_id`: raw capture used for analysis.
- `template_markers`: selectors, text patterns, or structure used to detect chrome.
- `navigation_links`: links useful for article discovery or ordering.
- `excluded_regions`: headers, footers, sidebars, widgets, ads, provider wrappers, or other recurring elements.

### Asset

- `id`: stable canonical identifier.
- `original_urls`: source URLs from HTML, CSS, or manifests.
- `file_path`: local recovered file path.
- `media_type`: MIME type.
- `checksum`: content hash.
- `provenance`: raw capture ID, retrieval timestamp, and fallback notes.
- `status`: recovered, missing, substituted, or excluded.

### Provenance

- `capture_id`: stable ID derived from URL, timestamp, and digest.
- `wayback_timestamp`: archive timestamp.
- `original_url`: URL recorded by Wayback.
- `retrieval_url`: URL used to download the local copy.
- `retrieved_at`: local retrieval time.
- `http_status`: status received during retrieval.
- `checksum`: hash of local bytes when downloaded.

## Export Mapping

- Ebook: the raw recovered index page defines generic topic order and chapter groups; linked canonical articles become chapter entries, eligible articles not listed on the raw index are included in an explicit additional-recovered appendix group, recovered ebook-safe assets become embedded media, and provenance becomes an appendix and metadata. See `docs/recovery/ebook-export-contract.md`.
- Raw static site: recovered pages become deployable HTML routes with original layout/chrome preserved as much as possible and dependencies rewritten to local recovered files.
- Raw article static site: articles become HTML routes in a self-contained deployable website; assets are copied from recovered local blobs to public paths; original URLs are preserved; unavailable internal resources are centralized in `missing-artifacts.html`; navigation preserves recovered homepage sections with an additional enhanced browse layer.
- DB engine: articles, assets, links, taxonomy, and provenance become importable records.
