"""
Calling flake8 directly to do some "integration testing".
"""
import json
import subprocess
import tempfile
import unittest

try:
    import flake8_bandit  # noqa: F401
    have_bandit = True
except ImportError:
    have_bandit = False


class TestGtlabCodeClimate(unittest.TestCase):

    def setUp(self):
        self.flake8_output_f = tempfile.NamedTemporaryFile(suffix=".flake8", dir=".")
        self.flake8_output_fn = self.flake8_output_f.name

        self.gl_codeclimate_output_f = tempfile.NamedTemporaryFile(suffix=".json", dir=".")
        self.gl_codeclimate_output_fn = self.gl_codeclimate_output_f.name

    def tearDown(self):
        for f in [self.flake8_output_f, self.gl_codeclimate_output_f]:
            f.close()

    def test__flake8_format_gl_codeclimate_good(self):
        args = [
            "flake8",
            "--format", "gl-codeclimate",
            "--output-file", self.flake8_output_fn,
            "examples/good.py",
        ]
        subprocess.call(args)

        with open(self.flake8_output_fn) as fp:
            data = fp.read()
            result = json.loads(data)

        self.assertEqual(0, len(result))

    def test__flake8_format_gl_codeclimate_bandit(self):
        if not have_bandit:
            self.skipTest("No flake8-bandit installed.")
        args = [
            "flake8",
            "--format", "gl-codeclimate",
            "--output-file", self.flake8_output_fn,
            "examples/bandit.py",
        ]
        subprocess.call(args)

        with open(self.flake8_output_fn) as fp:
            data = fp.read()
            result = json.loads(data)

        self.assertEqual(4, len(result))
        self.assertEqual("bandit", result[0]["check_name"])
        self.assertEqual(["Security"], result[0]["categories"])
        self.assertIn("insecure function", result[0]["description"])

    def test__flake8_format_gl_codeclimate_import_order(self):
        args = [
            "flake8",
            "--format", "gl-codeclimate",
            "--output-file", self.flake8_output_fn,
            "examples/order.py",
        ]
        subprocess.call(args)

        with open(self.flake8_output_fn) as fp:
            data = fp.read()
            result = json.loads(data)

        self.assertEqual(2, len(result))
        self.assertEqual("import-order", result[0]["check_name"])
        self.assertEqual(["Style"], result[0]["categories"])
        self.assertIn("should be before", result[0]["description"])
        self.assertIn("a different group", result[0]["description"])

    def test__flake8_format_gl_codeclimate_simplify(self):
        args = [
            "flake8",
            "--format", "gl-codeclimate",
            "--output-file", self.flake8_output_fn,
            "examples/simplify.py",
        ]
        subprocess.call(args)

        with open(self.flake8_output_fn) as fp:
            data = fp.read()
            result = json.loads(data)

        self.assertEqual(1, len(result))
        self.assertEqual("simplify", result[0]["check_name"])
        self.assertEqual(["Style", "Clarity"], result[0]["categories"])
        self.assertIn("contextlib.suppress", result[0]["description"])

    def test__flake8_format_gl_codeclimate_bad(self):
        args = [
            "flake8",
            "--format", "gl-codeclimate",
            "--output-file", self.flake8_output_fn,
            "examples/bad.py",
        ]
        subprocess.call(args)

        with open(self.flake8_output_fn) as fp:
            data = fp.read()
            result = json.loads(data)

        self.assertEqual(5, len(result))
        self.assertIn("imported but unused", result[0]["description"])
        self.assertIn("undefined name 'parsre' [F821]", result[-1]["description"])

    def test__flake8_report__to_gl_codeclimate(self):
        args = [
            "flake8",
            "--output-file", self.flake8_output_fn,
            "examples/bad.py",
        ]
        subprocess.call(args)

        args = [
            "scripts/report-to-gl-codeclimate.py",
            "--input-file", self.flake8_output_fn,
            "--output-file", self.gl_codeclimate_output_fn,
        ]
        out = subprocess.check_output(args)
        self.assertFalse(out)
        with open(self.gl_codeclimate_output_fn) as fp:
            data = fp.read()
            result = json.loads(data)

        self.assertEqual(5, len(result))
        self.assertIn("imported but unused", result[0]["description"])
        self.assertIn("undefined name 'parsre' [F821]", result[-1]["description"])

    def test__pylint_report__to_gl_codeclimate(self):
        args = [
            "flake8",
            "--format", "pylint",
            "--output-file", self.flake8_output_fn,
            "examples/bad.py",
        ]
        subprocess.call(args)

        args = [
            "scripts/report-to-gl-codeclimate.py",
            "--input-file", self.flake8_output_fn,
            "--output-file", self.gl_codeclimate_output_fn,
        ]
        out = subprocess.check_output(args)
        self.assertFalse(out)

        with open(self.gl_codeclimate_output_fn) as fp:
            data = fp.read()
            result = json.loads(data)

        self.assertEqual(5, len(result))
        self.assertIn("imported but unused", result[0]["description"])
        self.assertIn("undefined name 'parsre' [F821]", result[-1]["description"])

    def test__report_show_source__to_gl_codeclimate(self):
        args = [
            "flake8",
            "--show-source",
            "--output-file", self.flake8_output_fn,
            "examples/bad.py",
        ]
        subprocess.call(args)

        args = [
            "scripts/report-to-gl-codeclimate.py",
            "--input-file", self.flake8_output_fn,
            "--output-file", self.gl_codeclimate_output_fn,
        ]
        out = subprocess.check_output(args)
        self.assertFalse(out)

        with open(self.gl_codeclimate_output_fn) as fp:
            data = fp.read()
            result = json.loads(data)

        self.assertEqual(5, len(result))
        self.assertIn("imported but unused", result[0]["description"])
        self.assertIn("undefined name 'parsre' [F821]", result[-1]["description"])
