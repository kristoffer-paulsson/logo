# cython: language_level=3
#
# Copyright (c) 2020 by:
# Kristoffer Paulsson <kristoffer.paulsson@talenten.se>
# This file is distributed under the terms of the MIT license.
#
"""User actions related to contacts."""
from logo import strings
from logo.misc import ActionABC
from libangelos.policy.portfolio import PGroup
from libangelos.policy.verify import StatementPolicy


class ContactAction(ActionABC):
    """Base action for single contact actions."""

    def __init__(self, **kwargs):
        ActionABC.__init__(self, **kwargs)
        self._entity = kwargs.get("entity", None)
        self._cognomen = kwargs.get("name", None)

    def _name(self):
        return self._cognomen if self._cognomen else str(self._entity)


class FriendAction(ContactAction):
    """Adding a contact to friends."""

    def start(self):
        self._async(
            self._app.ioc.facade.api.contact.friend(self._entity),
            lambda x: self._flash(strings.TEXT_ACTION_FRIEND % self._name()),
            wait=False
        )


class UnfriendAction(ContactAction):
    """Removing a contact from friends."""

    def start(self):
        self._async(
            self._app.ioc.facade.api.contact.unfriend(self._entity),
            lambda x: self._flash(strings.TEXT_ACTION_UNFRIEND % self._name()),
            wait=False
        )


class FavoriteAction(ContactAction):
    """Adding a contact to favorites."""

    def start(self):
        self._async(
            self._app.ioc.facade.api.contact.favorite(self._entity),
            lambda x: self._flash(strings.TEXT_ACTION_FAVORITE % self._name()),
            wait=False
        )


class UnfavoriteAction(ContactAction):
    """Removing a contact from favorites."""

    def start(self):
        self._async(
            self._app.ioc.facade.api.contact.unfavorite(self._entity),
            lambda x: self._flash(strings.TEXT_ACTION_UNFAVORITE % self._name()),
            wait=False
        )


class BlockAction(ContactAction):
    """Blocking a contact."""

    def start(self):
        self._async(
            self._app.ioc.facade.api.contact.block(self._entity),
            lambda x: self._flash(strings.TEXT_ACTION_BLOCK % self._name()),
            wait=False
        )


class UnblockAction(ContactAction):
    """Unblocking a contact."""

    def start(self):
        self._async(
            self._app.ioc.facade.api.contact.unblock(self._entity),
            lambda x: self._flash(strings.TEXT_ACTION_UNBLOCK % self._name()),
            wait=False
        )


class ContactMassAction(ActionABC):
    """Base action for single contact actions."""

    def __init__(self, **kwargs):
        ActionABC.__init__(self, **kwargs)
        self._content = kwargs.get("content", None)

    def _selected(self):
        entities = set()
        items = []
        for data in self._content.data:
            if data["selected"]:
                entities.add(data["entity"])
                items.append(data)
        return entities, items

    def _remove(self, items):
        for item in items:
            self._content.data.remove(item)
        self._content.refresh_from_data()


class ContactsSelectAllAction(ContactMassAction):
    """Select all contacts in a list."""

    def __init__(self, **kwargs):
        ContactMassAction.__init__(self, **kwargs)

    def start(self):
        for data in self._content.data:
            if not data["selected"]:
                data["selected"] = True
        self._content.refresh_from_data()
        self._flash(strings.TEXT_ACTION_COMPLETE)


class ContactsDeselectAllAction(ContactMassAction):
    """Select all contacts in a list."""

    def __init__(self, **kwargs):
        ContactMassAction.__init__(self, **kwargs)

    def start(self):
        for data in self._content.data:
            if data["selected"]:
                data["selected"] = False
        self._content.refresh_from_data()
        self._flash(strings.TEXT_ACTION_COMPLETE)


class ContactsMassFriendAction(ContactMassAction):
    """Adding selected contacts to friends."""

    def __init__(self, **kwargs):
        ContactMassAction.__init__(self, **kwargs)

    def start(self):
        self.dialog_confirm(
            title=strings.TEXT_DIALOG_PROCEED_TITLE,
            message=strings.TEXT_DIALOG_PROCEED % strings.TEXT_FRIEND.lower(),
            ok=strings.TEXT_CONFIRM,
            cancel=strings.TEXT_CANCEL,
            callback=self.do_friend
        )

    def do_friend(self, click, dialog):
        if click != strings.TEXT_CONFIRM:
            return

        entities, _ = self._selected()

        self._async(
            self._app.ioc.facade.api.contact.friend(*entities),
            lambda x: self._flash(strings.TEXT_ACTION_COMPLETE),
            wait=False
        )


class ContactsMassUnfriendAction(ContactMassAction):
    """Removing selected contacts from friends."""

    def __init__(self, **kwargs):
        ContactMassAction.__init__(self, **kwargs)

    def start(self):
        self.dialog_confirm(
            title=strings.TEXT_DIALOG_PROCEED_TITLE,
            message=strings.TEXT_DIALOG_PROCEED % strings.TEXT_UNFRIEND.lower(),
            ok=strings.TEXT_CONFIRM,
            cancel=strings.TEXT_CANCEL,
            callback=self.do_unfriend
        )

    def do_unfriend(self, click, dialog):
        if click != strings.TEXT_CONFIRM:
            return

        entities, items = self._selected()
        if self._content.parent.parent.name == "friends":
            self._remove(items)

        self._async(
            self._app.ioc.facade.api.contact.unfriend(*entities),
            lambda x: self._flash(strings.TEXT_ACTION_COMPLETE),
            wait=False
        )


class ContactsMassFavoriteAction(ContactMassAction):
    """Adding selected contacts to favorites."""

    def __init__(self, **kwargs):
        ContactMassAction.__init__(self, **kwargs)

    def start(self):
        self.dialog_confirm(
            title=strings.TEXT_DIALOG_PROCEED_TITLE,
            message=strings.TEXT_DIALOG_PROCEED % strings.TEXT_FAVORITE.lower(),
            ok=strings.TEXT_CONFIRM,
            cancel=strings.TEXT_CANCEL,
            callback=self.do_favorite
        )

    def do_favorite(self, click, dialog):
        if click != strings.TEXT_CONFIRM:
            return

        entities, _ = self._selected()

        self._async(
            self._app.ioc.facade.api.contact.favorite(*entities),
            lambda x: self._flash(strings.TEXT_ACTION_COMPLETE),
            wait=False
        )


class ContactsMassUnfavoriteAction(ContactMassAction):
    """Removing selected contacts from favorites."""

    def __init__(self, **kwargs):
        ContactMassAction.__init__(self, **kwargs)

    def start(self):
        self.dialog_confirm(
            title=strings.TEXT_DIALOG_PROCEED_TITLE,
            message=strings.TEXT_DIALOG_PROCEED % strings.TEXT_UNFAVORITE.lower(),
            ok=strings.TEXT_CONFIRM,
            cancel=strings.TEXT_CANCEL,
            callback=self.do_unfavorite
        )

    def do_unfavorite(self, click, dialog):
        if click != strings.TEXT_CONFIRM:
            return

        entities, items = self._selected()
        if self._content.parent.parent.name == "favorites":
            self._remove(items)

        self._async(
            self._app.ioc.facade.api.contact.unfavorite(*entities),
            lambda x: self._flash(strings.TEXT_ACTION_COMPLETE),
            wait=False
        )


class ContactsMassBlockAction(ContactMassAction):
    """Blocking selected contacts."""

    def __init__(self, **kwargs):
        ContactMassAction.__init__(self, **kwargs)

    def start(self):
        self.dialog_confirm(
            title=strings.TEXT_DIALOG_PROCEED_TITLE,
            message=strings.TEXT_DIALOG_PROCEED % strings.TEXT_BLOCK.lower(),
            ok=strings.TEXT_CONFIRM,
            cancel=strings.TEXT_CANCEL,
            callback=self.do_block
        )

    def do_block(self, click, dialog):
        if click != strings.TEXT_CONFIRM:
            return

        entities, items = self._selected()
        self._remove(items)

        self._async(
            self._app.ioc.facade.api.contact.block(*entities),
            lambda x: self._flash(strings.TEXT_ACTION_COMPLETE),
            wait=False
        )


class ContactsMassUnblockAction(ContactMassAction):
    """Unblocking selected contacts."""

    def __init__(self, **kwargs):
        ContactMassAction.__init__(self, **kwargs)

    def start(self):
        self.dialog_confirm(
            title=strings.TEXT_DIALOG_PROCEED_TITLE,
            message=strings.TEXT_DIALOG_PROCEED % strings.TEXT_UNBLOCK.lower(),
            ok=strings.TEXT_CONFIRM,
            cancel=strings.TEXT_CANCEL,
            callback=self.do_unblock
        )

    def do_unblock(self, click, dialog):
        if click != strings.TEXT_CONFIRM:
            return

        entities, items = self._selected()
        self._remove(items)

        self._async(
            self._app.ioc.facade.api.contact.unblock(*entities),
            lambda x: self._flash(strings.TEXT_ACTION_COMPLETE),
            wait=False
        )

class ContactDeleteAction(ContactAction):
    """Deleting one contact and its portfolio."""

    def __init__(self, **kwargs):
        ContactAction.__init__(self, **kwargs)

    def start(self):
        self.dialog_confirm(
            title=strings.TEXT_DIALOG_PROCEED_TITLE,
            message=strings.TEXT_DIALOG_DELETE_CONTACT % self._name(),
            ok=strings.TEXT_CONFIRM,
            cancel=strings.TEXT_CANCEL,
            callback=self.do_delete
        )

    def do_delete(self, click, dialog):
        if click != strings.TEXT_CONFIRM:
            return

        self._async(
            self._app.ioc.facade.api.contact.remove(self._entity),
            lambda x: self.do_terminate(),
            wait=False
        )

    def do_terminate(self):
        self._async(
            self._app.ioc.facade.storage.vault.delete_portfolio(self._entity),
            lambda x: self._flash(strings.TEXT_ACTION_COMPLETE),
            wait=False
        )


class VerifyAction(ContactAction):
    """Adding a contact to friends."""

    def start(self):
        self._async(
            self._verify(),
            lambda x: self._flash("%s is now verified." % self._name()),
            wait=False
        )

    async def _verify(self):
        portfolio = await self._app.ioc.facade.storage.vault.load_portfolio(self._entity, PGroup.VERIFIER)
        statement = StatementPolicy.verified(self._app.ioc.facade.data.portfolio, portfolio)
        await self._app.ioc.facade.storage.vault.docs_to_portfolio(set([statement]))


class TrustAction(ContactAction):
    """Removing a contact from friends."""

    def start(self):
        self._async(
            self._trust(),
            lambda x: self._flash("%s is now trusted." % self._name()),
            wait=False
        )

    async def _trust(self):
        portfolio = await self._app.ioc.facade.storage.vault.load_portfolio(self._entity, PGroup.VERIFIER)
        statement = StatementPolicy.trusted(self._app.ioc.facade.data.portfolio, portfolio)
        await self._app.ioc.facade.storage.vault.docs_to_portfolio(set([statement]))


class ExportAction(ContactAction):
    """Removing a contact from friends."""

    def start(self):
        from ..baseclass.dialogs import PortfolioExporter
        writer = PortfolioExporter()
        writer.load(self._entity)
        writer.open()
        # self._async(
        #    self._export(),
        #    lambda x: self._flash("%s is now exported." % self._name()),
        #    wait=False
        #)

    # async def _export(self):
    #    writer = PortfolioExporter()
    #    writer.load(self._entity)
    #    writer.open()