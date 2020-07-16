import collections
import gettext
import json
import locale
import os
import pathlib
import sys

from kivy.animation import Animation
from kivy.properties import StringProperty
from kivymd.app import MDApp
from libangelos.automatic import Automatic
from libangelos.facade.facade import Facade
from libangelos.ioc import Container, ContainerAware, Config, Handle
# from libangelos.logger import LogHandler
from libangelos.misc import Misc
from logo.lock import PlatformFactory
from libangelos.ssh.client import ClientsClient
from libangelos.ssh.ssh import SessionManager
from libangelos.utils import Event

from logo.vars import ENV_DEFAULT, ENV_IMMUTABLE, CONFIG_DEFAULT, CONFIG_IMMUTABLE


class Environment:
    """Setup paths and variables for the runtime environment."""

    DEV = "LOGO_MESSENGER_DEV"
    ROOT = "LOGO_MESSENGER_ROOT"
    ASSETS = "LOGO_MESSENGER_ASSETS"
    LOCALES = "LOGO_MESSENGER_LOCALES"
    TMPL = "LOGO_MESSENGER_KV"


    def __init__(self):
        self.__dev = None
        self.__root = None
        self.__assets = None
        self.__locales = None
        self.__tmpl = None

        here = pathlib.Path(__file__)

        if hasattr(sys, "frozen"):
            self.__dev = "prod"
            if sys.frozen == "macosx_app":
                self.__root = here.parents[3]
                self.__assets = self.__root.joinpath("assets")
                self.__locales = self.__assets.joinpath("locales")
                self.__tmpl = self.__root.joinpath("kv")
        else:
            self.__dev = "dev"
            self.__root = here.parents[2]
            self.__assets = self.__root.joinpath("assets")
            self.__locales = self.__assets.joinpath("locales")

    def _setup(self):
        os.environ[self.DEV] = self.__dev
        os.environ[self.ROOT] = str(self.__root)
        os.environ[self.ASSETS] = str(self.__assets)
        os.environ[self.LOCALES] = str(self.__locales)
        if self.__tmpl:
            os.environ[self.TMPL] = str(self.__tmpl)

    def _gettext(self):
        current_locale, _ = locale.getdefaultlocale()
        gettext.translation(
            "messages",
            localedir=os.environ["LOGO_MESSENGER_LOCALES"],
            languages=["en"]
        ).install()

    def setup(self):
        """Run setup for runtime environment."""
        self._setup()
        self._gettext()


Environment().setup()

# Import gettext strings here, after gettext initialization
from logo import strings


class Configuration(Config, Container):
    def __init__(self):
        Container.__init__(self, self.__config())

    def __load(self, filename):
        path = os.path.join(self.auto.dir.root, filename)
        if not os.path.isfile(path):
            return {}
        with open(path) as jc:
            return json.load(jc.read())

    def __config(self):
        return {
            "env": lambda self: collections.ChainMap(
                ENV_IMMUTABLE,
                vars(self.auto),
                self.__load("env.json"),
                ENV_DEFAULT,
            ),
            "config": lambda self: collections.ChainMap(
                CONFIG_IMMUTABLE,
                self.__load("config.json"),
                CONFIG_DEFAULT
            ),
            "client": lambda self: Handle(ClientsClient),
            # "log": lambda self: LogHandler(self.config["logger"]),
            "session": lambda self: SessionManager(),
            "facade": lambda self: Handle(Facade),
            "auto": lambda self: Automatic("Logo"),
            "quit": lambda self: Event(),
        }


class LogoMessenger(ContainerAware, MDApp):
    user_name = StringProperty(strings.TEXT_APP_NAME)
    profile_picture = StringProperty()

    def __init__(self, **kwargs):
        ContainerAware.__init__(self, Configuration())
        MDApp.__init__(self, **kwargs)

    @property
    def key_loader(self):
        return PlatformFactory().get_key_loader()

    def build(self):
        self.theme_cls.primary_palette = "LightGreen"
        self.theme_cls.theme_style = "Dark"

        from logo.logo import Logo

        widget = Logo()
        widget.opacity = 0
        Animation(opacity=2, d=0.5).start(widget)
        return widget

    def on_start(self):
        """Creates a list of items with examples on start screen."""

    async def open_facade(self):
        self.ioc.facade = await Facade.open(self.user_data_dir, self.key_loader.get())
        # TODO: This is a workaround for bug in loading preferences.
        #   self.ioc.facade.data.prefs["NightMode"]
        self.theme_cls.theme_style = "Dark" if Misc.from_ini(
            self.ioc.facade.api.settings.get("Preferences", "NightMode")) else "Light"
