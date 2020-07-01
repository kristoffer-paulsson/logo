#!/usr/bin/env python
#
# Copyright (c) 2020 by:
# Kristoffer Paulsson <kristoffer.paulsson@talenten.se>
# This file is distributed under the terms of the MIT license.
#
"""Angelos build script."""
import distutils.command.build
import os
import re
from glob import glob
from os import path

from setuptools import setup, Extension

base_dir = path.abspath(path.dirname(__file__))


class BuildSetup(distutils.command.build.build):
    """Preparations and adaptions of building the app."""

    def run(self):
        """Carry out preparations and adaptions."""
        distutils.command.build.build.run(self)


class LibraryScanner:
    """Scan directories for Cython *.pyx files and configure extensions to build."""

    def __init__(self, base_path: str, globlist: list = None, pkgdata: dict = None, data: dict = None):
        self.__base_path = base_path
        self.__globlist = globlist if globlist else ["**.pyx"]
        self.__pkgdata = pkgdata if pkgdata else {}
        self.__data = data if data else {
            "compiler_directives": {
                "language_level": 3,
                "embedsignature": True
            }
        }

    def scan(self) -> list:
        """Build list of Extensions to be cythonized."""
        glob_result = list()
        for pattern in self.__globlist:
            glob_path = os.path.join(self.__base_path, pattern)
            glob_result += glob(glob_path, recursive=True)

        extensions = list()
        for module in glob_result:
            package = re.sub("/", ".", module[len(self.__base_path) + 1:-4])
            data = self.__pkgdata[package] if package in self.__pkgdata else {}
            core = {"name": package, "sources": [module]}
            kwargs = {**self.__data, **data, **core}
            extensions.append(Extension(**kwargs))

        return extensions


with open(path.join(base_dir, "README.md")) as desc:
    long_description = desc.read()

with open(path.join(base_dir, "version.py")) as version:
    exec(version.read())

setup(
    cmdclass={"build": BuildSetup},
    name="logo",
    version=__version__,
    license="MIT",
    description="A safe messaging system",
    author=__author__,
    author_email=__author_email__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=__url__,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Topic :: Communications :: Chat",
        "Topic :: Communications :: Email",
        "Topic :: Communications :: File Sharing",
        "Topic :: Religion",
        "Topic :: Security",
    ],
    zip_safe=True,
    python_requires="~=3.7",
    setup_requires=["cython", "pyinstaller"],
    install_requires=[],
    packages=["logo"],
    package_dir={"": "lib"},
    scripts=glob("bin/*"),
    # ext_modules=cythonize(LibraryScanner("lib", globlist, pkgdata, coredata).scan())
)
