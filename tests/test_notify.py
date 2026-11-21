"""Test notification retries without sockets or sleeping."""

import json
import unittest
from unittest.mock import call, patch

from pingwatch.checker import CheckResult
from pingwatch.config import Config
from pingwatch.notify import send_alert


class NotifyTests(unittest.TestCase):
    def test_retries_connection_reset_then_sends_json_with_bearer(self):
        config = Config("http://127.0.0.1:9099/v1/alerts", "test-key")
        result = CheckResult("https://example.test", 503, 12.5)

        with patch("pingwatch.notify.build_opener") as build, patch(
            "pingwatch.notify.time.sleep"
        ) as sleep:
            opener = build.return_value
            response = opener.open.return_value
            response.__enter__.return_value.status = 202
            opener.open.side_effect = [ConnectionResetError(), response]

            self.assertTrue(send_alert(result, config))

        self.assertEqual(sleep.call_args_list, [call(1)])
        self.assertEqual(opener.open.call_count, 2)
        request = opener.open.call_args.args[0]
        self.assertEqual(request.full_url, config.notify_url)
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertEqual(json.loads(request.data), result._asdict())
