"""URL exclusion keeps its meaning and handles URL-free long lines promptly."""
from pathlib import Path
import random
import re
import subprocess
import sys
import unittest

from scripts import sd101_check as check

ROOT = Path(__file__).resolve().parents[1]
OLD = re.compile(r"[A-Za-z][A-Za-z0-9+.\-]*://[^\s<>]+")


class UrlStripTests(unittest.TestCase):
    def test_preserves_address_boundaries_and_surrounding_prose(self):
        cases = ["", "API TLS", "Note:LLM", "https://", "https://<> API", "0+.-https://host/API TLS",
                 "https://a/API<LLM>", "WSS://a/TLS\nDNS", "git+ssh://host/API/TLS.git", "file:///API",
                 "1://host/API", "a://x://y TLS", "<https://a/API> https://b/DNS", "áhttps://a/API\u2003LLM"]
        for text in cases:
            with self.subTest(text=text):
                self.assertEqual(OLD.sub(" ", text), check.strip_urls(text))

    def test_matches_the_previous_rule_on_short_generated_inputs(self):
        rng = random.Random(84)
        alphabet = "abAZ19+.-:/<> \n\tá"
        for _ in range(1000):
            text = "".join(rng.choices(alphabet, k=rng.randrange(80)))
            self.assertEqual(OLD.sub(" ", text), check.strip_urls(text), repr(text))

    def test_long_url_free_runs_and_scheme_prefixes_finish_promptly(self):
        # A subprocess bounds regressions without leaving a runaway regex in the test process.
        program = '''from scripts.sd101_check import strip_urls
for text in ["a" * 200_000, "+9.-" * 50_000, ("9:// ") * 40_000]:
    assert strip_urls(text) == text
assert strip_urls("a" * 200_000 + "://host/API TLS") == "  TLS"
'''
        result = subprocess.run([sys.executable, "-c", program], cwd=ROOT, capture_output=True,
                                text=True, timeout=5, check=False)
        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
