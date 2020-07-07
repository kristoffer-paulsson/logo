# cython: language_level=3
#
# Copyright (c) 2020 by:
# Kristoffer Paulsson <kristoffer.paulsson@talenten.se>
# This file is distributed under the terms of the MIT license.
#
"""Logo Messenger main entry point."""
import os

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.theming import ThemableBehavior

Builder.load_string("""
#:import Window kivy.core.window.Window
#:import Splash logo.baseclass.splash.Splash
#:import PersonSetupGuide logo.baseclass.setup.PersonSetupGuide
#:import MinistrySetupGuide logo.baseclass.setup.MinistrySetupGuide
#:import ChurchSetupGuide logo.baseclass.setup.ChurchSetupGuide
#:import Main logo.baseclass.main.Main
#:import Malfunction logo.baseclass.malfunction.Malfunction


<Logo>
    Splash
    SetupGuide
    PersonSetupGuide
    MinistrySetupGuide
    ChurchSetupGuide
    Main
    Malfunction
""")

# KV_DIR = f"{os.path.dirname(__file__)}/kv"
KV_DIR = os.environ["LOGO_MESSENGER_KV"]
for kv_file in os.listdir(KV_DIR):
    Builder.load_file(os.path.join(KV_DIR, kv_file))


class Logo(ThemableBehavior, ScreenManager):
    """Main window manager for Logo Messenger."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
