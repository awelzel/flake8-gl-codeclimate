"""
Calling flake8 directly to do some "integration testing".
"""
import json
import os
import subprocess
import tempfile
import unittest


class TestGtlabCodeClimate(unittest.TestCase):

    def setUp(self):
        self.flake8_output_fn = tempfile.mktemp(suffix=".flake8")
        self.gl_codeclimate_output_fn = tempfile.mktemp(suffix=".json")

    def tearDown(self):
        for fn in [self.flake8_output_fn, self.gl_codeclimate_output_fn]:
            try:
                os.unlink(fn)
            except FileNotFoundError:
                pass

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
