import hashlib
import json

from flake8.formatting.base import BaseFormatter

from flake8.plugins.pyflakes import FLAKE8_PYFLAKES_CODES
from mccabe import McCabeChecker
PYFLAKE_CODES = frozenset(FLAKE8_PYFLAKES_CODES.values())
MCCABE_CODES = frozenset([McCabeChecker._code])


class GitlabCodeClimateFormatter(BaseFormatter):
    """
    A formatter implementation aimed to produce codeclimate issues
    as expected by Gitlab...
    """
    @classmethod
    def _make_fingerprint(cls, v):
        b = bytes(" ".join([str(getattr(v, f)) for f in v._fields]), "utf-8")
        return hashlib.sha1(b).hexdigest()

    @classmethod
    def _guess_check_name(cls, v):
        if v.code in MCCABE_CODES:
            return "mccabe"
        elif v.code in PYFLAKE_CODES:
            return "pyflakes"
        elif v.code.startswith("E") or v.code.startswith("W"):
            return "pycodestyle"
        elif v.code.startswith("G"):
            return "logging-format"

        # TODO: Check the flake8 extensions entrypoint - it should list
        #       error code that extensions are using...
        #
        #       Hmm, except flake8-logging-format does not use
        #           G = logging_format.api:LoggingFormatValidator
        #       And even if it would, we would still need to do some magic
        #       matching...
        return "unknown"

    @classmethod
    def _guess_categories(cls, v):
        """
        Try to guess the category the violation falls in.

        categories = {
            "Bug Risk"
            "Clarity"
            "Compatibility"
            "Complexity"
            "Duplication"
            "Performance"
            "Security"
            "Style"
        }

        TODO: This isn't really implemented.
        """
        result = []
        if cls._guess_check_name(v) == "pycodestyle":
            result.append("Style")
        if cls._guess_check_name(v) == "mccabe":
            result.append("Complexity")

        # Need at least one? Default to BugRisk
        if not result:
            result.append("Bug Risk")

        return result

    @classmethod
    def _violation_to_codeclimate_issue(cls, v):
        """
        Given a Violation/error, create a codeclimate issue.

        This is pretty basic for now - the idea to only support the subset
        that Gitlab is actually interested in.

        https://docs.gitlab.com/ee/user/project/merge_requests/code_quality.html#how-it-works  # noqa
        """
        return {
            "type": "issue",
            "check_name": cls._guess_check_name(v),
            "description": "{} [{}]".format(v.text, v.code),
            # "content": content -- Optional. A markdown snippet describing the
            # issue, including deeper explanations and links to other resources.
            "categories": cls._guess_categories(v),
            "location": {
                "path": v.filename,
                "lines": {
                    "begin": v.line_number,
                    "end": v.line_number,
                },
            },
            # trace -- Optional. A Trace object representing other interesting
            #          source code locations related to this issue.
            # remediation_points -- Optional. An integer indicating a rough
            #                       estimate of how long it would take to resolve
            #                       the reported issue.
            "fingerprint": cls._make_fingerprint(v),
            # severity -- Required. A Severity string (info, minor, major,
            #             critical, or blocker) describing the potential impact
            #             of the issue found. Use minor by default.
            "severity": "major" if v.code.startswith("E") else "minor",
        }

    def after_init(self):
        self.__error_written = False  # was an error printed
        self.__indent = 4 * " "

    def write(self, line, source=None):
        """
        Because this outputs a json structure, ignore source and also
        do not add newlines to the output...
        """
        if self.output_fd is not None:
            self.output_fd.write(line)
        if self.output_fd is None or self.options.tee:
            print(line, end="")

    def start(self):
        super().start()
        self.write("[", source=None)

    def stop(self):
        if self.__error_written:
            self.write(self.newline)

        self.write("]" + self.newline)
        super().stop()

    def handle(self, error):
        if self.__error_written:
            self.write(",")

        # Indent
        self.write(self.newline + self.__indent)
        self.write(json.dumps(self._violation_to_codeclimate_issue(error)))

        self.__error_written = True
