# Recovery Specification

## Summary

Recover `bullseyepistol.com`, primarily a collection of articles, from Wayback into a local repository with three layers:

1. `archive/raw`: immutable discovery metadata and downloaded Wayback source files.
2. `content/canonical`: normalized article, asset, link, taxonomy, and provenance records.
3. `exports`: generated ebook, static site, and DB-engine outputs.

The first implementation slice is a read-only Wayback inventory plus local raw backup manifest. Normalization and exports depend on that evidence. Full raw pages remain evidence, but canonical article bodies must omit unnecessary site chrome.

## Inputs

- Domain: `bullseyepistol.com`.
- Host variants: apex, `www`, HTTP, HTTPS, and discovered subdomains.
- Archive source: Internet Archive Wayback Machine.
- Source records: timestamp, original URL, status code, MIME type, digest, byte length when available, and retrieval URL.
- Content classification: article, article index/navigation, asset, active/dynamic, duplicate, or non-content.
- Local constraints: preserve provenance, avoid duplicate canonical records, and keep generated output separate from source content.

## Outputs

- CDX or equivalent inventory files under `archive/raw/wayback/cdx`.
- Raw downloaded files under `archive/raw/wayback/files`.
- Manifests describing every attempted and successful retrieval.
- Canonical article records under `content/canonical`.
- Asset catalog under `content/assets`.
- Chrome extraction notes that identify omitted recurring headers, footers, sidebars, widgets, and provider wrappers.
- Export contracts and generated artifacts under `exports`, including an
  `as-is` self-contained static website that preserves recovered page
  layout/chrome plus a normalized `raw` article site generated from canonical
  records.
- Ebook export contract: `docs/recovery/ebook-export-contract.md`.

Completeness guarantee: the backup can only claim completeness against the captured Wayback inventory and any additional owner-provided source lists. It cannot claim recovery of content that was never archived or provided.

## Error Cases

- Wayback returns no records for a host variant.
- Latest snapshot is a parked, deleted, blocked, or degraded page.
- Assets are missing from the same timestamp as the HTML page.
- A linked internal artifact is not recoverable but might still be found from
  owner files or a later source.
- Third-party media, forms, widgets, or scripts cannot be recovered.
- Multiple snapshots conflict on page content.
- Article body extraction accidentally includes recurring site chrome.
- Article body extraction removes meaningful article context, such as series navigation, breadcrumbs, captions, author/date, or category labels.
- Retrieval is throttled or interrupted.
- A URL appears under several hosts or paths and risks duplicate canonical records.

## Non-Goals

- No public relaunch in the preservation slice.
- No design modernization during raw recovery.
- No manual content rewriting before provenance exists.
- No restoration of active behavior unless later required separately.
- No DB schema implementation before canonical content fields are validated.
- No static export that depends on Wayback-hosted images or scripts for normal article navigation.

## Open Questions

No open question blocks the DB import/export contract definition as the next slice.

Deferred or routed questions:

- Historical baseline authority: deferred until snapshot conflicts affect a deliverable. Current recovery uses the documented selected baseline/overlay set.
- External assets or provider backups outside Wayback: routed to missing-resource review; do not silently replace missing files.
- Final public URL policy: deferred until a public rebuild or redirect-map slice.
- Ebook cover image is deferred. Supplemental recovered resources that are not
  EPUB-reader-safe are excluded from the EPUB package and tracked in reports or
  static-site artifact lists instead.
- Additional article-body/chrome selectors: deferred unless a later normalization pass finds canonical articles that cannot be reliably extracted with current markers and page-shell evidence.

## Related Decisions

- See `docs/project-goals.md`.
- See `docs/requirements.md`.
- See `docs/recovery/content-structure.md`.
- See `docs/recovery/ebook-export-contract.md`.
