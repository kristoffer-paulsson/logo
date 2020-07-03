import os

from kivy.app import App
from kivy.properties import StringProperty, Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivymd.theming import ThemableBehavior
from kivymd.uix.list import OneLineIconListItem

from logo import strings


class ContentNavigationDrawer(BoxLayout):
    pass

class NavigationItem(OneLineIconListItem):
    icon = StringProperty()
    goto = StringProperty()


class Main(ThemableBehavior, Screen):
    def __init__(self, **kwargs):
        super(Main, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        app.user_name = "[b]{e.given_name} {e.family_name}[/b]".format(
            e=app.ioc.facade.data.portfolio.entity)
        app.profile_picture = os.path.join(os.environ["LOGO_MESSENGER_ASSETS"], "images/mask.png")

        def goto(item):
            self.ids.scr_mngr.current = item.goto
            self.ids.nav_drawer.set_state("close")

        for item in (
                ("monitor-dashboard", "dashboard", strings.TEXT_SECTION_DASHBOARD),
                ("email-outline", "messages", strings.TEXT_SECTION_MESSAGES),
                ("contact-mail-outline", "contacts", strings.TEXT_SECTION_CONTACTS),
                ("folder-account-outline", "documents", strings.TEXT_SECTION_DOCUMENTS),
                ("web", "networks", strings.TEXT_SECTION_NETWORKS),
                ("face-profile", "profile", strings.TEXT_PROFILE),
                ("settings", "preferences", strings.TEXT_SECTION_PREFERENCES),
        ):
            self.ids.content_drawer.ids.box_item.add_widget(
                NavigationItem(
                    text=item[2],
                    icon=item[0],
                    goto=item[1],
                    on_release=goto
                )
            )
