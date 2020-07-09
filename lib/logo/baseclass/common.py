from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.list import IRightBodyTouch, ILeftBodyTouch, ILeftBody
from kivymd.uix.selectioncontrol import MDCheckbox, MDSwitch
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDToolbar


class LToolbar(MDToolbar):
    pass


class LCenterLabel(MDLabel):
    """Centered MDLabel"""
    pass


class LForm(BoxLayout):
    """BoxLayout with padding and spacing for form elements."""
    pass


class LFormHorizontal(BoxLayout):
    """Boxlayout that layouts elements horizontally."""
    pass


class LTextField(MDTextField):
    """Layouted text field."""
    pass


class LFormTitle(LCenterLabel):
    pass


class LChoiceGroup(BoxLayout):
    pass


class LCheckbox(MDCheckbox):
    pass


class LScrollContentItem(GridLayout):
    """Item whose content is centered and scrollable by LScrollLayout.

    The LScrollContentItem is a holder of multiple objects to be centered and
    scrolled. The centering is simulated by calculating the padding every time
    the width is changed.

    Attributes
    ----------
    rel_max : int
        Max relative width the layout can have.
    rel_min : type
        Min relative width before margins are fading away.

    """
    rel_max = NumericProperty(dp(800))
    rel_min = NumericProperty(dp(400))

    def __init__(self, **kwargs):
        super(LScrollContentItem, self).__init__(**kwargs)

        self.rel_max = kwargs.get("rel_max", dp(800))
        self.rel_min = kwargs.get("rel_min", dp(400))

    def on_width(self, instance, value):
        if self.rel_max < value:
            padding = max(value * .125, (value - self.rel_max) / 2)
        elif self.rel_min < value:
            padding = min(value * .125, (value - self.rel_min) / 2)
        elif self.rel_min < value:
            padding = (value - self.rel_min) / 2
        else:
            padding = 0

        self.padding[0] = self.padding[2] = padding


class LScrollLayout(FloatLayout):
    """Layout that let centered content be scrolled.

    Attributes
    ----------
    template : str
        The kivy template of the widget.
    content : Widget
        The widget to be centered and scrolled (LScrollLayout).

    """

    def __init__(self, **kwargs):
        super(LScrollLayout, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        content = self.children[0]
        if isinstance(content, LScrollContentItem):
            self.remove_widget(content)
            self.ids.content.add_widget(content)


class LIconRightCheckbox(IRightBodyTouch, MDCheckbox):
    """Checkbox selection control for MDList.

    Use inside OneLineRightIconListItem and others.
    """
    pass


class LIconRightSwitch(IRightBodyTouch, MDSwitch):
    """Switch selection control for MDList.

    Use inside OneLineRightIconListItem and others.
    """
    pass


class LIconLeftWidget(ILeftBody, MDIcon):
    pass


class Section(Screen):
    """App section."""
    nav_drawer = ObjectProperty()
    title = StringProperty()

    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
