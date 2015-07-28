# /travisbumpversion/main.py
#
# Entry point for travis-bump-version.
#
# See /LICENCE.md for Copyright information
"""Entry point for travis-bump-version.."""
import argparse

import atexit

import os

import subprocess

import sys

import yaml

try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, "wb")
    atexit.register(DEVNULL.close)


def error(message):
    """Print message to stderr."""
    sys.stderr.write("{}\n".format(message))


def _print_except_specifier_message():
    """Print message about how the user needs an except specifier."""
    # B901 is matched within these quotes
    #
    # suppress(B901)
    error("""bumpversion: Need to have branches: except: - /^v[0.9].*/ """
          """in /.travis.yml, otherwise it is not safe to push new tags """
          """without a build-loop.""")


def _check_travis_yml():
    """Check /.travis.yml to see if it is safe to do version bumps."""
    try:
        with open(".travis.yml", "r") as travis_yml:
            travis_config = yaml.load(travis_yml.read())
    except IOError:
        error("""bumpversion: Need to be able to read /.travis.yml to """
              """determine if safe to do automatic version bumps.""")
        return False

    try:
        except_specifiers = travis_config["branches"]["except"]
    except (KeyError, TypeError):
        _print_except_specifier_message()
        return False

    if "/^v[0-9].*/" not in except_specifiers:
        _print_except_specifier_message()
        return False

    return True


def _last_commit_message_body():
    """Read body of last commit message from git."""
    return subprocess.check_output(["git",  # pragma: no cover
                                    "log",
                                    "--format=%b",
                                    "-n",
                                    "1"]).decode("utf-8").strip()


def _get_level():
    """Read the last commit message and get the version bump level."""
    level = "patch"
    last_msg = _last_commit_message_body()

    if len(last_msg):
        code = [w for w in last_msg.splitlines()[-1].split(" ") if len(w)]

        if len(code) > 1 and code[0] == "bumpversion:":
            valid = ("major", "minor", "patch")
            if code[1] not in valid:
                error("""bumpversion: Invalid code {} given, expected """
                      """major, minor or patch. """
                      """Assuming patch""".format(code[1]))
            else:
                level = code[1]

    return level


def _last_tag_from_git():
    """Read known tag from git."""
    return subprocess.check_output(["git",  # pragma: no cover
                                    "describe",
                                    "--tags"]).decode("utf-8").strip()


def _call_bumpversion(level, files):
    """Call bumpversion to create commit and bump version."""
    subprocess.check_call([  # pragma: no cover
        "bumpversion",
        level
    ] + list(files) + [
        "--commit",
        "--tag",
        "--verbose"
    ])


def _push_commit_and_tags(api_token, repo):
    """Push most recent commit and tags to repo, using api_token."""
    subprocess.check_call(["git",  # pragma: no cover
                           "push",
                           "https://{}@github.com/{}".format(api_token,
                                                             repo),
                           "master",
                           "--tags"],
                          stdout=DEVNULL,
                          stderr=DEVNULL)


def version_bump(api_token=None,
                 repo=None,
                 files=None):
    """Check if possible to bump version and bump version."""
    if not files or not len(files):
        error("""Need to specify some files""")
        return 1

    if not _check_travis_yml():
        return 1

    last_tag = _last_tag_from_git()

    if not last_tag.startswith("v"):
        error("""Release a tag that matches vx.x.x to get automatic """
              """version bumps""")
        return 1

    _call_bumpversion(_get_level(), files)

    try:
        _push_commit_and_tags(api_token, repo)
    except subprocess.CalledProcessError:
        error("""bumpversion: Failed to push commit, assuming that another """
              """job was able to push it first.""")

    return 0


def main(arguments=None):  # suppress(unused-function)
    """Run travis-bump-version, pass files to version_bump."""
    parser = argparse.ArgumentParser(description="""Automatically bump """
                                                 """version on successful """
                                                 """Travis-CI builds.""")
    parser.add_argument("--api-token",
                        required=True,
                        type=str,
                        help="""GitHub API token. Always make sure this """
                             """variable is encrypted first.""")
    parser.add_argument("--repo",
                        required=True,
                        type=str,
                        help="""Name of repo on GitHub, eg user/repo.""")
    parser.add_argument("files",
                        nargs="*",
                        metavar=("FILE"),
                        help="""bump version on FILE""")
    result = parser.parse_args(arguments or sys.argv[1:])

    sys.exit(version_bump(**vars(result)))
