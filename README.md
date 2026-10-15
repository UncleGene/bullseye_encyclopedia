# The Encyclopedia of Bullseye Pistol — Recovery

![The Encyclopedia of Bullseye Pistol](docs/images/encyclopedia-of-bullseye-pistol-banner.gif)

This repository preserves and recovers **The Encyclopedia of Bullseye Pistol**, originally published at `bullseyepistol.com`.

This recovery was undertaken at the request of, and with permission from, the rights owners.

The project preserves recovered source pages and assets, records their provenance, and organizes the material for reading as a static website, EPUB, and PDF. Original content and attribution are retained wherever recoverable. Permission for this recovery does not imply a general license to reuse the original material.

## Reading the encyclopedia

The GitHub Pages workflow publishes the historical site at
`https://unclegene.github.io/bullseye_encyclopedia/` and the normalized article site
at `/raw/`. Both versions link to each other. See [deployment setup and status checks](docs/recovery/github-pages.md)
for enabling publication and verifying the live deployment.

Ready-to-read and downloadable editions are in [`exports/final`](exports/final):

- [EPUB](exports/final/bullseye-pistol.epub)
- [PDF](exports/final/bullseye-pistol.pdf)
- [Normalized article website ZIP](exports/final/bullseye-pistol-raw-site.zip)
- [Historical site reproduction ZIP](exports/final/bullseye-pistol-as-is-site.zip)

Extract either website ZIP and open its `index.html` to browse locally.

The historical site retains its recovered layout and topic groups. Broken navigation is repaired during export; inactive service widgets are removed or replaced with current service links. See the [function audit](docs/recovery/site-function-audit.md).

## Repository layout

- [`archive/`](archive/) — recovered source captures, manifests, and provenance.
- [`content/`](content/) — normalized canonical articles and recovered assets.
- [`exports/`](exports/) — generated websites, ebooks, and validation reports.
- [`tools/`](tools/) — recovery, normalization, export, and validation scripts.
- [`docs/`](docs/) — requirements, recovery notes, and project status.

See the [recovery handoff](docs/recovery/handoff.md), [current state](docs/current-state.md), and [validation plan](docs/recovery/validation-plan.md) for technical details and known gaps. Missing or unresolved material is recorded explicitly in the recovery reports.
