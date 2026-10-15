# Project Goals

## Source Request

`bullseyepistol.com` was taken down by its provider. Recover the content locally from the Wayback Machine, then organize the recovered material so it can be adapted into a single ebook, a static HTML site, or a DB-backed content engine.

## Goals

### G1: Local Preservation

Recover all Wayback-accessible `bullseyepistol.com` articles, source pages, and assets into a local, auditable backup.

Success means:

- The project has a complete URL inventory for known host variants.
- Each successful capture is stored locally with provenance and checksums.
- Failed, missing, redirected, duplicate, and partial captures are recorded.
- The raw backup can be rerun without losing or duplicating prior evidence.

### G2: Presentation-Neutral Canonical Content

Convert recoverable site material into a normalized canonical layer without tying it to a publishing format.

Success means:

- Articles, sections, media, metadata, and links have stable IDs.
- Canonical content traces back to raw captures.
- Internal links are normalized while original URL paths are retained.
- Repeated site chrome is excluded from canonical article bodies unless it carries article navigation, taxonomy, ordering, or provenance value.
- Ambiguous or conflicting snapshots are flagged for review.

### G3: Multi-Target Publishing Readiness

Prepare the recovered content for three downstream presentations: ebook, static site, and DB-backed engine.

Success means:

- Ebook export can order content as chapters or sections.
- Static site export is a good navigable copy of the website that can be deployed as-is anywhere.
- Static site export can reproduce original URLs or a documented redirect map while using local recovered assets.
- DB engine export has article, asset, provenance, link, and taxonomy records.
- Generated outputs are reproducible from canonical content, not hand-edited.

### G4: Release-Facing Artifact Policy

Make the generated reader artifacts clear enough for release review without
spreading missing-resource noise across every format.

Success means:

- The clean article static site is presented as the `raw` site: a normalized,
  provenance-backed article site generated from canonical records.
- The historical full-page reproduction is presented as the `as-is` site.
- The `raw` site has a dedicated `Missing Artifacts` section listing owner-file
  candidates and unrecovered historical resources that might still be found.
- Links in the `raw` site that target unavailable internal resources point to
  the `Missing Artifacts` section instead of standalone missing pages.
- The `as-is` site, EPUB, and PDF avoid reader-facing missing-resource notes
  where practical; they either omit unavailable links, leave non-essential
  original external references alone, or record omissions only in machine
  reports.
- The EPUB package includes only resources expected to open inside common EPUB
  readers: XHTML, CSS, and EPUB-supported image assets. Other recovered
  resources remain outside the EPUB package and are tracked by reports or the
  `raw` site's `Missing Artifacts` section.

## Non-Goals

- Do not modernize copy, branding, or design until preservation is complete.
- Do not invent missing historical content.
- Do not treat a rendered Wayback page as proof that all embedded assets were preserved.
- Do not store provider/site chrome as article content unless explicitly classified as meaningful recovered content.
- Do not build a CMS before the canonical content contract is stable.
