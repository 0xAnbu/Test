import io
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

from pingwatch import checker


class LoadTargetsTest(unittest.TestCase):
    def test_skips_blank_and_comments(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "targets.txt"
            p.write_text("# c\nhttp://a\n\n  http://b  \n")
            self.assertEqual(checker.load_targets(p), ["http://a", "http://b"])


class CheckTest(unittest.TestCase):
    def _resp(self, status):
        r = mock.MagicMock(status=status)
        r.__enter__.return_value = r
        return r

    @mock.patch("pingwatch.checker.urllib.request.urlopen")
    def test_ok(self, urlopen):
        urlopen.return_value = self._resp(200)
        url, status, latency = checker.check("http://a")
        self.assertEqual((url, status), ("http://a", 200))
        self.assertGreaterEqual(latency, 0)
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 5.0)

    @mock.patch("pingwatch.checker.urllib.request.urlopen")
    def test_http_error_keeps_status(self, urlopen):
        urlopen.side_effect = urllib.error.HTTPError("http://a", 503, "x", {}, io.BytesIO())
        self.assertEqual(checker.check("http://a").status, 503)

    @mock.patch("pingwatch.checker.urllib.request.urlopen")
    def test_network_errors_give_zero(self, urlopen):
        for exc in (urllib.error.URLError("down"), TimeoutError(), ConnectionResetError()):
            urlopen.side_effect = exc
            self.assertEqual(checker.check("http://a").status, 0)

    def test_invalid_url_gives_zero(self):
        self.assertEqual(checker.check("not a url").status, 0)


if __name__ == "__main__":
    unittest.main()
