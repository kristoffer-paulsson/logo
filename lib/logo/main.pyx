# cython: language_level=3
#
# Copyright (c) 2019 by:
# Kristoffer Paulsson <kristoffer.paulsson@talenten.se>
# This file is distributed under the terms of the MIT license.
#
"""Logo Messenger package configuration."""
import os
import collections
import json
import logging

from kivy.animation import Animation
from kivy.core.window import Window

from kivymd.app import MDApp

from libangelos.ioc import Container, ContainerAware, Config, Handle
from libangelos.utils import Util, Event
from libangelos.const import Const
from libangelos.policy.lock import KeyLoader
from libangelos.logger import LogHandler
from libangelos.ssh.ssh import SessionManager
from libangelos.ssh.client import ClientsClient
from libangelos.facade.facade import Facade
from libangelos.automatic import Automatic
from libangelos.prefs import Preferences
from logo.worker import Worker
from libangelos.helper import Glue

from logo.uix.common import RootWidget, SplashScreen
from logo.uix.wizard import SetupScreen
from logo.uix.navigation import AppScreen
from logo.vars import ENV_DEFAULT, ENV_IMMUTABLE, CONFIG_DEFAULT, CONFIG_IMMUTABLE


class Configuration(Config, Container):
    def __init__(self):
        Container.__init__(self, self.__config())

    def __load(self, filename):
        try:
            with open(os.path.join(self.auto.dir.root, filename)) as jc:
                return json.load(jc.read())
        except FileNotFoundError:
            return {}

    def __config(self):
        return {
            "env": lambda self: collections.ChainMap(
                ENV_IMMUTABLE,
                vars(self.auto),
                self.__load("env.json"),
                ENV_DEFAULT,
            ),
            "config": lambda self: collections.ChainMap(
                CONFIG_IMMUTABLE, self.__load("config.json"), CONFIG_DEFAULT
            ),
            "client": lambda self: Handle(ClientsClient),
            "log": lambda self: LogHandler(self.config["logger"]),
            "session": lambda self: SessionManager(),
            "facade": lambda self: Handle(Facade),
            "auto": lambda self: Automatic("Logo"),
            "prefs": lambda self: Preferences(
                self.facade, self.config["prefs"]),
            "quit": lambda self: Event(),
        }


class LogoMessenger(ContainerAware, MDApp):
    title = "Logo Messenger"
    main_widget = None

    def __init__(self, **kwargs):
        ContainerAware.__init__(self, Configuration())
        MDApp.__init__(self, **kwargs)
        # self._worker = Worker("client", self.ioc, executor=0)

        self.theme_cls.primary_palette = "LightGreen"
        self.theme_cls.accent_palette = "Green"
        self.theme_cls.theme_style = "Light"
        Window.clearcolor = self.theme_cls.bg_normal

    def build(self):
        self.main_widget = RootWidget.create()
        self.main_widget.add_widget(SplashScreen.create(name="splash"))
        return self.main_widget

    def on_start(self):
        anim = Animation(progress=1000, duration=3)

        vault_file = Util.path(self.user_data_dir, Const.CNL_VAULT)

        if os.path.isfile(vault_file):
            Glue.run_async(self.open_facade())
            # self._worker.run_coroutine(self.open_facade())
            next = lambda a, w: self.main_widget.switch_to(  # noqa E731
                AppScreen.create(name="app"))
            Glue.run_async(self.ioc.prefs.load())
        else:
            next = lambda a, w: self.main_widget.switch_to(  # noqa E731
                SetupScreen.create(name="setup"))

        anim.bind(on_complete=next)
        anim.start(self.main_widget.current_screen)

    def on_stop(self):
        logging.warning("Do on_stop exit")
        # self._worker.run_coroutine(self._worker.exit())
        # result = asyncio.run_coroutine_threadsafe(
        #    , self._worker.loop)
        # print(result)

    async def open_facade(self):
        self.ioc.facade = await Facade.open(self.user_data_dir, KeyLoader.get())

    def do_stop(self):
        raise KeyboardInterrupt()
