"""Test the CLI's exit status and recurring check interval."""

import io
import unittest
from unittest.mock import patch

from pingwatch.__main__ import main
from pingwatch.checker import CheckResult
from pingwatch.config import Config


class CliTests(unittest.TestCase):
    def setUp(self):
        self.config = Config("http://127.0.0.1:9099/v1/alerts", "test-key")
        self.url = "https://example.test"
        for name in ("load_config", "load_targets", "check_all", "send_alert", "time.sleep"):
            patcher = patch(f"pingwatch.__main__.{name}")
            setattr(self, name.rsplit(".", 1)[-1], patcher.start())
            self.addCleanup(patcher.stop)
        self.load_config.return_value = self.config
        self.load_targets.return_value = [self.url]

    def test_once_reports_failed_delivery_and_does_not_sleep(self):
        result = CheckResult(self.url, 502, 10.0)
        self.check_all.return_value = [result]
        self.send_alert.return_value = False

        with patch("sys.stderr", new_callable=io.StringIO) as stderr:
            self.assertEqual(main(["--once"]), 1)

        self.assertIn(self.url, stderr.getvalue())
        self.send_alert.assert_called_once_with(result, self.config)
        self.sleep.assert_not_called()

    def test_polling_uses_configured_interval_until_interrupted(self):
        self.check_all.return_value = [CheckResult(self.url, 204, 10.0)]
        self.sleep.side_effect = [None, KeyboardInterrupt()]

        self.assertEqual(main(["--interval", "2.5"]), 130)

        self.assertEqual(self.check_all.call_count, 2)
        self.check_all.assert_called_with([self.url], self.config.timeout)
        self.assertEqual([args.args for args in self.sleep.call_args_list], [(2.5,), (2.5,)])
        self.send_alert.assert_not_called()
