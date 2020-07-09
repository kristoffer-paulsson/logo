import pprint

from kivy.app import App
from kivymd.uix.dialog import BaseDialog
from kivymd.uix.label import MDLabel

from logo import strings
from logo.action.portfolio import PortfolioUpdateAction

# TODO: Translate first when portdolios are implemented

class DocView(MDLabel):
    pass


class PortfolioView(BaseDialog):
    id = ""
    title = strings.TEXT_PORTFOLIO_DIALOG_TITLE

    def load(self, portfolio):
        """Prepare the message composer dialog box."""
        self._app = App.get_running_app()
        self._portfolio = portfolio

        issuer, owner = portfolio.to_sets()
        for doc in issuer | owner:
            dw = DocView()
            dw.text = doc.__class__.__name__ + "\n" + pprint.pformat(
                doc.export_yaml())
            self.ids.docs.add_widget(dw)

    def save(self):
        PortfolioUpdateAction(portfolio=self._portfolio).start()
        self.dismiss()


