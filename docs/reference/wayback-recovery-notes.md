# Wayback Recovery Notes

## Sources Checked

- Internet Archive Help Center, "Using The Wayback Machine": https://archivesupport.zendesk.com/hc/en-us/articles/360004651732-Using-The-Wayback-Machine
- AI Wayback, "The Complete Guide to Restoring Your Website from the Wayback Machine": https://aiwayback.com/guide
- Suganthan, "How to Use the Wayback Machine to Recover Lost Content": https://suganthan.com/blog/how-to-use-wayback-machine/

## Planning Facts

- Internet Archive states archived sites may be incomplete, and broken images usually mean the image was not available on their servers.
- Internet Archive recommends wildcard-style browsing to see archived files for a site.
- Internet Archive does not provide a guaranteed packaged backup service for lost sites; recovery must be built from accessible archived versions.
- Operational recovery should use structured Wayback inventory data, retain all candidate captures before choosing a restoration baseline, and preserve provenance.
- For programmatic retrieval, the planned implementation should verify raw-download behavior with `id_` archive URLs before bulk use, then record any exceptions.

