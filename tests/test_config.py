import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from pingwatch.config import Config, load_config, parse_env


class ParseEnvTest(unittest.TestCase):
    def test_parses_comments_quotes_and_export(self):
        text = '# c\n\nexport A=1\nB="two words"\nC=\'x=y\'\nD=val # note\n'
        self.assertEqual(parse_env(text), {"A": "1", "B": "two words", "C": "x=y", "D": "val"})

    def test_rejects_malformed_line(self):
        with self.assertRaises(ValueError):
            parse_env("NOT A PAIR\n")


class LoadConfigTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.env = Path(self.tmp.name) / ".env"
        patcher = mock.patch.dict(os.environ, {}, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_loads_values_and_defaults(self):
        self.env.write_text("NOTIFY_URL=http://x/a\nNOTIFY_API_KEY=k\n")
        self.assertEqual(load_config(self.env), Config("http://x/a", "k"))

    def test_environment_overrides_file(self):
        self.env.write_text("NOTIFY_URL=http://x/a\nNOTIFY_API_KEY=k\nTIMEOUT=2\n")
        os.environ["NOTIFY_API_KEY"] = "from-env"
        cfg = load_config(self.env)
        self.assertEqual((cfg.notify_api_key, cfg.timeout), ("from-env", 2.0))

    def test_missing_required_raises(self):
        self.env.write_text("NOTIFY_URL=http://x/a\n")
        with self.assertRaisesRegex(ValueError, "NOTIFY_API_KEY"):
            load_config(self.env)

    def test_rejects_invalid_timeout(self):
        for value in ("0", "-1", "nan", "inf", "abc"):
            with self.subTest(value=value):
                self.env.write_text(f"NOTIFY_URL=u\nNOTIFY_API_KEY=k\nTIMEOUT={value}\n")
                with self.assertRaisesRegex(ValueError, "TIMEOUT"):
                    load_config(self.env)

    def test_repr_hides_key(self):
        self.assertNotIn("secret", repr(Config("u", "secret")))


if __name__ == "__main__":
    unittest.main()
