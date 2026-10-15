import tempfile
import unittest
from pathlib import Path
from urllib.parse import urljoin, urlparse

from tools.stage_pages import stage_site


class StagePagesTest(unittest.TestCase):
    def test_switches_resolve_from_home_and_nested_pages_on_either_domain(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            exports = root / "exports"
            for variant, other in [("as-is", "raw"), ("raw", "as-is")]:
                for name in ["index.html", "articles/example/index.html"]:
                    page = exports / variant / name
                    page.parent.mkdir(parents=True, exist_ok=True)
                    page.write_text(
                        f'<a data-site-variant="{other}" href="https://example.org/old/">Other version</a>'
                        '<p>Preserved article text</p>'
                    )
            stage_site(exports, root / "site")
            for name in ["index.html", "articles/example/index.html", "raw/index.html", "raw/articles/example/index.html"]:
                content = (root / "site" / name).read_text()
                href = content.split('href="')[1].split('"')[0]
                self.assertFalse(urlparse(href).scheme)
                for origin in ["https://unclegene.github.io", "https://203.softover.com"]:
                    actual = urljoin(f"{origin}/bullseye_encyclopedia/{name}", href)
                    target = "index.html" if name.startswith("raw/") else "raw/index.html"
                    self.assertEqual(actual, f"{origin}/bullseye_encyclopedia/{target}")
                self.assertIn('<p>Preserved article text</p>', content)
            self.assertIn('https://example.org/old/', (exports / "as-is/index.html").read_text())


if __name__ == "__main__":
    unittest.main()
