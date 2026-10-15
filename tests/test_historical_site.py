import json
import hashlib
import re
import subprocess
import unittest
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1] / "exports/static-site/as-is"


class HistoricalSiteTest(unittest.TestCase):
    def test_topic_search_without_cookies_and_with_untrusted_query(self):
        script = (ROOT / "pages/search/_scripts/header4.js").read_text()
        harness = r'''
const vm = require("node:vm");
const script = JSON.parse(process.argv[1]);
const results = [];
for (const query of ["", "trigger", "zzzzunmatched", "<img src=x onerror=alert(1)> & '"]) {
  let html = "";
  const context = {window: {location: {search:"?q=" + encodeURIComponent(query)}},
    URLSearchParams, document: {cookie:"", write(s) {html += s;}}};
  vm.createContext(context);
  vm.runInContext(script, context);
  vm.runInContext("findTopic()", context);
  results.push(html);
}
process.stdout.write(JSON.stringify(results));
'''
        result = subprocess.run(["node", "-e", harness, json.dumps(script)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        empty, match, missing, markup = json.loads(result.stdout)
        self.assertIn("Enter a word", empty)
        self.assertIn("2 matching topics", match)
        self.assertIn("trigger-control/index.html", match)
        self.assertIn("There were no matches", missing)
        self.assertIn("&lt;IMG", markup)
        self.assertNotIn("<IMG", markup)

    def test_search_navigation_encodes_query_and_does_not_write_cookie(self):
        script = (ROOT / "_scripts/header11.js").read_text()
        harness = r'''
const vm = require("node:vm");
const context = {window:{location:{}}, document:{cookie:""}};
vm.createContext(context);
vm.runInContext(JSON.parse(process.argv[1]), context);
context.Search({findit:{value:" trigger & sight "}});
process.stdout.write(JSON.stringify(context));
'''
        result = subprocess.run(["node", "-e", harness, json.dumps(script)],
                                capture_output=True, text=True, check=True)
        context = json.loads(result.stdout)
        self.assertEqual(context["window"]["location"]["href"],
                         "pages/search/index.html?q=trigger%20%26%20sight")
        self.assertEqual(context["document"]["cookie"], "")

    def test_misspelled_chapter_search_and_empty_forum_capture_are_repaired(self):
        script = (ROOT / "pages/search/_scripts/header4.js").read_text()
        for index in (5, 11):
            destination = re.search(rf'fd\[{index}\] = (.*)', script)[1]
            self.assertIn("articles/perfecting-technique/alcohol-coffee-tobacco-and-drugs/index.html", destination)
            self.assertNotIn("chaptr10", destination)
        for index in (37, 55, 78):
            destination = re.search(rf'fd\[{index}\] = (.*)', script)[1]
            self.assertIn("https://www.bullseyeforum.net/", destination)
            self.assertIn(">current forum</a>", destination)
            self.assertNotIn("bulseyel/index.html", destination)

    def test_inactive_homepage_widgets_removed_without_losing_topics(self):
        html = (ROOT / "index.html").read_text()
        for obsolete in ("showtime();", "javascript:bac", "javascript:frw", "subscribe/post",
                         "counter.digits.com", "twitter-timeline", "wts_subresults.asp"):
            self.assertFalse(obsolete in html, obsolete)
        for retained in ("Perfecting", "Shooting", "Biography", "Read the Clean Edition",
                         "pix", "image1.jpg", "thecmp.org/cmp-national-matches/", "onsubmit="):
            self.assertIn(retained, html)

    def test_related_article_arguments_resolve(self):
        count = 0
        for page in ROOT.rglob("*.html"):
            html = page.read_text(errors="replace")
            for match in re.finditer(r'\bheader\(([^;\n]*)\)', html):
                args = re.findall(r'"([^"]*)"', match.group(1))
                if len(args) != 3:
                    continue
                href = args[2]
                url = urlparse(href)
                if url.scheme or not url.path:
                    continue
                self.assertTrue((page.parent / unquote(url.path)).exists(), f"{page}: {href}")
                count += 1
        self.assertGreater(count, 100)

    def test_links_emitted_by_page_scripts_resolve(self):
        count = 0
        for script in ROOT.glob("**/_scripts/*.js"):
            for match in re.finditer(r'''(?:href|src|background)=['"]([^'"<>]+)['"]''', script.read_text()):
                href = match[1]
                url = urlparse(href)
                if url.scheme or not url.path or "+" in href:
                    continue
                self.assertTrue((script.parent.parent / unquote(url.path)).exists(), f"{script}: {href}")
                count += 1
        self.assertGreater(count, 2000)

    def test_script_urls_change_with_their_content(self):
        count = 0
        for page in ROOT.rglob("*.html"):
            for src in re.findall(r'<script[^>]+src="([^"]+)"', page.read_text(errors="replace")):
                url = urlparse(src)
                self.assertIn("_scripts/", url.path)
                script = page.parent / unquote(url.path)
                version = hashlib.sha256(script.read_bytes()).hexdigest()[:12]
                self.assertEqual(url.query, "v=" + version)
                count += 1
        self.assertGreater(count, 200)

    def test_unavailable_order_forms_and_member_login_are_removed(self):
        for page in ROOT.rglob("*.html"):
            html = page.read_text(errors="replace")
            self.assertFalse(re.search(r'<form\b[^>]*(?:paypal\.com|formmailto\.com)', html, re.I), str(page))
            self.assertFalse(re.search(r'<input[^>]+Order Advertising', html, re.I), str(page))
        member = (ROOT / "pages/pi-a/index.html").read_text()
        self.assertNotIn("mStation", member)
        self.assertIn("monthly club information", member)


if __name__ == "__main__":
    unittest.main()
