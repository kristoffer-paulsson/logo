import functools
import logging
import os

from kivy.app import App
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, BooleanProperty, Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleDataAdapter, RecycleView
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import TwoLineAvatarListItem, IRightBodyTouch
from kivymd.uix.menu import MDDropdownMenu
from libangelos.misc import Loop

from logo.baseclass.common import Section
from logo.baseclass.dialogs import MessageDialog
from logo import strings
from logo.action.message import SynchronizeMailAction, EmptyTrashAction


class IconRightMenu(IRightBodyTouch, MDIconButton):
    pass


class LogoRecycleViewListItemMixin:
    """List item mixin for recycle view."""
    data = {}
    item_id = ObjectProperty(allownone=True)
    error = NumericProperty(allownone=True)
    tab = StringProperty(allownone=True)
    selected = BooleanProperty(defaultvalue=False)

    def populate(self):
        try:
            self._call("_populate_")
        except Exception as e:
            logging.error(e, exc_info=True)

    def _call(self, name, **kwargs):
        tab = self.data.get("tab", "main")
        method = getattr(self, name + str(tab), None)
        if callable(method):
            method(**kwargs)
        else:
            raise RuntimeError("Method {} not found on {}".format(name + str(tab), str(self)))

    def err(self, e):
        pass

    def clear(self):
        keys = self.data.keys()
        keys += ["text", "secondary_text", "tertiary_text"]

        self.data = {}
        self.selected = False
        self.item_id = None
        self.error = 0
        self.tab = ""

        for key in keys:
            if hasattr(self, key):
                setattr(self, key, None)


class MessageListItem(LogoRecycleViewListItemMixin, TwoLineAvatarListItem):
    """Specific RV ListItem for the message section."""
    source = StringProperty()
    target_id = ObjectProperty()  # issuer/owner

    _app = None

    def __init__(self, **kwargs):
        super(MessageListItem, self).__init__(**kwargs)
        if not MessageListItem._app:
            MessageListItem._app = App.get_running_app()

    def open_letter(self):
        try:
            self._call("_letter_")
        except Exception as e:
            logging.error(e, exc_info=True)

    def _populate_inbox(self):
        info = Loop.main().run(
            self._app.ioc.facade.api.mailbox.get_info_inbox(
                self.data.get("item_id")), wait=True)

        self.data.setdefault("target_id", info[1])  # Issuer
        self.data.setdefault("text", "{:%c}".format(info[3]))  # Posted
        self.data.setdefault("secondary_text", info[2] if info[2] != "n/a" else str(info[1]))  # Sender or Issuer

        source = os.path.join(os.environ["LOGO_MESSENGER_ASSETS"], "images/dove.png")
        self.data.setdefault("source", source)

    def _letter_inbox(self):
        mail = Loop.main().run(
            self._app.ioc.facade.api.mailbox.open_envelope(
                self.item_id), wait=True)

        MessageDialog(MessageDialog.MODE_READER_RECEIVE, mail, title=strings.TEXT_MESSAGE_INBOX_TITLE).open()

    def _populate_outbox(self):
        info = Loop.main().run(
            self._app.ioc.facade.api.mailbox.get_info_outbox(
                self.data.get("item_id")), wait=True)

        self.data.setdefault("target_id", info[1])  # Owner
        self.data.setdefault("text", "{:%c}".format(info[3]))  # Posted
        self.data.setdefault("secondary_text", info[2] if info[2] != "n/a" else str(info[1]))  # Sender or Owner

        source = os.path.join(os.environ["LOGO_MESSENGER_ASSETS"], "images/dove.png")
        self.data.setdefault("source", source)

    def _letter_outbox(self):
        pass

    def _populate_drafts(self):
        info = Loop.main().run(
            self._app.ioc.facade.api.mailbox.get_info_draft(
                self.data.get("item_id")), wait=True)

        self.data.setdefault("target_id", info[1])  # Owner
        self.data.setdefault("text", info[2] if info[2] else "")  # Subject
        self.data.setdefault("secondary_text", info[3] if info[3] else "")  # Receiver

        source = os.path.join(os.environ["LOGO_MESSENGER_ASSETS"], "images/dove.png")
        self.data.setdefault("source", source)

    def _letter_drafts(self):
        mail = Loop.main().run(
            self._app.ioc.facade.api.mailbox.get_draft(
                self.item_id), wait=True)

        MessageDialog(MessageDialog.MODE_WRITER, mail, title=strings.TEXT_DRAFT).open()

    def _populate_read(self):
        info = Loop.main().run(
            self._app.ioc.facade.api.mailbox.get_info_read(
                self.data.get("item_id")), wait=True)

        self.data.setdefault("target_id", info[1])  # Issuer
        self.data.setdefault("text", info[2] if info[2] != "n/a" else str(info[1]))  # Subject or Issuer
        self.data.setdefault("secondary_text", info[3] + " - " + "{:%c}".format(info[4]))  # Sender and Posted

        source = os.path.join(os.environ["LOGO_MESSENGER_ASSETS"], "images/dove.png")
        self.data.setdefault("source", source)

    def _letter_read(self):
        mail = Loop.main().run(
            self._app.ioc.facade.api.mailbox.get_read(
                self.item_id), wait=True)

        MessageDialog(MessageDialog.MODE_READER_RECEIVE, mail, title=strings.TEXT_MESSAGE).open()

    def _populate_trash(self):
        info = Loop.main().run(
            self._app.ioc.facade.api.mailbox.get_info_trash(
                self.data.get("item_id")), wait=True)

        self.data.setdefault("target_id", info[1])  # Issuer
        self.data.setdefault("text", info[2] if info[2] != "n/a" else str(info[1]))  # Subject or Issuer
        self.data.setdefault("secondary_text", info[3] + " - " + "{:%c}".format(info[4]))  # Sender and Posted

        source = os.path.join(os.environ["LOGO_MESSENGER_ASSETS"], "images/dove.png")
        self.data.setdefault("source", source)

    def _letter_trash(self):
        mail = Loop.main().run(
            self._app.ioc.facade.api.mailbox.get_trash(
                self.item_id), wait=True)

        MessageDialog(MessageDialog.MODE_READER_RECEIVE, mail, title=strings.TEXT_MESSAGE_TRASH_TITLE).open()


class LogoRecycleDataAdapter(RecycleDataAdapter):
    """Custom recycle view DataAdapter.

    This adapter will load extra data from the vault at scrolling."""

    def __init__(self, **kwargs):
        super(LogoRecycleDataAdapter, self).__init__(**kwargs)
        self.app = App.get_running_app()

    def refresh_view_attrs(self, index, data_item, view):
        """Wrapper for the view refresher that loads extra envelope data ad-hoc."""
        if "error" not in data_item:
            try:
                view.data = data_item
                view.populate()
            except Exception as e:
                logging.error(e, exc_info=True)
                data_item.setdefault("error", 1)
                view.err(e)

        view.data = data_item
        super(LogoRecycleDataAdapter, self).refresh_view_attrs(index, data_item, view)

    def make_view_dirty(self, view, index):
        """Clean up some custom data from the list item"""
        view.clear()
        super(LogoRecycleDataAdapter, self).make_view_dirty(index, view)


class LogoRecycleView(RecycleView):
    """Custom recycle view that will set the right DataAdapter."""

    def __init__(self, **kwargs):
        kwargs.setdefault("view_adapter", LogoRecycleDataAdapter())
        super(LogoRecycleView, self).__init__(**kwargs)


class MessageSearch(BoxLayout):
    """Message search box logic."""
    pass


class MessageMenu(MDDropdownMenu):
    """Mass selection/deselection and other operations menu."""
    def __init__(self, **kwargs):
        super(MessageMenu, self).__init__(**kwargs)


menu_tab = {
    "inbox": ["sync"],
    "outbox": ["sync"],
    "drafts": [],
    "read": [],
    "trash": ["empty"]
}


class Messages(Section):
    """The messages sub screen."""

    def __init__(self, **kwargs):
        Section.__init__(self, **kwargs)
        self.menus = dict()
        self._app = App.get_running_app()

    def on_pre_enter(self, *args):
        """Prepare menus."""
        self.ids.panel.on_resize()

        def commit(action, tab_name, dt):
            """Selected menu command callback."""
            content = self.ids.get(tab_name).ids.content
            action(content=content).start()

        if not self.menus:
            caller = self.ids.toolbar.ids["right_actions"].children[0]
            for tab in menu_tab.keys():
                menu_items = list()
                for item in menu_tab[tab]:
                    menu_items.append({
                        "viewclass": "MDMenuItem",
                        "icon": menu_context[item][0],
                        "text": menu_context[item][1],
                        "callback": functools.partial(commit, menu_context[item][2], tab)
                    })
                self.menus[tab] = MessageMenu(caller=caller, items=menu_items, width_mult=4)

    def open_menu(self, widget):
        """Open menu for right tab."""
        self.menus[self.ids.panel.ids.tab_manager.current].open()

    def list_inbox(self, page):
        """load all favorite contacts."""
        self.__load_rv(
            self._app.ioc.facade.api.mailbox.load_inbox(),
            page.children[0].ids.content,
            tab=page.name
        )

    def list_outbox(self, page):
        """Load all friend contacts."""
        self.__load_rv(
            self._app.ioc.facade.api.mailbox.load_outbox(),
            page.children[0].ids.content,
            tab=page.name
        )

    def list_drafts(self, page):
        """Load all known contacts."""
        self.__load_rv(
            self._app.ioc.facade.api.mailbox.load_drafts(),
            page.children[0].ids.content,
            tab=page.name
        )

    def list_read(self, page):
        """Load all known contacts from a church network."""
        self.__load_rv(
            self._app.ioc.facade.api.mailbox.load_read(),
            page.children[0].ids.content,
            tab=page.name
        )

    def list_trash(self, page):
        """Load all blocked contacts."""
        self.__load_rv(
            self._app.ioc.facade.api.mailbox.load_trash(),
            page.children[0].ids.content,
            tab=page.name
        )

    @staticmethod
    def __load_rv(coro, content, tab=None, selectable=False):
        """Update the ScrollView with new and changed data."""
        data = content.data
        current = {e["item_id"] for e in data}
        loaded = Loop.main().run(coro, wait=True)

        # Remove from current that is not in loaded
        remove = (current - loaded)
        index = 0
        while index < len(data):
            if data[index]["item_id"] in remove:
                del data[index]
            else:
                index += 1

        # Add unique from loaded to current
        new = (loaded - current)
        for item in loaded:
            if item in new:
                model = {"item_id": item}
                if tab:
                    model["tab"] = tab
                if selectable:
                    model["selected"] = False
                data.append(model)


menu_context = {
    "sync": ("sync", strings.TEXT_SYNCHRONIZE, SynchronizeMailAction),
    "empty": ("trash-can-outline", strings.TEXT_EMPTY, EmptyTrashAction),
}