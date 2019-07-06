# flake8-gitlab-codeclimate

[![Build Status](https://travis-ci.org/awelzel/flake8-gl-codeclimate.svg?branch=master)](https://travis-ci.org/awelzel/flake8-gl-codeclimate)

Flake8 formatter producing [Gitlab Code Quality artifacts][1].

## Usage

By default, Flake8 will print to standard output. However, the purpose of this
formatter is to produce a JSON file that is then stored as Code Quality artifact
by Gitlab (see below) - the output itself isn't very human-readable:
```
$ pip install flake8-gl-codeclimate
$ flake8 --format gl-codeclimate examples/trailing-whitespace.py
[
    {"type": "issue", "check_name": "pycodestyle", "description": "trailing whitespace [W291]", ... }
]
```

## Adding it to Gitlab

To enable Code Quality reports based on Flake8 in Gitlab merge requests,
add a configuration as follows to your projects `gitlab-ci.yml` file.

```
flake8:
  script:
    - pip install flake8-gl-codeclimate
    - flake8 --exit-zero --format gl-codeclimate --output-file gl-code-quality-report.json my_package/
  artifacts:
    reports:
      codequality: gl-code-quality-report.json
```
This will upload the `gl-code-quality-report.json` as Gitlab Code Quality artifact.
Afterwards, code quality improvements and degradations should show up in
merge requests on Gitlab.

Gitlab Code Quality artifacts are a subset of the [Code Climate spec][2].

Have fun!


[1]: https://docs.gitlab.com/ee/user/project/merge_requests/code_quality.html
[2]: https://github.com/codeclimate/spec/blob/master/SPEC.md#data-types
