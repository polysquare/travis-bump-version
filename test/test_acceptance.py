# /test/test_acceptance.py
#
# Acceptance tests for travis-bump-version.
#
# See /LICENCE.md for Copyright information
"""Acceptance tests for travis-bump-version."""

import os

import shutil

import subprocess

import sys

import tempfile

from mock import Mock, call

from nose_parameterized import parameterized

from six import StringIO

from testtools import TestCase
from testtools.matchers import Contains, MatchesAll

import travisbumpversion.main

import yaml


def run(*args, **kwargs):
    """Run, converting kwargs to switches and passing args."""
    arguments = list(args)
    for key, value in kwargs.items():
        arguments.append("--" + key.replace("_", "-"))
        if not isinstance(value, list):
            value = [value]

        arguments.extend(value)

    try:
        travisbumpversion.main.main(arguments)
    finally:
        sys.stderr.seek(0)
        sys.stdout.seek(0)


def _write_travis_yml():
    """Write correctly formed /.travis.yml file."""
    options = {
        "branches": {
            "except": [
                "/^v[0-9].*/"
            ]
        }
    }

    assert not os.path.exists(".travis.yml")

    with open(".travis.yml", "w") as travis_yml:
        yaml.dump(options, travis_yml)


def _format_with_args(func, num, params):
    """Format docstring using provided arguments."""
    del num

    return func.__doc__.format(*params[0])


class TestAcceptance(TestCase):

    """Acceptance tests for travis-bump-version."""

    def __init__(self, *args, **kwargs):
        """Initialize instance variables."""
        super(TestAcceptance, self).__init__(*args, **kwargs)
        self.last_commit_message_body = Mock()
        self.last_tag_from_git = Mock()
        self.call_bumpversion = Mock()
        self.push_commit_and_tags = Mock()

    def setUp(self):
        """Set up acceptance tests, patch out functions calling subprocess."""
        super(TestAcceptance, self).setUp()
        self.patch(travisbumpversion.main,
                   "_last_commit_message_body",
                   self.last_commit_message_body)
        self.patch(travisbumpversion.main,
                   "_last_tag_from_git",
                   self.last_tag_from_git)
        self.patch(travisbumpversion.main,
                   "_call_bumpversion",
                   self.call_bumpversion)
        self.patch(travisbumpversion.main,
                   "_push_commit_and_tags",
                   self.push_commit_and_tags)
        self.patch(sys, "exit", Mock())
        self.patch(sys, "stdout", StringIO())
        self.patch(sys, "stderr", StringIO())

        last_directory = os.getcwd()
        temp_dir = tempfile.mkdtemp(dir=last_directory,
                                    prefix="bumpversionacceptance")
        os.chdir(temp_dir)
        self.addCleanup(lambda: os.chdir(last_directory))
        self.addCleanup(lambda: shutil.rmtree(temp_dir))

    def test_bail_when_not_passing_api_token(self):
        """Raise when failing to pass --api-token."""
        run("file", repo="user/repo")
        output = sys.stderr.read()
        self.assertThat(output, MatchesAll(Contains("""--api-token"""),
                                           Contains("""required""")))
        self.assertEqual(call(2), sys.exit.call_args_list[0])

    def test_bail_when_not_passing_repo(self):
        """Raise when failing to pass --repo."""
        run("file", api_token="token")
        output = sys.stderr.read()
        self.assertThat(output, MatchesAll(Contains("""--repo"""),
                                           Contains("""required""")))
        self.assertEqual(call(2), sys.exit.call_args_list[0])

    def test_bail_when_not_passing_files(self):
        """Raise when failing to pass list of files."""
        run(api_token="token", repo="user/repo")
        self.assertThat(sys.stderr.read(),
                        Contains("""Need to specify some files"""))
        self.assertEqual(call(1), sys.exit.call_args_list[0])

    def test_bail_when_travis_yml_doesnt_exist(self):
        """Raise when /.travis.yml doesn't exist."""
        run("file", api_token="token", repo="user/repo")
        self.assertThat(sys.stderr.read(),
                        Contains("""Need to be able to read /.travis.yml"""))
        self.assertEqual(call(1), sys.exit.call_args_list[0])

    def test_bail_when_travis_yml_doesnt_contain_except_specifier(self):
        """Raise when /.travis.yml doesn't contain except specifier."""
        with open(".travis.yml", "w"):
            pass

        run("file", api_token="token", repo="user/repo")
        self.assertThat(sys.stderr.read(),
                        Contains("""Need to have branches:"""))
        self.assertEqual(call(1), sys.exit.call_args_list[0])

    def test_bail_when_needed_except_specifiers_not_in_specifiers(self):
        """Raise when /.travis.yml's branches: except doesn't have our reg."""
        with open(".travis.yml", "w") as travis_yml:
            yaml.dump({
                "branches": {
                    "except": [
                        ""
                    ]
                }
            }, travis_yml)

        run("file", api_token="token", repo="user/repo")
        self.assertThat(sys.stderr.read(),
                        Contains("""Need to have branches:"""))
        self.assertEqual(call(1), sys.exit.call_args_list[0])

    def test_bail_when_not_last_tag_doesnt_start_with_v(self):
        """Raise when last tag doesn't start with v."""
        _write_travis_yml()
        self.last_tag_from_git.return_value = "x0.0.1"
        run("file", api_token="token", repo="user/repo")
        self.assertThat(sys.stderr.read(),
                        Contains("""Release a tag"""))
        self.assertEqual(call(1), sys.exit.call_args_list[0])

    def test_use_patch_by_default_for_empty_body(self):
        """Use level patch by default for empty commit message body."""
        _write_travis_yml()
        self.last_tag_from_git.return_value = "v0.0.1"
        self.last_commit_message_body.return_value = ""
        run("file", api_token="token", repo="user/repo")
        self.call_bumpversion.assert_called_with("patch", ["file"])
        self.assertEqual(call(0), sys.exit.call_args_list[0])

    def test_use_patch_by_default_for_body_with_no_code(self):
        """Use level patch by default commit message body with no code."""
        _write_travis_yml()
        self.last_tag_from_git.return_value = "v0.0.1"
        self.last_commit_message_body.return_value = "Title\n\nBody"
        run("file", api_token="token", repo="user/repo")
        self.call_bumpversion.assert_called_with("patch", ["file"])
        self.assertEqual(call(0), sys.exit.call_args_list[0])

    def test_use_patch_level_for_malformed_bumpversion_code(self):
        """Use level patch when bumpversion code is malformed."""
        _write_travis_yml()
        self.last_tag_from_git.return_value = "v0.0.1"
        self.last_commit_message_body.return_value = "T\n\nbumpversion: mjr"
        run("file", api_token="token", repo="user/repo")
        self.call_bumpversion.assert_called_with("patch", ["file"])
        self.assertEqual(call(0), sys.exit.call_args_list[0])

    def test_complain_for_malformed_bumpversion_code(self):
        """Complain when bumpversion code is malformed."""
        _write_travis_yml()
        self.last_tag_from_git.return_value = "v0.0.1"
        self.last_commit_message_body.return_value = "T\n\nbumpversion: mjr"
        run("file", api_token="token", repo="user/repo")
        self.assertThat(sys.stderr.read(), Contains("""Invalid code mjr"""))

    @parameterized.expand(("major", "minor", "patch"),
                          testcase_func_doc=_format_with_args)
    def test_use_valid_bumpversion_code(self, lvl):
        """Use level {0} when bumpversion code is set to {0}."""
        _write_travis_yml()
        self.last_tag_from_git.return_value = "v0.0.1"
        self.last_commit_message_body.return_value = "T\n\nbumpversion: " + lvl
        run("file", api_token="token", repo="user/repo")
        self.call_bumpversion.assert_called_with(lvl, ["file"])
        self.assertEqual(call(0), sys.exit.call_args_list[0])

    def test_push_commit_and_tags_success(self):
        """Push commit and tags with provided token and repo."""
        _write_travis_yml()
        self.last_tag_from_git.return_value = "v0.0.1"
        self.last_commit_message_body.return_value = ""
        run("file", api_token="token", repo="user/repo")
        self.push_commit_and_tags.assert_called_with("token", "user/repo")
        self.assertEqual(call(0), sys.exit.call_args_list[0])

    def test_push_commit_and_tags_complain_on_failure(self):
        """Push commit and tags with provided token and repo."""
        _write_travis_yml()
        self.last_tag_from_git.return_value = "v0.0.1"
        self.last_commit_message_body.return_value = ""
        error = subprocess.CalledProcessError(1, 1)
        self.push_commit_and_tags.side_effect = error
        run("file", api_token="token", repo="user/repo")
        self.assertThat(sys.stderr.read(), Contains("""Failed to push"""))
        self.assertEqual(call(0), sys.exit.call_args_list[0])
