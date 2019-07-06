#!/usr/bin/env python3
"""
Convert an existing violation report to a Gitlab Code Climate artifact.

Currently only supports the "pylint" output format.

https://docs.gitlab.com/ee/user/project/merge_requests/code_quality.html
"""
import argparse
import json
import logging
import re
import sys

import flake8_gl_codeclimate
from flake8.style_guide import Violation


LOGGER = logging.getLogger(__name__)

# %(path)s:%(row)d: [%(code)s] %(text)
pylint_fmt_re = re.compile(r"^([^ ]+):([0-9]+): \[(.+)\] (.+)$")


def violation_from_pylint_line(l):
    """
    Given a line in "pylint" format, parse out a
    flake8.style_guide.Violation object.

    >>> l = 'tourmap/json.py:23: [E302] expected 2 blank lines, found 1'
    >>> v = violation_from_pylint_line(l)
    >>> v.code, v.filename, v.line_number, v.text
    ('E302', 'tourmap/json.py', 23, 'expected 2 blank lines, found 1')
    """
    match = pylint_fmt_re.match(l.strip())
    if match is None:
        LOGGER.warning("unamtched line: %r", l)
        return None

    filename, line_number, code, text = match.groups()
    return Violation(
        code=code,
        filename=filename,
        line_number=int(line_number),
        column_number=None,
        text=text,
        physical_line=None
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=argparse.FileType(mode="r"), default=sys.stdin)
    parser.add_argument("--output", type=argparse.FileType(mode="w"), default=sys.stdout)
    args = parser.parse_args()

    ccs = []
    fmt = flake8_gl_codeclimate.GitlabCodeClimateFormatter
    for l in args.input:
        v = violation_from_pylint_line(l)
        cc = fmt._violation_to_codeclimate_issue(v)
        ccs.append(cc)

    s = json.dumps(ccs, indent=4)
    args.output.write(s)
    args.output.write("\n")


if __name__ == '__main__':
    main()
