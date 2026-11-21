"""Exercise the CLI and notification delivery against a local HTTP server."""

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import call, patch

from pingwatch.checker import CheckResult
from pingwatch.config import Config
from pingwatch.notify import send_alert


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(int(self.path.lstrip("/")))
        self.end_headers()

    def do_POST(self):
        size = int(self.headers["Content-Length"])
        self.server.alerts.append(
            (self.path, self.headers["Authorization"], json.loads(self.rfile.read(size)))
        )
        self.send_response(self.server.notify_status)
        self.end_headers()

    def log_message(self, format, *args):
        pass


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.addCleanup(self.server.server_close)
        self.server.alerts = []
        self.server.notify_status = 204
        thread = threading.Thread(target=self.server.serve_forever)
        thread.start()
        self.addCleanup(thread.join)
        self.addCleanup(self.server.shutdown)
        self.base = f"http://127.0.0.1:{self.server.server_port}"
        self.notify_url = f"{self.base}/v1/alerts"

    def test_cli_only_sends_alerts_for_failed_checks(self):
        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory, socket.socket() as closed:
            closed.bind(("127.0.0.1", 0))
            unreachable = f"http://127.0.0.1:{closed.getsockname()[1]}/"
            workdir = Path(directory)
            (workdir / ".env").write_text(
                f"NOTIFY_URL={self.notify_url}\nNOTIFY_API_KEY=integration-test\n",
                encoding="utf-8",
            )
            (workdir / "targets.txt").write_text(
                f"{self.base}/200\n{self.base}/404\n{self.base}/500\n{unreachable}\n",
                encoding="utf-8",
            )
            env = {
                key: value for key, value in os.environ.items()
                if key not in {"NOTIFY_URL", "NOTIFY_API_KEY", "TARGETS_FILE", "TIMEOUT"}
            }
            env["PYTHONPATH"] = str(repo)
            result = subprocess.run(
                [sys.executable, "-m", "pingwatch", "--once"],
                cwd=workdir,
                env=env,
                capture_output=True,
                text=True,
                timeout=15,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            [(path, auth, body["url"], body["status"]) for path, auth, body in self.server.alerts],
            [
                ("/v1/alerts", "Bearer integration-test", f"{self.base}/500", 500),
                ("/v1/alerts", "Bearer integration-test", unreachable, 0),
            ],
        )
        for _, _, body in self.server.alerts:
            self.assertGreaterEqual(body["latency_ms"], 0)

    def test_retries_three_times_with_exponential_backoff(self):
        self.server.notify_status = 503
        config = Config(notify_url=self.notify_url, notify_api_key="integration-test")
        with patch("pingwatch.notify.time.sleep") as sleep:
            delivered = send_alert(CheckResult(f"{self.base}/500", 500, 1.0), config)
        self.assertFalse(delivered)
        self.assertEqual(sleep.call_args_list, [call(1), call(2), call(4)])
        self.assertEqual(len(self.server.alerts), 4)


if __name__ == "__main__":
    unittest.main()
