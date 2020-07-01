import logging
import os
import uuid

from kivy.app import App
from kivy.core.clipboard import Clipboard
from kivy.properties import StringProperty, ListProperty, ObjectProperty, Clock
from kivymd.toast import toast
from kivymd.uix.dialog import BaseDialog
from kivymd.uix.menu import MDDropdownMenu
from libangelos.document.messages import Mail
from libangelos.helper import Glue
from libangelos.misc import Loop
from libangelos.operation.export import ExportImportOperation
from libangelos.policy.portfolio import PGroup
from libangelos.policy.print import PrintPolicy

from lib.logo.baseclass.portfolios import PortfolioView


class LogoBaseDialog(BaseDialog):
    title = StringProperty("<Title>")
    left_action_items = ListProperty([])
    right_action_items = ListProperty([])

    def __init__(self, **kwargs):
        BaseDialog.__init__(self, **kwargs)

    def _toolbar_action_dismiss(self):
        return ["chevron-left", lambda x: self.dismiss()]


class MessageDialog(LogoBaseDialog):
    MODE_WRITER = 0
    MODE_READER_SEND = 1
    MODE_READER_RECEIVE = 2

    source = StringProperty(allownone=True)
    target = StringProperty(allownone=True)
    posted = StringProperty(allownone=True)
    reply = ObjectProperty(allownone=True)
    subject = StringProperty(allownone=True)
    body = StringProperty(allownone=True)

    _app = None

    def __init__(self, mode: int, mail: Mail, **kwargs):
        LogoBaseDialog.__init__(self, **kwargs)
        if not MessageDialog._app:
            MessageDialog._app = App.get_running_app()
        self.__mode = mode
        self.__mail = mail
        self.left_action_items.append(self._toolbar_action_dismiss())
        if mode is self.MODE_WRITER:
            self.right_action_items.append(self._toolbar_action_draft())
            self.right_action_items.append(self._toolbar_action_save())
            self.ids.reader.parent.remove_widget(self.ids.reader)
        else:
            self.right_action_items.append(self._toolbar_action_report())
            self.right_action_items.append(self._toolbar_action_reply())
            self.ids.writer.parent.remove_widget(self.ids.writer)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        if self.__mode is self.MODE_WRITER:
            tid = self.__mail.owner
        elif self.__mode is self.MODE_READER_RECEIVE:
            tid = self.__mail.issuer
        elif self.__mode is self.MODE_READER_SEND:
            tid = self._mail.owner

        self.target = PrintPolicy.title(Loop.main().run(
            self._app.ioc.facade.storage.vault.load_portfolio(
                tid, PGroup.VERIFIER), wait=True))

        self.source = os.path.join(os.environ["LOGO_MESSENGER_ASSETS"], "images/dove-128x128.png")
        self.posted = "{:%c}".format(self.__mail.posted) if self.__mail.posted else ""
        self.reply = self.__mail.reply
        self.subject = self.__mail.subject if self.__mail.subject else ""
        self.body = self.__mail.body if self.__mail.body else ""

    def _toolbar_action_draft(self):
        return ["content-save", lambda x: self.save()]

    def _toolbar_action_save(self):
        return ["send", lambda x: self.send()]

    def _toolbar_action_report(self):
        return ["alert-outline", lambda x: print("Report message")]

    def _toolbar_action_reply(self):
        return ["reply", lambda x: self.reply_to()]

    def dropdown(self, anchor):
        return MDDropdownMenu(
            items=[
                {
                    "viewclass": "MDMenuItem",
                    "icon": "reply",
                    "text": "Reply to",
                    "callback": self.reply_to,
                }, {
                    "viewclass": "MDMenuItem",
                    "icon": "forward",
                    "text": "Forward to",
                    "callback": self.forward,
                }, {
                    "viewclass": "MDMenuItem",
                    "icon": "share",
                    "text": "Share with",
                    "callback": self.share,
                }, {
                    "viewclass": "MDMenuItem",
                    "icon": "email-plus-outline",
                    "text": "Compose new",
                    "callback": self.compose,
                }, {
                    "viewclass": "MDMenuItem",
                    "icon": "trash-can-outline",
                    "text": "Trash it",
                    "callback": self.trash,
                }
            ],
            width_mult=3).open(anchor)

    def reply_to(self, *largs):
        mail = Mail(nd={
            "owner": self.__mail.issuer,
            "reply": self.__mail.id,
            "subject": "Reply to: %s" % (self.__mail.subject if self.__mail.subject else ""),
            "issuer": self._app.ioc.facade.data.portfolio.entity.id
        })
        MessageDialog(MessageDialog.MODE_WRITER, mail, title="Reply").open()
        self.dismiss()

    def forward(self, *largs):
        print("Forward")

    def compose(self, *largs):
        mail = Mail(nd={
            "owner": self.__mail.issuer,
            "issuer": self._app.ioc.facade.data.portfolio.entity.id
        })
        MessageDialog(MessageDialog.MODE_WRITER, mail, title="Compose new").open()
        self.dismiss()

    def share(self, *largs):
        print("Share")

    def report(self, *largs):
        print("Report")

    def trash(self, *largs):
        Loop.main().run(self._app.ioc.facade.api.mailbox.move_trash(self.__mail.id), wait=True)
        self.dismiss()

    def send(self):
        """Compile and send message from dialog data."""
        Loop.main().run(self._app.ioc.facade.api.mailbox.send_mail(
            self.__mail, self.subject, self.body, reply=self.reply
        ))
        self.dismiss()

    def save(self):
        """Compile and save message as draft from dialog data."""
        Loop.main().run(self._app.ioc.facade.api.mailbox.save_draft(
            self.__mail, self.subject, self.body, reply=self.reply
        ))
        self.dismiss()


class PortfolioImporter(BaseDialog):
    id = ""
    title = "Portfolio importer"
    data = StringProperty()

    def load(self):
        """Prepare the message composer dialog box."""
        self._app = App.get_running_app()

    def parse(self):
        try:
            portfolio = ExportImportOperation.text_imp(self.ids.data.text)

            pw = PortfolioView()
            pw.load(portfolio)
            pw.open()
            self.dismiss()
        except Exception as e:
            toast("Failed parsing portfolio data.")
            logging.exception(e)


class PortfolioExporter(BaseDialog):
    id = ''
    title = 'Portfolio exporter'
    data = StringProperty()

    def load(self, entity: uuid.UUID=None):
        """Prepare the message composer dialog box."""
        self._app = App.get_running_app()
        if entity:
            portfolio = Glue.run_async(self._app.ioc.facade.storage.vault.load_portfolio(
                entity,
                PGroup.SHARE_MAX_USER))
        else:
            portfolio = Glue.run_async(self._app.ioc.facade.storage.vault.load_portfolio(
                self._app.ioc.facade.data.portfolio.entity.id,
                PGroup.SHARE_MAX_USER))
        self.data = ExportImportOperation.text_exp(portfolio)

    def copy(self):
        Clipboard.copy(self.data)
        toast("Copied portfolio to clipboard.")