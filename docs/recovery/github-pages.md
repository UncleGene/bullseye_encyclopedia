# GitHub Pages deployment

## Published layout

User decision, 2026-10-15 (revised): publish the historical `as-is` reproduction
as the main website and the normalized `raw` article site under `/raw/`.
This supersedes the earlier root/secondary assignment.

- Historical main site: `https://unclegene.github.io/bullseye_encyclopedia/`
- Article version: `https://unclegene.github.io/bullseye_encyclopedia/raw/`

Deployment verified on 2026-10-15: [workflow run 38814095608](https://github.com/UncleGene/bullseye_encyclopedia/actions/runs/38814095608)
succeeded for commit `0b22bcd`. Both public URLs returned HTTP 200. The main
homepage contains its original historical banner and the relative Article
Version link; `/raw/` contains the recovered banner and a relative return
link. The default GitHub URL served directly without a custom-domain redirect
at verification time. These were HTTP/HTML checks, not live browser testing.

The workflow is `.github/workflows/pages.yml`. `tools/stage_pages.py` stages the contents of
`exports/static-site/as-is` at the deployment root and copies
`exports/static-site/raw` into its `raw/` subdirectory. It validates the
combined layout and the source article export before uploading the
staged website to Pages. It publishes the committed exports; it does not
rebuild them or alter archive or canonical files.

## Links and banner

The 2026-10-15 control repairs first deployed successfully as `430193f` in
[run 38820995649](https://github.com/UncleGene/bullseye_encyclopedia/actions/runs/38820995649).
Chrome confirmed the replacement Camp Perry link, removed inactive widgets,
current `https://www.bullseyeforum.net/` destinations, and both edition switches.
A post-deployment search check exposed cached pre-repair JavaScript. The
generator now versions page-local script URLs by their content hash; the
regression suite checks every emitted script URL. See
[the function audit](site-function-audit.md) for repair policy and limitations.

The historical homepage includes **Read the Clean Edition** beside **Website Index**
in its recovered navigation and a prominent green-and-cream link directly below
the historical banner. The accompanying text explains that it contains the same
recovered articles with simpler navigation and an uncluttered reading layout. Other historical
content pages have a compact switch using the same green-and-cream palette.
Empty captures, empty redirect shells, and the frameset wrapper are preserved
without added navigation.
The article site's header includes the original recovered encyclopedia banner
and a **Historical site** return link on every generated page. The banner is
copied unchanged from the archived `banner2.gif`; its capture and checksum are
recorded in `exports/static-site/raw/_raw-export-report.json`.

Standalone exports use the full published addresses above for version switches,
so downloaded editions can open the other version online. Pages staging rewrites
only the marked version-switch URLs to relative paths. Published switches stay
on the serving domain, including an account-level custom domain, without
hardcoding a host or repository prefix. Each variant's own page and asset links
remain relative. Both generators own the presentation changes; the final
website ZIPs are refreshed from the rebuilt exports.

## Enable and run

In the repository's **Settings > Pages > Build and deployment**, select
**GitHub Actions** as the source. This requires repository settings access.
Then open **Actions > Publish encyclopedia > Run workflow**, selecting
`main`. Subsequent pushes to `main` also publish automatically.

Watch the workflow result and its `github-pages` deployment URL to confirm
publication. The addresses above describe the intended layout; committing
the workflow alone does not establish that Pages is enabled or live.

GitHub's reference: [custom Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Scope

Only the staged static websites are uploaded. The raw archive, canonical
records, tools, and repository documentation are outside the Pages artifact.
The relative page and asset links keep both sites under the repository's URL
prefix. Custom domains and redirects from the original domain remain
separate decisions.
