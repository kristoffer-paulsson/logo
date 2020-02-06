# cython: language_level=3
#
# Copyright (c) 2020 by:
# Kristoffer Paulsson <kristoffer.paulsson@talenten.se>
# This file is distributed under the terms of the MIT license.
#
"""User actions related to contacts."""
import logging
import uuid
from typing import Awaitable

from libangelos.policy.portfolio import Portfolio, PGroup
from libangelos.starter import Starter

from studies.logo import strings
from studies.logo.misc import ActionABC


class ContactAction(ActionABC):
    """Base action for single contact actions."""

    def __init__(self, **kwargs):
        ActionABC.__init__(self, **kwargs)


class SynchronizeMailAction(ContactAction):
    """Adding a contact to friends."""

    def start(self):
        """Connect to server and start mail replication."""
        self._async(self.connect())
        # try:
        #     network_id = uuid.UUID(self._app.ioc.facade.data.client["CurrentNetwork"])
        #     self.connect_network(network_id)
        # except (KeyError, ValueError) as e:
        #     self._flash("No network configured.")
        #     logging.warning(e, exc_info=True)

    async def connect(self):
        try:
            network_id = uuid.UUID(self._app.ioc.facade.data.client["CurrentNetwork"])
            host = await self._app.ioc.facade.storage.vault.load_portfolio(network_id, PGroup.SHARE_MIN_COMMUNITY)
            connection, client = await Starter().clients_client(self._app.ioc.facade.data.portfolio, host, ioc=self._app.ioc)
            self._flash("Success connecting to network.")
            await self.synchronize(client)
        except (KeyError,) as e:
            self._flash("No primary network set.")
            logging.error(e, exc_info=True)
        except Exception as e:
            self._flash("Connection failed.")
            logging.error(e, exc_info=True)

    async def synchronize(self, client):
        await client.mail()

    def connect_network(self, network_id: uuid.UUID) -> Awaitable:
        """Open connection to a network."""
        host = self._async(self._app.ioc.facade.storage.vault.load_portfolio(network_id, PGroup.SHARE_MIN_COMMUNITY))
        connection, client = self._async(self._open_connection(host), self._connection_callback, wait=False)

    async def _open_connection(self, host: Portfolio):
        return await Starter().clients_client(
            self._app.ioc.facade.data.portfolio, host, ioc=self._app.ioc
        )

    def _connection_callback(self, future: Awaitable) -> None:
        """Will start replication and show appropriate snackbar based on connection status"""
        if future.cancelled():
            self._flash("Connection cancelled.")
        elif future.done():
            exc = future.exception()
            if exc:
                logging.error(exc, exc_info=True)
                self._flash("Connection failed.")
            else:
                _, client = future.result()
                self._async(client.mail())
                self._flash("Success connecting to network.")


class EmptyTrashAction(ContactAction):
    """Adding a contact to friends."""

    def start(self):
        self._async(
            self._app.ioc.facade.api.mailbox.empty_trash(),
            lambda x: self._flash(strings.TEXT_ACTION_EMPTY),
            wait=False
        )
