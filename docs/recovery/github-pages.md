# GitHub Pages deployment

## Published layout

User decision, 2026-10-15: publish the normalized `raw` article site as the
main website and the historical `as-is` reproduction as the secondary site.

- Main: `https://unclegene.github.io/bullseye_encyclopedia/`
- Historical: `https://unclegene.github.io/bullseye_encyclopedia/as-is/`

The workflow is `.github/workflows/pages.yml`. It stages the contents of
`exports/static-site/raw` at the deployment root and copies
`exports/static-site/as-is` into its `as-is/` subdirectory. It validates the
combined layout and the historical site separately before uploading the
staged website to Pages. It publishes the committed exports; it does not
rebuild them or alter archive or canonical files.

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
The existing relative links keep both sites under the repository's URL
prefix. Custom domains and redirects from the original domain remain
separate decisions.
