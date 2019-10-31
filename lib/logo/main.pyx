# import .boot

import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.factory import Factory
from kivymd.theming import ThemeManager


Builder.load_string('''
<ExampleFileManager@BoxLayout>
    orientation: 'vertical'
    spacing: dp(5)
    MDToolbar:
        id: toolbar
        title: app.title
        left_action_items: [['menu', lambda x: None]]
        elevation: 10
        md_bg_color: app.theme_cls.primary_color
    FloatLayout:
        MDRoundFlatIconButton:
            text: "Open manager"
            icon: "folder"
            pos_hint: {'center_x': .5, 'center_y': .6}
            on_release: app.file_manager_open()
''')


class LogoMessenger(App):
    theme_cls = ThemeManager()
    theme_cls.primary_palette = 'LightGreen'
    title = "Logo Messenger"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.manager = None

    def build(self):
        return Factory.ExampleFileManager()
