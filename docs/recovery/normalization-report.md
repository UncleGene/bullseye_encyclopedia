# Canonical Normalization Report

Date: 2026-05-22

## Inputs

- Raw backup manifest: `archive/raw/wayback/manifests/20260522T-combined-backup-blobs.json`
- Image recovery manifest: `archive/raw/wayback/manifests/20260522T-combined-image-recovery.json`

## Output

- Canonical articles: `content/canonical/articles`
- Article index: `content/canonical/articles.index.json`
- Page shell index: `content/canonical/page-shells.index.json`
- Asset index: `content/assets/assets.index.json`
- Machine report: `archive/normalized/article-normalization-report.json`

## Results

- Canonical article records: `150`
- Page shell records: `27`
- Canonical asset records referenced by articles: `165`
- Recovered article records: `149`
- Partial article records: `1`
- Articles with multiple body variants: `31`

## Extraction Rules

- Article body extraction uses the site's `ARTICLE BEGINS/ENDS` HTML comment markers.
- Header/footer JavaScript, global style blocks, and template wrapper markup are omitted from canonical article bodies.
- The preferred article body uses the latest recovered capture for that canonical article.
- Older captures remain in provenance for comparison, rollback, and historical review.
- Records without article markers are retained as page shells, not forced into article bodies.

## Validation

- Verified `content/canonical/articles.index.json` contains `150` articles.
- Verified sampled article `goodgrip` omits `ARTICLE BEGINS`, `header(...)`, and `footer()` from its canonical body.
- Verified sampled article `goodgrip` selects the latest recovered capture: `20250816021344`.

