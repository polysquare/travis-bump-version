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

try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, "wb")
    atexit.register(DEVNULL.close)


def error(message):
    """Print message to stderr."""
    sys.stderr.write("{}\n".format(message))


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


def _last_tag_from_git(repo=""):
    """Read known tag from git."""
    subprocess.check_call(["git", "checkout", "master"])  # pragma: no cover
    subprocess.check_call(["git",  # pragma: no cover
                           "fetch",
                           "--tags",
                           "git://github.com/{}".format(repo)])
    return subprocess.check_output(["git",  # pragma: no cover
                                    "describe",
                                    "--tags"]).decode("utf-8").strip()


def _call_bumpversion(level, files):
    """Call bumpversion to create commit and bump version."""
    subprocess.check_call(["git",  # pragma: no cover
                           "config",
                           "user.name",
                           "Travis-CI"])
    subprocess.check_call(["git",  # pragma: no cover
                           "config",
                           "user.email",
                           "travis@travis-ci.org"])
    subprocess.check_call([  # pragma: no cover
        "bumpversion",
        level
    ] + list(files) + [
        "--commit",
        "--message",
        "Bump version: {current_version} -> {new_version}\n\n[ci skip]",
        "--tag",
        "--verbose"
    ])


def _push_commit_and_tags(api_token, repo):
    """Push most recent commit and tags to repo, using api_token."""
    subprocess.check_call(["git",  # pragma: no cover
                           "push",
                           "https://{0}@github.com/{1}".format(api_token,
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

    last_tag = _last_tag_from_git(repo)

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
