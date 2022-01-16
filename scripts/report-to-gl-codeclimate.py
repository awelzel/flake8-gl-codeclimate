#!/usr/bin/env python3
"""
Convert an existing flake8 report to a Gitlab Code Climate artifact.

This guesses the format by trying default and pylint..

https://docs.gitlab.com/ee/user/project/merge_requests/code_quality.html
"""
import argparse
import logging
import re
import sys

import flake8_gl_codeclimate
from flake8.style_guide import Violation


LOGGER = logging.getLogger(__name__)

# %(path)s:%(row)d:%(col)d: %(code)s %(text)s
flake8_fmt_re = re.compile(r"^([^ ]+):([0-9]+):([0-9]+): ([^ ]+) (.+)$")


def violation_from_flake8_line(line):
    """
    Given a line in "default format, parse out a Violation.

        examples/unused-module.py:5:1: F401 'sys' imported but unused

    """
    match = flake8_fmt_re.match(line.strip())
    if match is None:
        return None

    filename, line_number, column_number, code, text = match.groups()
    return Violation(
        code=code,
        filename=filename,
        line_number=int(line_number),
        column_number=int(column_number),
        text=text,
        physical_line=None
    )


# %(path)s:%(row)d: [%(code)s] %(text)
pylint_fmt_re = re.compile(r"^([^ ]+):([0-9]+): \[([^ ]+)\] (.+)$")


def violation_from_pylint_line(line):
    """
    Given a line in "pylint" format, parse out a Violation.

    >>> line = 'tourmap/json.py:23: [E302] expected 2 blank lines, found 1'
    >>> v = violation_from_pylint_line(line)
    >>> v.code, v.filename, v.line_number, v.text
    ('E302', 'tourmap/json.py', 23, 'expected 2 blank lines, found 1')
    """
    match = pylint_fmt_re.match(line.strip())
    if match is None:
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
    parser.add_argument("--input-file", type=argparse.FileType(mode="r"),
                        default=sys.stdin)
    parser.add_argument("--output-file", type=str)
    parser.add_argument("--tee", action="store_true", default=False)
    options = parser.parse_args()
    ignored = 0

    fmt = flake8_gl_codeclimate.GitlabCodeClimateFormatter(options)
    fmt.start()
    for line in options.input_file:
        v = violation_from_flake8_line(line)
        if v is None:
            v = violation_from_pylint_line(line)
        if v is None:
            ignored += 1
            continue

        fmt.handle(v)

    fmt.stop()

    if ignored:
        LOGGER.warning("Ignored %d input lines", ignored)


if __name__ == '__main__':
    main()
