import csv
import logging
import os
import uuid

from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView, RecycleDataAdapter
from kivymd.toast import toast
from kivymd.uix.list import OneLineAvatarIconListItem
from libangelos.misc import Loop
from libangelos.policy.portfolio import PGroup
from libangelos.policy.print import PrintPolicy

from logo.baseclass.common import Section
from logo.baseclass.messages import LogoRecycleViewListItemMixin


class NetworkListItem(LogoRecycleViewListItemMixin, OneLineAvatarIconListItem):
    """Specific RV ListItem for the message section."""
    source = StringProperty()

    _app = None

    def __init__(self, **kwargs):
        super(NetworkListItem, self).__init__(**kwargs)
        if not NetworkListItem._app:
            NetworkListItem._app = App.get_running_app()

    def _populate_main(self):
        portfolio = Loop.main().run(
            self._app.ioc.facade.storage.vault.load_portfolio(
                self.data.get("item_id"), PGroup.VERIFIER), wait=True)

        self.data.setdefault("text", PrintPolicy.title(portfolio))  # Posted

        source = os.path.join(os.environ["LOGO_MESSENGER_ASSETS"], "images/dove.png")
        self.data.setdefault("source", source)

    def selection(self):
        portfolio = Loop.main().run(
            self._app.ioc.facade.storage.vault.load_portfolio(
                self.data.get("item_id"), PGroup.VERIFIER), wait=True)

        self._app.ioc.facade.data.client["CurrentNetwork"] = portfolio.entity.id
        toast("%s selected as primary network" % PrintPolicy.title(portfolio))

    def on_selected(self, instance, value):
        """Update the data."""
        self.data["selected"] = value


class LogoSearch(BoxLayout):
    """Contact search box logic."""
    pass


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


class Networks(Section):

    def list_networks(self):
        """Load all blocked contacts."""
        app = App.get_running_app()

        async def load():
            """Load networks from settings and filter out not trusted."""
            networks = set()
            for row in await app.ioc.facade.api.settings.networks():
                if row[1]:
                    networks.add(uuid.UUID(row[0]))

            return networks

        try:
            network_id = set([uuid.UUID(app.ioc.facade.data.client["CurrentNetwork"])])
        except KeyError:
            network_id = set()

        self.__load_rv(
            load(),
            self.ids.network.ids.content,
            selectable=True,
            preselected=network_id
        )

    @staticmethod
    def __load_rv(coro, content, tab=None, selectable=False, preselected=set()):
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
                    model["selected"] = True if item in preselected else False
                data.append(model)