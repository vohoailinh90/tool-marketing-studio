"""The CI workflow's triggers and concurrency: one run per commit, and a newer run replaces a waiting one."""

import unittest

import yaml

from mkt.model import ROOT

WORKFLOW = ROOT / ".github/workflows/ci.yml"


def workflow() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def triggers(config: dict) -> dict:
    # YAML 1.1 reads the bare key `on` as the boolean True.
    return config[True] if True in config else config["on"]


class CiTriggerTests(unittest.TestCase):
    def test_a_push_runs_only_on_main(self):
        push = triggers(workflow())["push"]
        self.assertEqual(["main"], push["branches"])

    def test_a_pull_request_still_runs_ci(self):
        self.assertIn("pull_request", triggers(workflow()))


class CiConcurrencyTests(unittest.TestCase):
    def test_a_newer_pull_request_run_replaces_an_older_one(self):
        concurrency = workflow()["concurrency"]
        self.assertIn("github.event.pull_request.number", concurrency["group"])
        self.assertIn("github.event_name == 'pull_request'", str(concurrency["cancel-in-progress"]))

    def test_pushes_to_one_ref_share_a_group_so_a_waiting_run_is_replaced(self):
        group = workflow()["concurrency"]["group"]
        self.assertIn("github.ref", group)
        self.assertNotIn("github.run_id", group)

    def test_a_started_push_run_is_not_cancelled(self):
        cancel = str(workflow()["concurrency"]["cancel-in-progress"])
        self.assertNotIn("true", cancel.lower().replace("github.event_name == 'pull_request'", ""))


if __name__ == "__main__":
    unittest.main()
