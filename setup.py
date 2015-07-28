# /setup.py
#
# Installation and setup script for travis-bump-version
#
# See /LICENCE.md for Copyright information
"""Installation and setup script for travis-bump-version."""

from setuptools import find_packages
from setuptools import setup

setup(name="travis-bump-version",
      version="0.0.1",
      description="Bump version files on travis builds",
      long_description_markdown_filename="README.md",
      author="Sam Spilsbury",
      author_email="smspillaz@gmail.com",
      url="http://github.com/polysquare/travis-runner",
      classifiers=["Development Status :: 3 - Alpha",
                   "Programming Language :: Python :: 2",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 3.1",
                   "Programming Language :: Python :: 3.2",
                   "Programming Language :: Python :: 3.3",
                   "Programming Language :: Python :: 3.4",
                   "Intended Audience :: Developers",
                   "Topic :: Software Development :: Build Tools",
                   "License :: OSI Approved :: MIT License"],
      license="MIT",
      keywords="development linters",
      packages=find_packages(exclude=["tests"]),
      install_requires=["pyaml", "bumpversion"],
      extras_require={
          "green": ["nose-parameterized",
                    "testtools",
                    "six",
                    "setuptools-green"],
          "polysquarelint": ["polysquare-setuptools-lint>=0.0.19"],
          "upload": ["setuptools-markdown"]
      },
      entry_points={
          "console_scripts": [
              "travis-bump-version=travisbumpversion.main:main"
          ]
      },
      test_suite="nose.collector",
      zip_safe=True,
      include_package_data=True)
