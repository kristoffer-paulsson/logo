#!/usr/bin/env python
#
# Copyright (c) 2020 by:
# Kristoffer Paulsson <kristoffer.paulsson@talenten.se>
# This file is distributed under the terms of the MIT license.
#
"""Angelos build script."""
import logging
import os
import re
import datetime
import shutil
import subprocess
import sys
import tempfile
from glob import glob
from os import path

from setuptools import setup, Extension, Command as _Command

base_dir = path.abspath(path.dirname(__file__))


class Command(_Command):
    user_options = [
    ]

    def initialize_options(self):
        """Initialize options"""
        pass

    def finalize_options(self):
        """Finalize options"""
        pass


class Translator(Command):
    """Translate texts in the project."""

    HEADER = """# This file was automatically generated by the translator command.\n# Timestamp: {}\n\n"""
    STRING = """{key} = _("{string}")\n"""
    MESSAGE = """#:\nmsgid "{identity}"\nmsgstr "{string}"\n\n"""

    def run(self):
        """Loads the TEXTS and export them as gettext strings for the app."""
        TEXTS = None  # placeholder
        text_import = os.path.join(os.path.abspath(os.curdir), "lib", "logo", "texts.py")
        print("Loading the texts from {}".format(text_import))
        try:
            with open(text_import) as texts:
                imp_global = dict()
                exec(texts.read(), imp_global)
                if isinstance(imp_global, dict):
                    if "TEXTS" in imp_global.keys():
                        TEXTS = imp_global["TEXTS"]
                if not TEXTS:
                    raise ImportError("Failed importing TEXTS")
        except Exception as e:
            logging.error(e, exc_info=True)
            return

        text_export = os.path.join(os.path.abspath(os.curdir), "lib", "logo", "strings.py")
        print("Writing the gettext strings to {}".format(text_export))
        try:
            with open(text_export, "w+") as strings:
                strings.write(self.HEADER.format(datetime.datetime.now()))
                for key in TEXTS:
                    strings.write(self.STRING.format(key=key, string=repr(TEXTS[key])[1:-1]))
        except Exception as e:
            logging.error(e, exc_info=True)

        pot_export = os.path.join(os.path.abspath(os.curdir), "assets", "locales", "messages.pot")
        print("Writing the pot message file to {}".format(pot_export))
        try:
            with open(pot_export, "w+") as strings:
                strings.write(self.HEADER.format(datetime.datetime.now()))
                for key in TEXTS:
                    message = repr(TEXTS[key])[1:-1]
                    strings.write(self.MESSAGE.format(identity=message, string=message))
        except Exception as e:
            logging.error(e, exc_info=True)


class BuildSetup(Command):
    """Preparations and adaptions of building the app."""

    def run(self):
        """Carry out preparations and adaptions."""
        self.run_command("translate")

        if sys.platform == "darwin":
            pass

        if sys.platform == "darwin":
            self.run_command("py2app")
            self.run_command("pkg_dmg")


BUNDLE_NAME = "LogoMessenger"


class PackageDmg(Command):
    """Build a macos dmg image."""

    def run(self):
        self._dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
        self._temp = tempfile.TemporaryDirectory()
        self._bundle = os.path.join(self._temp.name, "bundle")
        installer = BUNDLE_NAME + "Installer"
        target = os.path.join(self._dist, installer) + ".dmg"

        os.mkdir(self._bundle)
        shutil.copytree(
            os.path.join(self._dist, BUNDLE_NAME + ".app"),
            os.path.join(self._bundle, BUNDLE_NAME + ".app")
        )

        subprocess.check_call(
            "hdiutil create {} -ov -volname \"{}\" -fs HFS+ -srcfolder \"{}\"".format(
                os.path.join(self._temp.name, "tmp.dmg"),
                installer,
                self._bundle
            ), cwd=self._temp.name, shell=True
        )

        if os.path.exists(target):
            os.unlink(target)

        subprocess.check_call(
            "hdiutil convert {} -format UDZO -o {}".format(
                os.path.join(self._temp.name, "tmp.dmg"),
                target
            ), cwd=self._temp.name, shell=True
        )
        self._temp.cleanup()


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


with open(os.path.join(base_dir, "README.md")) as desc:
    long_description = desc.read()

with open(os.path.join(base_dir, "version.py")) as version:
    exec(version.read())

# py2app options and datafiles
DATA_FILES = [
    os.path.abspath(os.path.join(os.path.dirname("."),  "assets")),
    os.path.abspath(os.path.join(os.path.dirname("."),  "lib", "logo", "kv")),
]

OPTIONS = {
    # Mitigate from libangelos: dataclasses
    "packages": ",".join([
        "logo", "libangelos", "asyncssh", "msgpack", "kivy", "kivymd", "plyer", "asyncio", "dataclasses",
        "logging", "logging.config"
    ]),
    "iconfile": "./icons/dove.icns",
    "plist": {
        'CFBundleName': BUNDLE_NAME,
        'CFBundleDisplayName': BUNDLE_NAME,
        'CFBundleGetInfoString': "Λόγῳ is a safe messenger client. Logo means \"reason, matter, statement, remark, saying, word.\"",
        'CFBundleIdentifier': "org.thotlm.osx.logo_messenger",
        'CFBundleVersion': __version__,
        'CFBundleShortVersionString': __version__,
        'NSHumanReadableCopyright': u"Copyright © 2019-2020 by Kristoffer Paulsson.",
    }
}

setup(
    cmdclass={
        "make": BuildSetup,
        "translate": Translator,
        "pkg_dmg": PackageDmg
    },
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
    zip_safe=False,
    python_requires="~=3.7",
    install_requires=[
        # First install libangelos manually:
        # pip install git+https://github.com/kristoffer-paulsson/angelos.git@1.0.0b1
        # Build tools requirements
        "cython",
        # Software import requirements
        "docutils; platform_system == 'Windows'",  # Installation of packages in special order not to mess up in Win10
        "pygments; platform_system == 'Windows'",
        "pypiwin32; platform_system == 'Windows'",
        "kivy.deps.sdl2; platform_system == 'Windows'",
        "kivy.deps.glew; platform_system == 'Windows'",
        "kivy~=1.11", "kivymd",
        # Platform specific requirements
        # [Windows|Linux|Darwin]
        "py2app; platform_system == 'Darwin'",
        "py2exe; platform_system == 'Windows'",
    ],
    # packages=["logo"], # Incompatible with py2app
    package_dir={"": "lib"},
    # scripts=glob("bin/*"),  # Incompatible with py2app
    # ext_modules=cythonize(LibraryScanner("lib", globlist, pkgdata, coredata).scan())
    # Py2app and Py2exe specifics
    app=["./bin/prod"],
    data_files=DATA_FILES,
    options={"py2app": OPTIONS, "py2exe": OPTIONS},
    # TODO: Windows version
    # TODO: Linux Gnome version
    # TODO: Linux QT Version
    # TODO: iOS version
    # TODO: Android version
    # TODO: Windows phone version
)
