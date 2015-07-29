# Travis Bump Version

Automatically bump version when merging to master.

## Status

| Travis CI (Ubuntu) | Coverage | PyPI | Licence |
|--------------------|----------|------|---------|
|[![Travis](https://img.shields.io/travis/polysquare/travis-bump-version.svg)](http://travis-ci.org/polysquare/travis-bump-version)|[![Coveralls](https://img.shields.io/coveralls/polysquare/travis-bump-version.svg)](http://coveralls.io/polysquare/travis-bump-version)|[![PyPIVersion](https://img.shields.io/pypi/v/travis-bump-version.svg)](https://pypi.python.org/pypi/travis-bump-version)[![PyPIPythons](https://img.shields.io/pypi/pyversions/travis-bump-version.svg)](https://pypi.python.org/pypi/travis-bump-version)|[![License](https://img.shields.io/github/license/polysquare/travis-bump-version.svg)](http://github.com/polysquare/travis-bump-version)|

## Usage

    usage: travis-bump-version [-h] --api-token API_TOKEN --repo REPO
                               [FILE [FILE ...]]

    Automatically bump version on successful Travis-CI builds.

    positional arguments:
      FILE                  bump version on FILE

    optional arguments:
      -h, --help            show this help message and exit
      --api-token API_TOKEN
                            GitHub API token. Always make sure this variable is
                            encrypted first.
      --repo REPO           Name of repo on GitHub, eg user/repo.

On Travis-CI you can use the `TRAVIS_REPO_SLUG` variable to determine
the current repository. See [this guide](https://github.com/blog/1509-personal-api-tokens)
on how to generate an API token. Remember to encrypt it first using
`travis encrypt --add env.global` first!
