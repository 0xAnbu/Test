"""Run URL checks once or at a fixed interval."""

import argparse
import math
import sys
import time

from .checker import check_all, load_targets
from .config import load_config
from .notify import send_alert


def _positive_seconds(value: str) -> float:
    try:
        seconds = float(value)
    except ValueError:
        seconds = 0
    if not math.isfinite(seconds) or seconds <= 0:
        raise argparse.ArgumentTypeError("interval must be a finite positive number")
    return seconds


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Monitor configured URLs.")
    parser.add_argument("--once", action="store_true", help="run one round of checks")
    parser.add_argument("--interval", type=_positive_seconds, default=60, metavar="SECONDS")
    args = parser.parse_args(argv)
    try:
        config = load_config()
        targets = load_targets(config.targets_file)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    try:
        while True:
            delivered = True
            for result in check_all(targets, config.timeout):
                if (result.status == 0 or result.status >= 500) and not send_alert(result, config):
                    print(f"Could not send alert for {result.url}", file=sys.stderr)
                    delivered = False
            if args.once:
                return 0 if delivered else 1
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
