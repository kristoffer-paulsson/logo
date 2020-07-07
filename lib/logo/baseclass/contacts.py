import functools
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior, RecycleDataAdapter
from kivymd.uix.bottomsheet import MDCustomBottomSheet
from kivymd.uix.list import OneLineAvatarIconListItem, OneLineAvatarListItem, OneLineIconListItem
from kivymd.uix.menu import MDDropdownMenu
from libangelos.document.messages import Mail
from libangelos.misc import Loop
from libangelos.policy.portfolio import PGroup
from libangelos.policy.print import PrintPolicy

from logo.baseclass.common import Section
from logo.baseclass.dialogs import MessageDialog
from logo import strings
from logo.action.contact import (
    ContactsSelectAllAction,
    ContactsDeselectAllAction,
    ContactsMassFriendAction,
    ContactsMassUnfriendAction,
    ContactsMassFavoriteAction,
    ContactsMassUnfavoriteAction,
    ContactsMassBlockAction,
    ContactsMassUnblockAction
)


class AvatarContactSheetItem(OneLineAvatarListItem):
    """The avatar of the bottom sheet."""
    source = StringProperty()


class IconContactSheetItem(OneLineIconListItem):
    """An action of the bottom sheet."""
    icon = StringProperty()


class ContactBottomSheetContent(BoxLayout):
    """Bottom sheet content logic."""
    entity = ObjectProperty()
    text = StringProperty()

    def __init__(self, **kwargs):
        super(ContactBottomSheetContent, self).__init__(**kwargs)
        self._app = App.get_running_app()
        Clock.schedule_once(self.finish_init, 0)

    def finish_init(self, dt):
        """Adapt the actions of the bottom sheet based on the entities contact status."""
        self.ids.avatar.source = os.path.join(os.environ["LOGO_MESSENGER_ASSETS"], "images/mask.png")
        favorite, friend, blocked = Loop.main().run(self._app.ioc.facade.api.contact.status(self.entity), wait=True)

        if blocked:
            self.remove_widget(self.ids.message)
            self.remove_widget(self.ids.friend)
            self.remove_widget(self.ids.unfriend)
            self.remove_widget(self.ids.favorite)
            self.remove_widget(self.ids.unfavorite)
            self.remove_widget(self.ids.block)
        else:
            self.remove_widget(self.ids.unblock)
            self.remove_widget(self.ids.delete)

            if friend:
                self.remove_widget(self.ids.friend)
            else:
                self.remove_widget(self.ids.unfriend)

            if favorite:
                self.remove_widget(self.ids.favorite)
            else:
                self.remove_widget(self.ids.unfavorite)
        self.do_layout()

    def compose(self):
        mail = Mail(nd={
            "owner": self.entity,
            "issuer": self._app.ioc.facade.data.portfolio.entity.id
        })
        MessageDialog(MessageDialog.MODE_WRITER, mail, title="Compose new").open()


class ContactListItem(RecycleDataViewBehavior, OneLineAvatarIconListItem):
    """Contact list item used by recycle view"""
    entity = ObjectProperty()
    source = StringProperty()
    selected = BooleanProperty(defaultvalue=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = None

    def show_menu(self):
        """Open the bottom sheet for this list item."""
        MDCustomBottomSheet(
            screen=ContactBottomSheetContent(entity=self.entity, text=self.text),
            animation=True,
            radius_from="top",
            pos_hint={"center_x": .5, "center_y": .5}  # Necessary to center on macOS
        ).open()

    def on_selected(self, instance, value):
        """Update the data."""
        self.data["selected"] = value


class ContactSearch(BoxLayout):
    """Contact search box logic."""
    pass


class ContactRecycleDataAdapter(RecycleDataAdapter):
    """Custom recycle view DataAdapter.

    This adapter will load extra data from the vault at scrolling."""

    def __init__(self, **kwargs):
        super(ContactRecycleDataAdapter, self).__init__(**kwargs)
        self.app = App.get_running_app()

    def refresh_view_attrs(self, index, data_item, view):
        """Wrapper for the view refresher that loads extra entity data ad-hoc."""
        if "text" not in data_item:
            portfolio = Loop.main().run(
                self.app.ioc.facade.storage.vault.load_portfolio(
                    data_item.get("entity"), PGroup.VERIFIER), wait=True)
            data_item.setdefault("text", PrintPolicy.title(portfolio))
            source = os.path.join(os.environ["LOGO_MESSENGER_ASSETS"], "images/mask.png")
            data_item.setdefault("source", source)

        view.data = data_item
        super(ContactRecycleDataAdapter, self).refresh_view_attrs(index, data_item, view)

    def make_view_dirty(self, view, index):
        """Clean up some custom data from the list item"""
        view.selected = False
        view.data = None
        super(ContactRecycleDataAdapter, self).make_view_dirty(index, view)


class ContactRecycleView(RecycleView):
    """Custom recycle view that will set the right DataAdapter."""

    def __init__(self, **kwargs):
        kwargs.setdefault("view_adapter", ContactRecycleDataAdapter())
        super(ContactRecycleView, self).__init__(**kwargs)


class ContactMenu(MDDropdownMenu):
    """Mass selection/deselection and other operations menu."""
    def __init__(self, **kwargs):
        super(ContactMenu, self).__init__(**kwargs)


menu_tab = {
    "favorites": ["select", "deselect", "friend", "unfriend", "unfavorite", "block"],
    "friends": ["select", "deselect", "unfriend", "favorite", "unfavorite", "block"],
    "church": ["select", "deselect", "friend", "unfriend", "favorite", "unfavorite", "block"],
    "all": ["select", "deselect", "friend", "unfriend", "favorite", "unfavorite", "block"],
    "blocked": ["select", "deselect", "unblock"]
}


class Contacts(Section):
    """The contacts sub screen."""

    def __init__(self, **kwargs):
        Section.__init__(self, **kwargs)
        self.menus = dict()

    def on_pre_enter(self, *args):
        """Prepare menus."""
        def commit(action, tab_name, dt):
            """Selected menu command callback."""
            content = self.ids.get(tab_name).ids.content
            action(content=content).start()

        if not self.menus:
            caller = self.ids.toolbar.ids["right_actions"].children[0]
            for tab in menu_tab.keys():
                menu_items = []
                for item in menu_tab[tab]:
                    menu_items.append({
                        "viewclass": "MDMenuItem",
                        "icon": menu_context[item][0],
                        "text": menu_context[item][1],
                        "callback": functools.partial(commit, menu_context[item][2], tab)
                    })
                self.menus[tab] = ContactMenu(caller=caller, items=menu_items, width_mult=4)

    def open_menu(self, widget):
        """Open menu for right tab."""
        self.menus[self.ids.panel.ids.tab_manager.current].open()

    def list_favorites(self, page):
        """load all favorite contacts."""
        self.__load_rv(
            App.get_running_app().ioc.facade.api.contact.load_favorites(),
            page.children[0].ids.content
        )

    def list_friends(self, page):
        """Load all friend contacts."""
        self.__load_rv(
            App.get_running_app().ioc.facade.api.contact.load_friends(),
            page.children[0].ids.content
        )

    def list_church(self, page):
        """Load all known contacts from a church network."""
        pass

    def list_all(self, page):
        """Load all known contacts."""
        self.__load_rv(
            App.get_running_app().ioc.facade.api.contact.load_all(),
            page.children[0].ids.content
        )

    def list_blocked(self, page):
        """Load all blocked contacts."""
        self.__load_rv(
            App.get_running_app().ioc.facade.api.contact.load_blocked(),
            page.children[0].ids.content
        )

    @staticmethod
    def __load_rv(coro, content):
        """Update the ScrollView with new and changed data."""
        data = content.data
        current = {e["entity"] for e in data}
        loaded = Loop.main().run(coro, wait=True)

        # Remove from current that is not in loaded
        remove = (current - loaded)
        index = 0
        while index < len(data):
            if data[index]["entity"] in remove:
                del data[index]
            else:
                index += 1

        # Add unique from loaded to current
        for eid in (loaded - current):
            data.append({"entity": eid, "selected": False})


menu_context = {
    "select": ("checkbox-multiple-marked-outline", strings.TEXT_SELECT_ALL, ContactsSelectAllAction),
    "deselect": ("checkbox-multiple-blank-outline", strings.TEXT_DESELECT_ALL, ContactsDeselectAllAction),
    "friend": ("heart", strings.TEXT_FRIEND, ContactsMassFriendAction),
    "unfriend": ("heart-off", strings.TEXT_UNFRIEND, ContactsMassUnfriendAction),
    "favorite": ("star", strings.TEXT_FAVORITE, ContactsMassFavoriteAction),
    "unfavorite": ("star-off", strings.TEXT_UNFAVORITE, ContactsMassUnfavoriteAction),
    "block": ("alert-outline", strings.TEXT_BLOCK, ContactsMassBlockAction),
    "unblock": ("door", strings.TEXT_UNBLOCK, ContactsMassUnblockAction),
}