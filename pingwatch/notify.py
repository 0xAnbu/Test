"""Send failed URL checks to the configured HTTP notifier."""

import json
import time
from http.client import HTTPException
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .checker import CheckResult
from .config import Config, load_config


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def send_alert(result: CheckResult, config: Config | None = None) -> bool:
    """Return whether the notifier accepted the alert after up to three retries."""
    if config is None:
        config = load_config()
    data = json.dumps({
        "url": result.url,
        "status": result.status,
        "latency_ms": result.latency_ms,
    }).encode("utf-8")
    request = Request(
        config.notify_url,
        data=data,
        headers={
            "Authorization": f"Bearer {config.notify_api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    opener = build_opener(_NoRedirect())
    for attempt in range(4):
        if attempt:
            time.sleep(2 ** (attempt - 1))
        try:
            with opener.open(request, timeout=config.timeout) as response:
                if 200 <= response.status < 300:
                    return True
        except HTTPError as error:
            error.close()
        except (OSError, HTTPException):
            pass
    return False
