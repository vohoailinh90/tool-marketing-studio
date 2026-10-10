import tempfile
import unittest
from pathlib import Path

from mkt.metrics import MetricsError, append_row, read_rows, totals, verdict

VALIDATION = {"min_counts": {"reach": 100, "link_clicks": 10}, "go_if": {"signups": 3, "click_rate": 0.01}}


def row(**counts):
    base = {"date": "2026-10-12", "post": "01", "lang": "vi", "platform": "facebook"}
    return {**base, **counts}


class MetricsTests(unittest.TestCase):
    def setUp(self):
        self.path = Path(tempfile.mkdtemp()) / "metrics.csv"

    def test_below_minimum_counts_is_insufficient_data(self):
        append_row(self.path, row(reach=50, link_clicks=40, signups=9))
        self.assertEqual(verdict(totals(read_rows(self.path)), VALIDATION)[0], "INSUFFICIENT_DATA")

    def test_targets_met_is_go(self):
        append_row(self.path, row(reach=1000, link_clicks=20, signups=3))
        self.assertEqual(verdict(totals(read_rows(self.path)), VALIDATION)[0], "GO")

    def test_targets_missed_is_not_yet(self):
        append_row(self.path, row(reach=1000, link_clicks=20, signups=1))
        self.assertEqual(verdict(totals(read_rows(self.path)), VALIDATION)[0], "NOT_YET")

    def test_rates_with_no_base_are_unknown(self):
        self.assertIsNone(totals([])["click_rate"])

    def test_counts_must_be_whole_numbers(self):
        with self.assertRaises(MetricsError):
            append_row(self.path, row(reach="12.5"))


if __name__ == "__main__":
    unittest.main()
