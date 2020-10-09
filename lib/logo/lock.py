# cython: language_level=3
#
# Copyright (c) 2018-2020 by Kristoffer Paulsson <kristoffer.paulsson@talenten.se>.
#
# This software is available under the terms of the MIT license. Parts are licensed under
# different terms if stated. The legal terms are attached to the LICENSE file and are
# made available on:
#
#     https://opensource.org/licenses/MIT
#
# SPDX-License-Identifier: MIT
#
# Contributors:
#     Kristoffer Paulsson - initial implementation
#
"""Module string"""
import base64
import getpass
import platform
from abc import ABC, abstractmethod
from subprocess import Popen, PIPE

from angelos.bin.nacl import SecretBox


class BaseKeyLoader(ABC):
    """Key loader base class. Subclass this for different backends."""

    @classmethod
    @abstractmethod
    def _get_key(cls, realm: str, name: str) -> bytes:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def _set_key(cls, realm: str, name: str, key: bytes):
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def _del_key(cls, realm: str, name: str) -> bytes:
        raise NotImplementedError()

    @classmethod
    def new(cls) -> bytes:
        """Generate a new secret."""
        return SecretBox().sk

    @classmethod
    def set(cls, master: bytes, key: bytes = None):
        """Save a key, generate new if none given."""
        if key is None:
            key = cls.new()

        cls._set_key("Λόγῳ", "angelos-conceal", base64.b64encode(key).decode())
        box = SecretBox(key)

        cls._set_key(
            "Λόγῳ", "angelos-masterkey", base64.b64encode(
                box.encrypt(master)).decode())

    @classmethod
    def get(cls) -> bytes:
        """Get the key."""
        key = base64.b64decode(cls._get_key("Λόγῳ", "angelos-conceal"))
        box = SecretBox(key)
        master = base64.b64decode(cls._get_key("Λόγῳ", "angelos-masterkey"))
        master_key = box.decrypt(master)
        return master_key

    @classmethod
    def redo(cls):
        """"""
        cls.set(cls.get())


class DarwinKeyLoader(BaseKeyLoader):
    """Keyloader for the keychain in Darwin/macos."""

    @classmethod
    def _set_key(cls, realm: str, name: str, key: bytes):
        with Popen("security add-generic-password -a{a} -s{s} -w{w}".format(
                a=getpass.getuser(), s=name, w=key), shell=True) as proc:
            if proc.returncode:
                raise RuntimeWarning(
                    "Set key '{}' failed: {}".format(name, proc.returncode))

    @classmethod
    def _get_key(cls, realm: str, name: str) -> bytes:
        with Popen("security find-generic-password -w -a{a} -s{s}".format(
                a=getpass.getuser(), s=name), shell=True, stdout=PIPE) as proc:
            if proc.returncode:
                raise RuntimeWarning(
                    "Get key '{}' failed: {}".format(name, proc.returncode))
            else:
                return proc.stdout.read()

    @classmethod
    def _del_key(cls, realm: str, name: str) -> bytes:
        with Popen("security delete-generic-password -a{a} -s{s}".format(
                a=getpass.getuser(), s=name), shell=True) as proc:
            if proc.returncode:
                raise RuntimeWarning(
                    "Delete key '{}' failed: {}".format(name, proc.returncode))


class PlatformFactory:
    """Factory class for platform independent classes."""

    DARWIN = "Darwin"

    def __init__(self):
        self.__system = platform.system()

    def command_available(self, command: str) -> str:
        """Path to a command if available, else None."""
        with Popen("whereis {}".format(command), shell=True, stdout=PIPE) as proc:
            if proc.returncode:
                raise RuntimeWarning(
                    "Where is '{}' failed: {}".format(command, proc.returncode))
            else:
                path = proc.stdout.read()
                return path if path else None

    def get_key_loader(self):
        """Get class for KeyLoader."""
        if self.__system == self.DARWIN:
            class KeyLoader(DarwinKeyLoader):
                """Darwin implementation."""
                pass
        else:
            class KeyLoader(BaseKeyLoader):
                """No implementation."""
                pass

        return KeyLoader
