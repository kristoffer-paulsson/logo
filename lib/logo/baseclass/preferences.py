from kivy.app import App
from kivymd.toast import toast
from kivymd.uix.bottomsheet import MDListBottomSheet
from angelos.common.misc import Loop
from angelos.lib.task.task import TaskWaitress

from logo import strings
from logo.baseclass.common import Section
from logo.baseclass.dialogs import PortfolioImporter, PortfolioExporter


class PortfolioBottomSheet(MDListBottomSheet):

    def __init__(self, **kwargs):
        super(PortfolioBottomSheet, self).__init__(**kwargs)

        for item in (
                ("Import data", lambda x: self.import_portfolio(), "database-import"),
                ("Import QR", lambda x: toast("Implement me!"), "qrcode"),  # TODO: QR code import
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

    def contact_sync(self):
        Loop.main().run(
            TaskWaitress().wait_for(App.get_running_app().ioc.facade.task.contact_sync),
            lambda x: toast(strings.TEXT_PREFERENCES_SYNCHRO_SUCCESS)
        )

    def network_index(self):
        Loop.main().run(
            TaskWaitress().wait_for(App.get_running_app().ioc.facade.task.network_index),
            lambda x: toast(strings.TEXT_PREFERENCES_NETWORKS_SUCCESS)
        )
