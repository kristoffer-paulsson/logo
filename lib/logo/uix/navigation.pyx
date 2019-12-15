# cython: language_level=3
#
# Copyright (c) 2019 by:
# Kristoffer Paulsson <kristoffer.paulsson@talenten.se>
# This file is distributed under the terms of the MIT license.
#
"""Navigation widgets and logic."""
from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.navigationdrawer import NavigationDrawerIconButton
from logo.uix.common import MainWidgetBase, WidgetFactoryBehavior

dashboard_KV = """
<Dashboard>
    name: 'dashboard'
"""


class Dashboard(MainWidgetBase, WidgetFactoryBehavior):
    template = dashboard_KV

    name = StringProperty("dashboard")
    title = StringProperty("Dashboard")


messages_KV = """
<Messages>
    name: 'messages'

    MDBottomNavigation
        id: panel
        tab_display_mode: 'icons'

        MDBottomNavigationItem:
            name: 'inbox'
            text: "Inbox"
            icon: 'inbox-arrow-up'
            # on_pre_enter: root.get_inbox()
            # on_leave: print('On leave')

        MDBottomNavigationItem:
            name: 'outbox'
            text: "Outbox"
            icon: 'inbox-arrow-down'
            # on_pre_enter: root.get_outbox()
            # on_leave: print('On leave')

        MDBottomNavigationItem:
            name: 'drafts'
            text: "Drafts"
            icon: 'file-multiple'
            # on_pre_enter: root.get_drafts()
            # on_leave: print('On leave')

        MDBottomNavigationItem:
            name: 'read'
            text: "Read"
            icon: 'email-open'
            # on_pre_enter: root.get_read()
            # on_leave: print('On leave')

        MDBottomNavigationItem:  # Button to empty trash
            name: 'trash'
            text: "Trash"
            icon: 'delete'
            # on_pre_enter: root.get_trash()
            # on_leave: print('On leave')
"""


class Messages(MainWidgetBase, WidgetFactoryBehavior):
    template = messages_KV

    name = StringProperty("messages")
    title = StringProperty("Messages")


contacts_KV = """
<ContactSearch@BoxLayout>:
    orientation: 'vertical'
    spacing: dp(10)
    padding: dp(20)

    BoxLayout:
        size_hint_y: None
        height: self.minimum_height

        MDIconButton:
            icon: 'magnify'

        MDTextField:
            id: search_field
            hint_text: 'Search in ' + self.parent.parent.parent.name
            # on_text: app.set_list_md_icons(self.text, True)

    RecycleView:
        id: rv
        key_viewclass: 'viewclass'
        key_size: 'height'

        RecycleBoxLayout:
            padding: dp(10)
            default_size: None, dp(48)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'

<Contacts>
    name: 'contacts'

    MDBottomNavigation:
        id: panel
        tab_display_mode: 'icons'

        MDBottomNavigationItem:
            name: 'favorites'
            text: 'Favorites'
            icon: 'star'
            # on_pre_enter: root.list_favorites()
            # on_leave: print('On leave')
            ContactSearch:

        MDBottomNavigationItem:
            name: 'friends'
            text: 'Friends'
            icon: 'heart'
            # on_pre_enter: root.list_friends()
            # on_leave: print('On leave')
            ContactSearch:

        MDBottomNavigationItem:
            name: 'church'
            text: 'Church'
            icon: 'church'
            # on_pre_enter: root.list_church()
            # on_leave: print('On leave')
            ContactSearch:

        MDBottomNavigationItem:
            name: 'all'
            text: 'All'
            icon: 'account-multiple'
            # on_pre_enter: root.list_all()
            # on_leave: print('On leave')
            ContactSearch:

        MDBottomNavigationItem:
            name: 'blocked'
            text: 'Blocked'
            icon: 'block-helper'
            # on_pre_enter: root.list_blocked()
            # on_leave: print('On leave')
            ContactSearch:
"""


class Contacts(MainWidgetBase, WidgetFactoryBehavior):
    template = contacts_KV

    name = StringProperty("contacts")
    title = StringProperty("Contacts")


portfolios_KV = """
<Portfolios>
    name: 'portfolios'
"""


class Portfolios(MainWidgetBase, WidgetFactoryBehavior):
    template = portfolios_KV

    name = StringProperty("portfolios")
    title = StringProperty("Portfolios")


documents_KV = """
<Documents>
    name: 'documents'
"""


class Documents(MainWidgetBase, WidgetFactoryBehavior):
    template = documents_KV

    name = StringProperty("documents")
    title = StringProperty("Documents")


networks_KV = """
<Networks>
    name: 'networks'
"""


class Networks(MainWidgetBase, WidgetFactoryBehavior):
    template = networks_KV

    name = StringProperty("networks")
    title = StringProperty("Networks")


profile_KV = """
<Profile>
    name: 'profile'
"""


class Profile(MainWidgetBase, WidgetFactoryBehavior):
    template = profile_KV

    name = StringProperty("profile")
    title = StringProperty("Profile")


preferences_KV = """
#:import LIconRightSwitch logo.uix.common.LIconRightSwitch

<Preferences>
    name: 'preferences'

    free_dark_mode: free_dark_mode.__self__

    ScrollView:
        do_scroll_x: False
        MDList:
            id: prefs
            OneLineRightIconListItem:
                text: "Night mode"
                LIconRightSwitch:
                    id: free_dark_mode
                    on_active: root.pref_dark_mode(self.active)

"""


class Preferences(MainWidgetBase, WidgetFactoryBehavior):
    template = preferences_KV

    name = StringProperty("preferences")
    title = StringProperty("Preferences")

    free_dark_mode = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Preferences, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        app.ioc.prefs.load()

    def pref_dark_mode(self, active):
        app = App.get_running_app()
        mode = "Dark" if active else "Light"
        app.theme_cls.theme_style = mode
        app.ioc.prefs.free_dark_mode = mode


ASKV = """
#:import FadeTransition kivy.uix.screenmanager.FadeTransition

<AppScreen>:
    id: main

    toolbar: toolbar.__self__
    scr_mngr: scr_mngr.__self__
    nav_drawer: nav_drawer.__self__

    NavigationLayout:
        id: nav_layout

        MDNavigationDrawer:
            id: nav_drawer
            drawer_logo: f'{environ["LOGO_ASSETS"]}icons/dove-1024.png'

        FloatLayout:
            id: float_box

            BoxLayout:
                id: box_for_manager
                orientation: 'vertical'

                MDToolbar:
                    id: toolbar
                    title: root.title
                    md_bg_color: root.theme_cls.primary_color
                    background_palette: 'Primary'
                    background_hue: '500'
                    elevation: 10
                    left_action_items: [['menu', lambda x: root.ids.nav_layout.toggle_nav_drawer()]]
                    # right_action_items:
                    #    [['dots-vertical', lambda x: root.open_context_menu_source_code(toolbar)]] \
                    #    if scr_mngr.current != "previous" else []

                ScreenManager:
                    id: scr_mngr
                    transition: FadeTransition()
                    # on_current: root.set_source_code_file()

                    # Screen:
                    #    name: 'previous'
                    #
                    #    FloatLayout:
                    #
                    #        Image:
                    #           source: f'{environ["LOGO_ASSETS"]}icons/dove-1024.png'
                    #            opacity: .3
"""  # noqa E501


class AppScreen(MainWidgetBase, WidgetFactoryBehavior):
    toolbar = ObjectProperty(None)
    scr_mngr = ObjectProperty(None)
    nav_drawer = ObjectProperty(None)

    template = ASKV

    title = "Logo Messenger"
    data = {
        "dashboard": {
            "factory": Dashboard,
            "icon": "monitor-dashboard",
            "object": None,
        },
        "messages": {
            "factory": Messages,
            "icon": "email-outline",
            "object": None,
        },
        "contacts": {
            "factory": Contacts,
            "icon": "contact-mail",
            "object": None,
        },
        "portfolios": {
            "factory": Portfolios,
            "icon": "briefcase-check",
            "object": None,
        },
        "documents": {
            "factory": Documents,
            "icon": "folder-account",
            "object": None,
        },
        "networks": {
            "factory": Networks,
            "icon": "domain",
            "object": None,
        },
        "profile": {
            "factory": Profile,
            "icon": "face-profile",
            "object": None,
        },
        "preferences": {
            "factory": Preferences,
            "icon": "settings",
            "object": None,
        }
    }

    def __init__(self, **kwargs):
        super(AppScreen, self).__init__(**kwargs)

    def set_chevron_menu(self):
        self.toolbar.left_action_items = [
            ["menu", lambda x: self.nav_drawer.toggle_nav_drawer()]
        ]

    def set_title_toolbar(self, title):
        """Set string title in MDToolbar for the whole application."""
        self.toolbar.title = title

    def show_screen(self, screen):
        """"""
        self.scr_mngr.current = screen.name
        self.toolbar.title = screen.title

    def on_pre_enter(self, *args):
        """Initiates the ScreenManager and its screens."""
        def init_screen(screen_name, *args):
            klass = self.data[screen_name]['factory']
            object = klass.create()
            self.data[screen_name]['object'] = object
            self.scr_mngr.add_widget(object)

            self.nav_drawer.add_widget(
                NavigationDrawerIconButton(
                    text=object.title,
                    icon=self.data[screen_name]['icon'],
                    on_release=lambda x: self.show_screen(object)
                )
            )

        for screen in self.data.keys():
            Clock.schedule_once(partial(init_screen, str(screen)), 0)

    def on_enter(self, *args):
        self.scr_mngr.current = "dashboard"
