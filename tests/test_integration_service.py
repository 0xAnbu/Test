"""Integration test against the real local notifier at 127.0.0.1:9099.

The valid-key test only runs when NOTIFY_API_KEY is set in the environment,
so the key never has to be written to disk or shared.
"""

import os
import socket
import unittest
from unittest import mock

from pingwatch.checker import CheckResult
from pingwatch.config import Config
from pingwatch.notify import send_alert

SERVICE_URL = "http://127.0.0.1:9099/v1/alerts"


def _service_up() -> bool:
    try:
        with socket.create_connection(("127.0.0.1", 9099), timeout=1):
            return True
    except OSError:
        return False


@unittest.skipUnless(_service_up(), "notifier service not running on 127.0.0.1:9099")
class NotifierServiceTests(unittest.TestCase):
    result = CheckResult("http://example.invalid/", 0, 12.5)

    @unittest.skipUnless(os.environ.get("NOTIFY_API_KEY"), "NOTIFY_API_KEY not set")
    def test_alert_accepted_with_valid_key(self):
        config = Config(SERVICE_URL, os.environ["NOTIFY_API_KEY"])
        self.assertTrue(send_alert(self.result, config))

    def test_alert_rejected_with_wrong_key(self):
        config = Config(SERVICE_URL, "wrong-key")
        with mock.patch("pingwatch.notify.time.sleep"):
            self.assertFalse(send_alert(self.result, config))


if __name__ == "__main__":
    unittest.main()
