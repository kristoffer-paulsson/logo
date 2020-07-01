import os

from kivy.animation import Animation
from kivy.app import App
from kivy.properties import BoundedNumericProperty
from kivy.uix.screenmanager import Screen
from kivymd.theming import ThemableBehavior
from libangelos.const import Const
from libangelos.misc import Loop
from libangelos.utils import Util


class Splash(ThemableBehavior, Screen):
    progress = BoundedNumericProperty(0, min=0, max=1000)

    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.__goto = "setup"

    def on_progress(self, instance, value):
        image = self.children[0].children[0]
        self.progress = value
        image.canvas.ask_update()

    def on_pre_enter(self):
        anim = Animation(progress=1000, duration=3)
        anim.on_start = self.__prepare
        anim.on_complete = self.__start
        anim.start(self)

    def __prepare(self, x):
        app = App.get_running_app()
        vault_file = Util.path(app.user_data_dir, Const.CNL_VAULT)

        if os.path.isfile(vault_file):
            e = Loop.main().run(app.open_facade(), wait=True)
            if not isinstance(e, Exception):
                self.__goto = "home"
            else:
                self.__goto = "malfunction"

    def __start(self, x):
        self.parent.current = self.__goto
