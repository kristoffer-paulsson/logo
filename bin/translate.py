"""
pygettext.py -d messages -o assets/locales/messages.pot studies/logo/strings.py
"""
import argparse
import logging

import os
import sys

sys.path.append(os.path.join(os.path.abspath(os.curdir), "studies/logo"))

from texts import TEXTS

HEADER = """
"""

MESSAGE = """{key} = _("{string}")\n"""


class Translator:
    """Take all texts from the Logo Messenger python/cython/kivy files and export messages.pot"""

    def __init__(self):
        self.process = None

    def parser(self):
        parser = argparse.ArgumentParser()
        return parser

    def escaper(self, text: str):
        for key in Translator.ESC.keys():
            text.replace(key, Translator.ESC[key])
        return text

    def output(self):
        try:
            with open(os.path.join(os.path.abspath(os.curdir), "studies/logo/strings.py"), "w+") as strings:
                strings.write(HEADER)
                for key in TEXTS:
                    strings.write(MESSAGE.format(key=key, string=repr(TEXTS[key])[1:-1]))
        except Exception as e:
            logging.error(e, exc_info=True)

    def run(self):
        self.output()


if __name__ == "__main__":
    Translator().run()
