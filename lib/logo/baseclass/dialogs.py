import logging
import os
import uuid

from kivy.app import App
from kivy.core.clipboard import Clipboard
from kivy.properties import StringProperty, ListProperty, ObjectProperty, Clock
from kivymd.theming import ThemableBehavior
from kivymd.toast import toast
from kivymd.uix.behaviors import BackgroundColorBehavior
from kivymd.uix.dialog import BaseDialog
from kivymd.uix.menu import MDDropdownMenu
from libangelos.document.messages import Mail
from libangelos.helper import Glue
from libangelos.misc import Loop
from libangelos.operation.export import ExportImportOperation
from libangelos.policy.portfolio import PGroup
from libangelos.policy.print import PrintPolicy

from logo import strings
from logo.baseclass.portfolios import PortfolioView


class LogoBaseDialog(BaseDialog):
    title = StringProperty("<Title>")
    left_action_items = ListProperty([])
    right_action_items = ListProperty([])

    def __init__(self, **kwargs):
        BaseDialog.__init__(self, **kwargs)

    def _toolbar_action_dismiss(self):
        return ["chevron-left", lambda x: self.dismiss()]

    # TODO: Make full screen dialogs themeable


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

        self.source = os.path.join(os.environ["LOGO_MESSENGER_ASSETS"], "images", "dove.png")
        self.posted = "{:%c}".format(self.__mail.posted) if self.__mail.posted else ""
        self.reply = self.__mail.reply
        self.subject = self.__mail.subject if self.__mail.subject else ""
        self.body = self.__mail.body if self.__mail.body else ""

    def _toolbar_action_draft(self):
        return ["content-save", lambda x: self.save()]

    def _toolbar_action_save(self):
        return ["send", lambda x: self.send()]

    def _toolbar_action_report(self):
        return ["alert-outline", lambda x: toast(strings.TEXT_MESSAGE_REPORT)]

    def _toolbar_action_reply(self):
        return ["reply", lambda x: self.reply_to()]

    def dropdown(self, anchor):
        return MDDropdownMenu(
            items=[
                {
                    "viewclass": "MDMenuItem",
                    "icon": "reply",
                    "text": strings.TEXT_MESSAGE_REPLY,
                    "callback": self.reply_to,
                }, {
                    "viewclass": "MDMenuItem",
                    "icon": "forward",
                    "text": strings.TEXT_MESSAGE_FORWARD,
                    "callback": self.forward,
                }, {
                    "viewclass": "MDMenuItem",
                    "icon": "share",
                    "text": strings.TEXT_MESSAGE_SHARE,
                    "callback": self.share,
                }, {
                    "viewclass": "MDMenuItem",
                    "icon": "email-plus-outline",
                    "text": strings.TEXT_MESSAGE_COMPOSE,
                    "callback": self.compose,
                }, {
                    "viewclass": "MDMenuItem",
                    "icon": "trash-can-outline",
                    "text": strings.TEXT_MESSAGE_TRASH,
                    "callback": self.trash,
                }
            ],
            width_mult=3).open(anchor)

    def reply_to(self, *largs):
        mail = Mail(nd={
            "owner": self.__mail.issuer,
            "reply": self.__mail.id,
            "subject": "{}: {}".format(
                strings.TEXT_MESSAGE_REPLY, self.__mail.subject if self.__mail.subject else ""),
            "issuer": self._app.ioc.facade.data.portfolio.entity.id
        })
        MessageDialog(MessageDialog.MODE_WRITER, mail, title=strings.TEXT_REPLY).open()
        self.dismiss()

    def forward(self, *largs):
        toast("Implement me!")
        print("Forward")
        # FIXME: Implement me

    def compose(self, *largs):
        mail = Mail(nd={
            "owner": self.__mail.issuer,
            "issuer": self._app.ioc.facade.data.portfolio.entity.id
        })
        MessageDialog(MessageDialog.MODE_WRITER, mail, title=strings.TEXT_MESSAGE_COMPOSE).open()
        self.dismiss()

    def share(self, *largs):
        toast("Implement me!")
        print("Share")
        # FIXME: Implement me

    def report(self, *largs):
        toast("Implement me!")
        print("Report")
        # FIXME: Implement me

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


class PortfolioImporter(LogoBaseDialog):
    id = ""
    title = strings.TEXT_PORTFOLIO_IMPORTER_TITLE
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
            toast(strings.TEXT_PORTFOLIO_IMPORTER_FAILURE)
            logging.exception(e)


class PortfolioExporter(LogoBaseDialog):
    id = ""
    title = strings.TEXT_PORTFOLIO_EXPORTER_TITLE
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
        toast(strings.TEXT_PORTFOLIO_EXPORTER_FAILURE)