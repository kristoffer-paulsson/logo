from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ListProperty, DictProperty, StringProperty, BooleanProperty
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineIconListItem, ILeftBodyTouch
from kivymd.uix.selectioncontrol import MDCheckbox

Builder.load_string("""
<-ContentMDDialog>
    orientation: 'vertical'
    padding: dp(15)
    spacing: dp(10)
    text_button_ok: ''
    text_button_cancel: ''

    MDLabel:
        id: title
        text: root.title
        font_style: 'H6'
        halign: 'left' if not root.device_ios else 'center'
        valign: 'top'
        size_hint_y: None
        text_size: self.width, None
        height: self.texture_size[1]

    RecycleView:
        id: content
        key_viewclass: 'viewclass'
        key_size: 'height'

        RecycleBoxLayout:
            padding: dp(10)
            default_size: None, dp(48)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'

    MDSeparator:
        id: sep

    BoxLayout:
        id: box_buttons
        size_hint_y: None
        height: dp(20)
        padding: dp(20), 0, dp(20), 0


BoxLayout:

    Button:
        text: "Example"
        on_press: app.show_dialog()
""")


class CheckboxItem(ILeftBodyTouch, MDCheckbox):
    pass


class CheckboxIconListItem(OneLineIconListItem):
    """List item with a checkbox/radiobutton to the left.

    Attributes
    ----------
    key : str
        Option key code
    active : bool
        Checkbo pre-selection.
    group : str
        Group name for radiobuttons.

    """
    key = StringProperty(None)
    active = BooleanProperty(False)
    group = StringProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._finish_init, 0)

    def _finish_init(self, dt):
        self.add_widget(CheckboxItem(
            id=self.key,
            active=self.active,
            group=self.group
        ))

    def on_release(self):
        box = self.ids._left_container.children[0]
        active = box.active
        if box.group:
            for cb in ToggleButtonBehavior.get_widgets(box.group):
                cb.active = False
        box.active = not active


class ConfirmationDialog(MDDialog):
    """Material Design Confirmation dialog.

    Attributes
    ----------
    options : dict
        Key/value of options to choose from.
    preselected : list
        Keys of pre-selected options.
    group : str
        Group name for radiobuttons, leave blank for checkboxes.
    choosen : list
        Result of the choosen options.

    """
    options = DictProperty({})
    preselected = ListProperty([])
    group = StringProperty(None)
    choosen = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        for opt in self.options:
            self.children[0].ids.content.data.append({
                "viewclass": "CheckboxIconListItem",
                "text": self.options[opt],
                "key": opt,
                "active": (True if opt in self.preselected else False),
                "group": self.group,
                "divider": None,
            })

    def get_choices(self):
        for ic in self.children[0].ids.content.children[0].children:
            cb = ic.ids._left_container.children[0]
            if cb.active:
                self.choosen.append(cb.id)
        return self.choosen
