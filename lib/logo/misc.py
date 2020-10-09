# cython: language_level=3
#
# Copyright (c) 2019 by:
# Kristoffer Paulsson <kristoffer.paulsson@talenten.se>
# This file is distributed under the terms of the MIT license.
#
"""User actions related to contacts."""
from abc import ABC

from kivy.app import App
from kivymd.toast import toast
from kivymd.uix.dialog import MDDialog
from angelos.common.misc import Loop

from logo import strings


class ActionABC(ABC):
    """An action is an event or operation that happens on application level.

    An action should be user-initiated and carry out a certain set of
    business logic that may require several steps of interaction with the user.
    """

    def __init__(self, **kwargs):
        self._app = App.get_running_app()
        self._no_flash = kwargs.get("no_flash", False)

    def start(self):
        """Action execution entry-point.

        Should be implemented on the final action.
        """
        raise NotImplementedError()

    def _flash(self, text):
        if not self._no_flash:
            toast(text)

    def _async(self, coro, callback=None, wait=True):
        Loop.main().run(coro, callback, wait)

    def dialog_confirm(self, title, message, callback=lambda x, y: None, size=(.5, .5),
                       ok=strings.TEXT_OK, cancel=strings.TEXT_CANCEL):
        """Show a confirmation dialog"""
        MDDialog(
            title=title,
            text=message,
            events_callback=callback,
            text_button_ok=ok,
            text_button_cancel=cancel,
            size_hint=size,
            pos_hint={"center_x": .5, "center_y": .5}  # Necessary to center on macOS
        ).open()
