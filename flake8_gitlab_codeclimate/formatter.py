import hashlib
import logging
import re

from flake8.style_guide import Violation
from flake8.formatting.base import BaseFormatter

from flake8.plugins.pyflakes import FLAKE8_PYFLAKES_CODES
from mccabe import McCabeChecker
PYFLAKE_CODES = frozenset(FLAKE8_PYFLAKES_CODES.values())
MCCABE_CODES = frozenset([McCabeChecker._code])


LOGGER = logging.getLogger(__name__)



class GitlabCodeClimateFormatter(BaseFormatter):
    """
    A formatter implementation aimed to produce codeclimate issues
    as expected by Gitlab...
    """
    @classmethod
    def _make_fingerprint(cls, v):
        """
        """
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

        return "unknown"

    @classmethod
    def _guess_categories(cls, v):
        """
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
        """
        result = []
        if cls._guess_check_name(v) == "pycodestyle":
            result.append("Style")

        # Need at least one? Default to BugRisk
        if not result:
            result.append("Bug Risk")

        return result

    @classmethod
    def _violation_to_codeclimate_issue(cls, v):
        """
        Given a flake8.style_guide.Violation, create a codeclimate issue.

        This is pretty basic for now - the idea to only support the subset
        that Gitlab is actually interested in.

        https://docs.gitlab.com/ee/user/project/merge_requests/code_quality.html#how-it-works
        """
        return {
            "type": "issue",
            "check_name": cls._guess_check_name(v),
            "description": v.text,
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
            # severity -- Optional. A Severity string (info, minor, major,
            #             critical, or blocker) describing the potential impact
            #             of the issue found.
            "fingerprint": cls._make_fingerprint(v),
        }
