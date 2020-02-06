from dummy.support import Generate
from kivy.app import App
from kivymd.toast import toast
from libangelos.misc import Loop
from libangelos.operation.setup import SetupPersonOperation
from libangelos.policy.message import EnvelopePolicy, MessagePolicy
from libangelos.task.task import TaskWaitress

from .common import Section

from kivymd.uix.bottomsheet import MDListBottomSheet

from .dialogs import PortfolioImporter, PortfolioExporter


class PortfolioBottomSheet(MDListBottomSheet):

    def __init__(self, **kwargs):
        super(PortfolioBottomSheet, self).__init__(**kwargs)

        for item in (
            ("Import data", lambda x: self.import_portfolio(), "database-import"),
            ("Import QR", lambda x: toast("Implement me!"), "qrcode"),
            ("Export self", lambda x: self.export_portfolio(), "database-export"),
        ):
            self.add_item(item[0], item[1], item[2])

    def import_portfolio(self):
        writer = PortfolioImporter()
        writer.load()
        writer.open()

    def export_portfolio(self):
        writer = PortfolioExporter()
        writer.load()
        writer.open()

class Preferences(Section):
    def open_portfolio_sheet(self):
        PortfolioBottomSheet().open()

    def generate_dummys(self):
        Loop.main().run(self.dummy_run(), wait=False)

    async def dummy_run(self):
        app = App.get_running_app()
        for person in Generate.person_data(20):
            portfolio = SetupPersonOperation.create(person, server=False)
            await app.ioc.facade.storage.vault.add_portfolio(portfolio)

    def generate_mail(self):
        Loop.main().run(self.dummy_mailer(), wait=False)

    async def dummy_mailer(self):
        app = App.get_running_app()
        for person in Generate.person_data():
            portfolio = SetupPersonOperation.create(person, server=False)
            await app.ioc.facade.storage.vault.add_portfolio(portfolio)
            for _ in range(10):
                await app.ioc.facade.api.mailbox.import_envelope(
                    EnvelopePolicy.wrap(
                        portfolio,
                        app.ioc.facade.data.portfolio,
                        MessagePolicy.mail(portfolio, app.ioc.facade.data.portfolio).message(
                            Generate.filename(postfix="."),
                            Generate.lipsum().decode(),
                        ).done(),
                    )
                )

    def contact_sync(self):
        Loop.main().run(
            TaskWaitress().wait_for(App.get_running_app().ioc.facade.task.contact_sync),
            lambda x: toast("Portfolios and contacts synchronized")
        )

    def network_index(self):
        Loop.main().run(
            TaskWaitress().wait_for(App.get_running_app().ioc.facade.task.network_index),
            lambda x: toast("Available networks indexed")
        )