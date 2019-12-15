from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.modalview import ModalView
from kivymd.theming import ThemableBehavior
from kivymd.uix.behaviors import SpecificBackgroundColorBehavior, RectangularElevationBehavior

Builder.load_string("""
#:import images_path kivymd.images_path

<SelectableItem@OneLineIconListItem>:
    icon: 'android'
    text_color: 0, 0, 0, 1
    on_release: root.callback(root.icon)

    IconLeftWidget:
        icon: root.icon
        theme_text_color: "Custom"
        text_color: root.text_color

<SelectPicker>
    size_hint: (None, None)
    size: dp(284), dp(120)+dp(290)
    pos_hint: {'center_x': .5, 'center_y': .5}
    canvas:

        Color:
            rgb: app.theme_cls.primary_color

        Rectangle:
            size: self.width, dp(120)
            pos: root.pos[0], root.pos[1] + root.height-dp(120)

        Color:
            rgb: app.theme_cls.bg_normal

        Rectangle:
            size: self.width, dp(290)
            pos: root.pos[0], root.pos[1] + root.height-(dp(120)+dp(290))

    MDFlatButton:
        id: close_button
        pos: root.pos[0]+root.size[0]-self.width-dp(10), root.pos[1] + dp(10)
        text: "Close"
        on_release: root.dismiss()

    MDLabel:
        id: title
        font_style: "H5"
        text: "Change theme"
        size_hint: (None, None)
        size: dp(160), dp(50)
        pos_hint: {'center_x': .5, 'center_y': .9}
        theme_text_color: 'Custom'
        text_color: root.specific_text_color

    BoxLayout:
        orientation: 'vertical'
        spacing: dp(10)
        padding: dp(20)

        BoxLayout:
            size_hint_y: None
            height: self.minimum_height

            MDIconButton:
                icon: 'magnify'

            MDTextField:
                id: search_field
                hint_text: 'Search icon'
                on_text: app.set_list_md_icons(self.text, True)

        RecycleView:
            id: rv
            key_viewclass: 'viewclass'
            key_size: 'height'

            RecycleBoxLayout:
                padding: dp(10)
                default_size: None, dp(48)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
""")


class SelectPicker(
    ThemableBehavior,
    FloatLayout,
    ModalView,
    SpecificBackgroundColorBehavior,
    RectangularElevationBehavior,
):
    pass
