"""Check target URLs with a GET request."""

from __future__ import annotations

import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import NamedTuple

DEFAULT_TIMEOUT = 5.0


class CheckResult(NamedTuple):
    url: str
    status: int  # HTTP status code; 0 on network error
    latency_ms: float


def load_targets(path: str | os.PathLike[str] = "targets.txt") -> list[str]:
    """Return non-empty, non-comment lines from the targets file."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [s for s in (line.strip() for line in lines) if s and not s.startswith("#")]


def check(url: str, timeout: float = DEFAULT_TIMEOUT) -> CheckResult:
    """GET `url`; HTTP errors keep their status, network errors give status 0."""
    start = time.perf_counter()
    try:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "pingwatch"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
    except urllib.error.HTTPError as exc:
        status = exc.code
        exc.close()
    except (urllib.error.URLError, OSError, ValueError):
        status = 0
    latency_ms = round((time.perf_counter() - start) * 1000, 1)
    return CheckResult(url, status, latency_ms)


def check_all(targets: list[str], timeout: float = DEFAULT_TIMEOUT) -> list[CheckResult]:
    return [check(url, timeout) for url in targets]
