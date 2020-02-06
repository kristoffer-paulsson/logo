import collections
import gettext
import json
import locale
import os
import sys

from kivy.animation import Animation
from kivy.properties import StringProperty
from kivymd.app import MDApp
from libangelos.automatic import Automatic
from libangelos.facade.facade import Facade
from libangelos.ioc import Container, ContainerAware, Config, Handle
from libangelos.logger import LogHandler
from libangelos.policy.lock import KeyLoader
from libangelos.ssh.client import ClientsClient
from libangelos.ssh.ssh import SessionManager
from libangelos.utils import Event

from vars import ENV_DEFAULT, ENV_IMMUTABLE, CONFIG_DEFAULT, CONFIG_IMMUTABLE

if getattr(sys, "frozen", False):  # bundle mode with PyInstaller
    os.environ["LOGO_MESSENGER_ROOT"] = sys._MEIPASS
else:
    sys.path.append(os.path.abspath(__file__).split("demos")[0])
    os.environ["LOGO_MESSENGER_ROOT"] = os.path.dirname(os.path.abspath(__file__))
os.environ["LOGO_MESSENGER_ASSETS"] = os.path.join(
    os.environ["LOGO_MESSENGER_ROOT"], f"assets{os.sep}"
)

current_locale, _ = locale.getdefaultlocale()
gettext.translation(
    "messages",
    localedir=os.path.join(os.environ["LOGO_MESSENGER_ASSETS"], "locales/"),
    languages=["en"]
).install()

# Make sure the following line says: "from studies.logo import strings"
from studies.logo import strings


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
            "quit": lambda self: Event(),
        }


class LogoMessenger(ContainerAware, MDApp):
    user_name = StringProperty(strings.TEXT_APP_NAME)
    profile_picture = StringProperty()

    def __init__(self, **kwargs):
        ContainerAware.__init__(self, Configuration())
        MDApp.__init__(self, **kwargs)

        self.theme_cls.primary_palette = "LightGreen"

    @property
    def key_loader(self):
        return KeyLoader

    def build(self):
        from studies.logo.logo import Logo
        widget = Logo()
        widget.opacity = 0
        Animation(opacity=2, d=0.5).start(widget)
        return widget

    def on_start(self):
        """Creates a list of items with examples on start screen."""
        pass

    async def open_facade(self):
        self.ioc.facade = await Facade.open(self.user_data_dir, self.key_loader.get())
