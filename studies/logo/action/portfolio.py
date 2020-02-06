import logging

from kivymd.toast import toast
from libangelos.document.statements import Statement
from libangelos.error import PortfolioAlreadyExists

from studies.logo.misc import ActionABC


class PortfolioUpdateAction(ActionABC):
    """Adding or updating an portfolio."""

    def __init__(self, **kwargs):
        ActionABC.__init__(self, **kwargs)
        self._portfolio = kwargs.get("portfolio", None)

    def start(self):
        """Connect to server and start mail replication."""
        self._async(self._insert(), wait=False)

    async def _insert(self):
        updating = False
        statements = self._portfolio.issuer.to_set() | self._portfolio.owner.to_set()
        try:
            _, _, _ = await self._app.ioc.facade.storage.vault.add_portfolio(self._portfolio)
        except PortfolioAlreadyExists:
            updating = True
            _, _, _ = await self._app.ioc.facade.storage.vault.update_portfolio(self._portfolio)

        try:
            await self._app.ioc.facade.storage.vault.docs_to_portfolio(statements)
        except Exception as e:
            toast("Failed importing/updating portfolio.")
            logging.error(e, exc_info=True)
            return
        if not updating:
            toast("Success importing portfolio.")
        else:
            toast("Success updating portfolio.")

    async def _insert2(self):
        try:
            statements = self._portfolio.issuer.to_set() | self._portfolio.owner.to_set()
            _, _, _ = await self._app.ioc.facade.storage.vault.add_portfolio(self._portfolio)
            await self._app.ioc.facade.storage.vault.docs_to_portfolio(statements)
            toast("Success importing portfolio.")
            return
        except PortfolioAlreadyExists:
            pass

        try:
            statements = self._portfolio.issuer.to_set() | self._portfolio.owner.to_set()
            _, _, _ = await self._app.ioc.facade.storage.vault.update_portfolio(self._portfolio)
            await self._app.ioc.facade.storage.vault.docs_to_portfolio(statements)
            toast("Success updating portfolio.")
            return
        except Exception as e:
            logging.error(e, exc_info=True)

        toast("Failed importing/updating portfolio.")