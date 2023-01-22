import json
import tempfile
import unittest
import unittest.mock

from flake8.style_guide import Violation

from flake8_gl_codeclimate import GitlabCodeClimateFormatter


class TestGitlabCodeClimateFormatter(unittest.TestCase):

    def setUp(self):
        self.options = unittest.mock.Mock(["output_file", "tee", "color"])
        self.output_f = tempfile.NamedTemporaryFile(suffix=".json", dir=".")
        self.options.output_file = self.output_f.name
        self.options.tee = False
        self.options.color = "auto"

        self.formatter = GitlabCodeClimateFormatter(self.options)
        self.error1 = Violation(
            code="E302",
            filename="./examples/hello-world.py",
            line_number=23,
            column_number=None,
            text="expected 2 blank lines, found 1",
            physical_line=None,
        )

        self.error2 = Violation(
            code="X111",  # unknown
            filename="./examples/unknown.py",
            line_number=99,
            column_number=None,
            text="Some extension produced this.",
            physical_line=None,
        )

        self.logging_error = Violation(
            code="G001",  # This is coming from flake8-logging-format
            filename="./examples/logging-format.py",
            line_number=4,
            column_number=None,
            text="Logging statement uses string.format()",
            physical_line=None,
        )

        self.complexity_error = Violation(
            code="C901",  # This is coming from flake8-logging-format
            filename="./examples/complex-code.py",
            line_number=42,
            column_number=None,
            text="Something is too complex",
            physical_line=None,
        )

        self.security_error = Violation(
            code="S102",  # This is coming from flake8-bandit
            filename="examples/insecure-code.py",
            line_number=42,
            column_number=None,
            text="Use of exec detected",
            physical_line=None,
        )

    def tearDown(self):
        self.output_f.close()

    def test_no_errors(self):
        self.formatter.start()
        self.formatter.stop()
        with open(self.options.output_file) as fp:
            violations = json.load(fp)
        self.assertEqual(0, len(violations))

    def test_error1(self):
        self.formatter.start()
        self.formatter.handle(self.error1)
        self.formatter.stop()

        with open(self.options.output_file) as fp:
            violations = json.load(fp)

        self.assertEqual(1, len(violations))
        self.assertEqual("issue", violations[0]["type"])
        self.assertEqual("pycodestyle", violations[0]["check_name"])
        self.assertEqual(["Style"], violations[0]["categories"])
        self.assertEqual("major", violations[0]["severity"])

    def test_error1_and_error2(self):
        self.formatter.start()
        self.formatter.handle(self.error1)
        self.formatter.handle(self.error2)
        self.formatter.stop()

        with open(self.options.output_file) as fp:
            violations = json.load(fp)

        self.assertEqual(2, len(violations))
        self.assertEqual("issue", violations[1]["type"])
        self.assertEqual("unknown", violations[1]["check_name"])
        self.assertEqual("minor", violations[1]["severity"])

    def test_logging_errro(self):
        self.formatter.start()
        self.formatter.handle(self.logging_error)
        self.formatter.stop()

        with open(self.options.output_file) as fp:
            violations = json.load(fp)

        self.assertEqual(1, len(violations))
        self.assertEqual("logging-format", violations[0]["check_name"])
        self.assertEqual("minor", violations[0]["severity"])

    def test_complexity_error(self):
        self.formatter.start()
        self.formatter.handle(self.complexity_error)
        self.formatter.stop()

        with open(self.options.output_file) as fp:
            violations = json.load(fp)

        self.assertEqual(1, len(violations))
        self.assertEqual("mccabe", violations[0]["check_name"])
        self.assertEqual(["Complexity"], violations[0]["categories"])
        self.assertEqual("minor", violations[0]["severity"])

    def test_security_error(self):
        self.formatter.start()
        self.formatter.handle(self.security_error)
        self.formatter.stop()

        with open(self.options.output_file) as fp:
            violations = json.load(fp)

        self.assertEqual(1, len(violations))
        self.assertEqual("bandit", violations[0]["check_name"])
        self.assertEqual(["Security"], violations[0]["categories"])
        self.assertEqual("critical", violations[0]["severity"])

    def test_error_filepath_with_prefix(self):
        self.formatter.start()
        self.formatter.handle(self.security_error)
        self.formatter.stop()

        with open(self.options.output_file) as fp:
            violations = json.load(fp)

        self.assertEqual(1, len(violations))
        self.assertEqual("examples/insecure-code.py", violations[0]["location"]["path"])

    def test_error_filepath(self):
        self.formatter.start()
        self.formatter.handle(self.error1)
        self.formatter.stop()

        with open(self.options.output_file) as fp:
            violations = json.load(fp)

        self.assertEqual(1, len(violations))
        self.assertEqual("examples/hello-world.py", violations[0]["location"]["path"])
