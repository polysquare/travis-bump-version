# Travis Bump Version

Automatically bump version when merging to master

## Status

| Travis CI (Ubuntu) | Coverage | PyPI | Licence |
|--------------------|----------|------|---------|
|[![Travis](https://img.shields.io/travis/polysquare/travis-bump-version.svg)]()|[![AppVeyor](https://img.shields.io/appveyor/ci/polysquare/travis-bump-version.svg)]()|[![Coveralls](https://img.shields.io/coveralls/polysquare/travis-bump-version.svg)]()|[![PyPI](https://img.shields.io/pypi/v/travis-bump-version.svg)]()[![PyPI](https://img.shields.io/pypi/pyversions/travis-bump-version.svg)]()|[![License](https://img.shields.io/github/license/polysquare/travis-bump-version.svg)]()|

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