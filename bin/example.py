from kivymd.app import MDApp
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout


LIPSUM = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""  # noqa E501


Builder.load_string("""

<LCenterLabel@MDLabel>:
    halign: 'justify'
    padding: dp(16), dp(16)
    markup: True
    font_style: 'Body1'
    theme_text_color: 'Primary'
    size_hint_y: None
    height: self.texture_size[1]

<LScrollContentItem>:
    cols: 1
    size_hint_y: None
    height: self.minimum_height


<LScrollLayout>:
    content: content
    ScrollView:
        id: content
        do_scroll_x: False
        bar_width: 10
        bar_color: app.theme_cls.primary_color
        bar_color_acrive: app.theme_cls.accent_color
        effect_cls: "DampedScrollEffect"
        scroll_type: ['bars']


<ExampleContent@LScrollContentItem>:
    LCenterLabel:
        text: app.label_text + app.label_text
    LCenterLabel:
        text: app.label_text + app.label_text
    Widget
""")


class LScrollContentItem(GridLayout):
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


class LScrollLayout(FloatLayout):
    content = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LScrollLayout, self).__init__(**kwargs)
        self.ids.content.add_widget(kwargs.get('content', None))


class Example(MDApp):
    title = "Dialogs"
    label_text = LIPSUM

    def build(self):
        self.theme_cls.primary_palette = "LightGreen"
        self.theme_cls.accent_palette = "Green"
        self.theme_cls.theme_style = "Dark"
        return Factory.LScrollLayout(content=Factory.ExampleContent())


Example().run()
