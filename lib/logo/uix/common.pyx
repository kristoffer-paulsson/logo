# cython: language_level=3
#
# Copyright (c) 2019 by:
# Kristoffer Paulsson <kristoffer.paulsson@talenten.se>
# This file is distributed under the terms of the MIT license.
#
"""Main screen widgets."""
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import BoundedNumericProperty, NumericProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.theming import ThemableBehavior
from kivymd.uix.label import MDLabel
from kivymd.uix.list import IRightBodyTouch
from kivymd.uix.selectioncontrol import MDCheckbox, MDSwitch


class MainWidgetBase(Screen, ThemableBehavior):
    def __init__(self, **kwargs):
        super(MainWidgetBase, self).__init__(**kwargs)


class WidgetFactoryBehavior:
    template = ""

    @classmethod
    def create(cls, **kwargs):
        Builder.load_string(cls.template)
        return cls(**kwargs)


Builder.load_string("""<LIconRightCheckbox>""")


class LIconRightCheckbox(IRightBodyTouch, MDCheckbox):
    """Checkbox selection control for MDList.

    Use inside OneLineRightIconListItem and others.
    """
    pass


Builder.load_string("""<LIconRightSwitch>""")


class LIconRightSwitch(IRightBodyTouch, MDSwitch):
    """Switch selection control for MDList.

    Use inside OneLineRightIconListItem and others.
    """
    pass


Builder.load_string("""
<LCenterLabel>:
    halign: 'justify'
    padding: dp(16), dp(16)
    markup: True
    font_style: 'Body1'
    theme_text_color: 'Primary'
    size_hint_y: None
    height: self.texture_size[1]
""")


class LCenterLabel(MDLabel):
    pass


LSCIKV = """
<LScrollContentItem>:
    cols: 1
    size_hint_y: None
    height: self.minimum_height
"""


class LScrollContentItem(GridLayout, WidgetFactoryBehavior):
    """Item whoose content is centered and scrollable by LScrollLayout.

    The LScrollContentItem is a holder of multiple objects to be centeered and
    scrolled. The centering is simulated by calculating the padding every time
    the width is changed.

    Attributes
    ----------
    rel_max : int
        Max relative width the layout can have.
    rel_min : type
        Min relativa width before margins are fading away.

    """
    template = LSCIKV
    rel_max = NumericProperty(dp(800))
    rel_min = NumericProperty(dp(400))

    def __init__(self, **kwargs):
        super(LScrollContentItem, self).__init__(**kwargs)

        self.rel_max = kwargs.get('rel_max', dp(800))
        self.rel_min = kwargs.get('rel_min', dp(400))

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


LSLKV = """
<LScrollLayout>:
    content: content
    ScrollView:
        id: content
        do_scroll_x: False
        bar_width: 10
        bar_color: root.theme_cls.primary_color
        bar_color_acrive: root.theme_cls.accent_color
        effect_cls: "DampedScrollEffect"
        scroll_type: ['bars']
"""


class LScrollLayout(FloatLayout, WidgetFactoryBehavior):
    """Layout that let centered content be scrolles.

    Attributes
    ----------
    template : str
        The kivy template of the widget.
    content : Widget
        The widget to be centered and scrolled (LScrollLayout).

    """
    template = LSLKV
    content = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LScrollLayout, self).__init__(**kwargs)
        self.ids.content.add_widget(kwargs.get('content', None))


RWKV = """
#:import NoTransition kivy.uix.screenmanager.NoTransition

<RootWidget>
    id: scr_mngr
    transition: NoTransition()
    clearcolor: root.theme_cls.bg_normal
    # canvas:
    #    Color:
    #        rgba: root.theme_cls.bg_normal
    #    Rectangle:
    #        size: self.size
    #        pos: self.pos
"""


class RootWidget(ScreenManager, WidgetFactoryBehavior, ThemableBehavior):
    template = RWKV


MSKV = """
#:import environ os.environ

<SplashScreen>:

    BoxLayout:
        orientation: 'vertical'
        size_hint: .5, .5
        size_hint_min: dp(200), dp(200)
        pos_hint: {'center_y': .618, 'center_x': .5}

        Image:
            id: logo_icon
            keep_ration: True
            allow_stretch: True
            source: f'{environ["LOGO_ASSETS"]}icons/dove-1024.png'
            canvas:
                Color:
                    rgba: root.theme_cls.primary_color
                Line:
                    cap: 'none'
                    width: min(self.width, self.height) * .0145
                    circle: (self.center_x, self.center_y, \
                    (min(self.width, self.height)*.919) / 2, 0, \
                    root.progress * .360)
"""


class SplashScreen(MainWidgetBase, WidgetFactoryBehavior):
    template = MSKV
    progress = BoundedNumericProperty(0, min=0, max=1000)

    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)

    def on_progress(self, instance, value):
        image = self.children[0].children[0]
        self.progress = value
        image.canvas.ask_update()
