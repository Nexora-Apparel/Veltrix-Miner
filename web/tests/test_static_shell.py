from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "index.html"


class ShellParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.nav_targets = set()
        self.assets = set()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "a" and values.get("data-view"):
            self.nav_targets.add(values["data-view"])
        if tag == "link" and values.get("href"):
            self.assets.add(values["href"])
        if tag == "script" and values.get("src"):
            self.assets.add(values["src"])


class StaticShellTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML_PATH.read_text(encoding="utf-8")
        cls.parser = ShellParser()
        cls.parser.feed(cls.html)
        cls.js = (ROOT / "app.js").read_text(encoding="utf-8")
        cls.api = (ROOT / "api.js").read_text(encoding="utf-8")
        cls.config = (ROOT / "config.js").read_text(encoding="utf-8")
        cls.css = (ROOT / "styles.css").read_text(encoding="utf-8")

    def test_navigation_targets_have_views(self):
        for name in self.parser.nav_targets:
            self.assertIn(f"view-{name}", self.parser.ids)

    def test_local_assets_and_modules_exist(self):
        for asset in self.parser.assets:
            if asset.startswith(("http://", "https://", "//")):
                self.fail(f"External asset is not allowed in the zero-dependency shell: {asset}")
            self.assertTrue((ROOT / asset).is_file(), f"Missing local asset: {asset}")
        for module in ("api.js", "config.js"):
            self.assertTrue((ROOT / module).is_file(), f"Missing module: {module}")

    def test_all_required_sections_exist(self):
        expected = {
            "overview", "market", "profitability", "workers", "pools",
            "earnings", "costs", "audit", "settings",
        }
        self.assertEqual(self.parser.nav_targets, expected)

    def test_no_background_mining_or_polling_primitives(self):
        source = self.html + self.js + self.api
        forbidden = [
            r"WebAssembly", r"SharedWorker", r"new\s+Worker\s*\(",
            r"navigator\.hardwareConcurrency", r"setInterval\s*\(",
            r"requestAnimationFrame\s*\(",
        ]
        for pattern in forbidden:
            self.assertIsNone(re.search(pattern, source, re.IGNORECASE), pattern)

    def test_unknown_values_are_not_fake_zeroes(self):
        self.assertIn("UNKNOWN", self.html)
        self.assertIn("UNCONFIGURED", self.html)
        self.assertIn("No verified earnings recorded", self.html)

    def test_api_client_fails_closed_and_validates_provenance(self):
        self.assertIn('apiBaseUrl: ""', self.config)
        self.assertIn('url.protocol !== "https:"', self.api)
        self.assertIn('credentials: "omit"', self.api)
        self.assertIn('cache: "no-store"', self.api)
        self.assertIn('row.source !== "coingecko"', self.api)
        self.assertIn("quoteMaxAgeMs", self.api)
        self.assertIn("INCOMPLETE_DATA", self.api)

    def test_api_refresh_is_manual_and_bounded(self):
        self.assertIn('refresh.addEventListener("click", refreshData)', self.js)
        self.assertIn("requestTimeoutMs", self.api)
        self.assertNotIn("setInterval(", self.js + self.api)

    def test_mobile_layout_and_api_states_exist(self):
        self.assertIn("@media", self.css)
        self.assertIn("max-width:760px", self.css)
        for state in (".state.verified", ".state.stale", ".state.error"):
            self.assertIn(state, self.css)

    def test_health_and_market_bindings_are_present(self):
        for element_id in (
            "api-service-state", "database-state",
            "quote-btc", "quote-xmr", "quote-ltc", "quote-doge",
        ):
            self.assertIn(element_id, self.parser.ids)


if __name__ == "__main__":
    unittest.main()
