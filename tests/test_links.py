import unittest
from urllib.parse import parse_qs, urlsplit

from mkt.links import tracked_link


class LinkTests(unittest.TestCase):
    def test_utm_parameters_name_post_language_and_platform(self):
        url = tracked_link("https://example.com/f?a=1", campaign="c", post="01", lang="ja", platform="facebook")
        query = parse_qs(urlsplit(url).query)
        self.assertEqual(query["a"], ["1"])
        self.assertEqual(query["utm_source"], ["facebook"])
        self.assertEqual(query["utm_content"], ["01-ja"])

    def test_an_existing_utm_parameter_is_kept(self):
        url = tracked_link("https://example.com/?utm_source=x", campaign="c", post="01", lang="vi", platform="facebook")
        self.assertEqual(parse_qs(urlsplit(url).query)["utm_source"], ["x"])

    def test_source_placeholder_is_filled(self):
        url = tracked_link("https://forms.example/v?entry.1={source}", campaign="c", post="01", lang="vi", platform="x")
        self.assertTrue(url.endswith("entry.1=c-01-vi-x"))

    def test_a_placeholder_url_gives_no_link(self):
        self.assertEqual(tracked_link("https://REPLACE_ME/x", campaign="c", post="01", lang="vi", platform="x"), "")
        self.assertEqual(tracked_link("javascript:alert(1)", campaign="c", post="01", lang="vi", platform="x"), "")


if __name__ == "__main__":
    unittest.main()
