"""Load settings from a .env file (own parser, no dependencies)."""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    notify_url: str
    notify_api_key: str
    targets_file: str = "targets.txt"
    timeout: float = 5.0

    def __repr__(self) -> str:  # never leak the API key in logs
        return (
            f"Config(notify_url={self.notify_url!r}, notify_api_key='***', "
            f"targets_file={self.targets_file!r}, timeout={self.timeout!r})"
        )


def parse_env(text: str) -> dict[str, str]:
    """Parse KEY=VALUE lines; supports comments, `export`, and quoted values."""
    values: dict[str, str] = {}
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        key, sep, value = line.partition("=")
        key = key.strip()
        if not sep or not key.isidentifier():
            raise ValueError(f".env line {lineno}: expected KEY=VALUE")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        elif " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        values[key] = value
    return values


def load_config(path: str | os.PathLike[str] = ".env") -> Config:
    """Read `path` (if present); process environment variables take precedence."""
    p = Path(path)
    values = parse_env(p.read_text(encoding="utf-8")) if p.is_file() else {}
    values.update({k: v for k, v in os.environ.items() if k in _KEYS})

    missing = [k for k in ("NOTIFY_URL", "NOTIFY_API_KEY") if not values.get(k)]
    if missing:
        raise ValueError(f"missing required settings: {', '.join(missing)}")

    try:
        timeout = float(values.get("TIMEOUT", 5.0))
    except ValueError:
        raise ValueError("TIMEOUT must be a number") from None
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("TIMEOUT must be a finite positive number")

    return Config(
        notify_url=values["NOTIFY_URL"],
        notify_api_key=values["NOTIFY_API_KEY"],
        targets_file=values.get("TARGETS_FILE") or "targets.txt",
        timeout=timeout,
    )


_KEYS = ("NOTIFY_URL", "NOTIFY_API_KEY", "TARGETS_FILE", "TIMEOUT")
