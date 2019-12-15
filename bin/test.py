from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory
from kivymd.toast import toast
from kivymd.theming import ThemeManager
from kivymd.uix.useranimationcard import MDUserAnimationCard
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import (
    ILeftBodyTouch, OneLineIconListItem, ThreeLineIconListItem)

from libangelos.policy.portfolio import Portfolio
from libangelos.policy.print import PrintPolicy
from libangelos.document.profiles import (
    PersonProfile, MinistryProfile, ChurchProfile)


"""
PERSON

    PICTURE: picture
    NAME: given_name, [names...], family_name

    ADDRESS: address        ThreeLineIconListItem
    EMAIL: email            OneLineIconListItem
    MOBILE: mobile          OneLineIconListItem
    PHONE: phone            OneLineIconListItem
    LANGUAGE: language      OneLineIconListItem
    SOCIAL MEDIA: social... OneLineIconListItem
    SEX: sex                OneLineIconListItem
    ESTABLISHED: born       OneLineIconListItem

    ID: id                  OneLineIconListItem

    picture = BinaryField(required=False, limit=65536)
    email = EmailField(required=False)
    mobile = StringField(required=False)
    phone = StringField(required=False)
    address = DocumentField(required=False, t=Address)
    language = StringField(required=False, multiple=True)
    social = DocumentField(required=False, t=Social, multiple=True)

    sex = ChoiceField(choices=["man", "woman", "undefined"])
    born = DateField()
    names = StringField(multiple=True)
    family_name = StringField()
    given_name = StringField()
"""

"""
MINISTRY

    PICTURE: picture
    NAME: ministry

    VISION: vision          ThreeLineIconListItem
    ADDRESS: address        ThreeLineIconListItem
    EMAIL: email            OneLineIconListItem
    MOBILE: mobile          OneLineIconListItem
    PHONE: phone            OneLineIconListItem
    SOCIAL MEDIA: social... OneLineIconListItem
    ESTABLISHED: founded    OneLineIconListItem

    ID: id                  OneLineIconListItem

    picture = BinaryField(required=False, limit=65536)
    email = EmailField(required=False)
    mobile = StringField(required=False)
    phone = StringField(required=False)
    address = DocumentField(required=False, t=Address)
    language = StringField(required=False, multiple=True)
    social = DocumentField(required=False, t=Social, multiple=True)

    vision = StringField(required=False)
    ministry = StringField()
    founded = DateField()
"""

"""
CHURCH

    PICTURE: picture
    NAME: city, region, country

    ADDRESS: address
    EMAIL: email
    MOBILE: mobile
    PHONE: phone
    SOCIAL MEDIA: social...
    ESTABLISHED: founded

    ID: id


    picture = BinaryField(required=False, limit=65536)
    email = EmailField(required=False)
    mobile = StringField(required=False)
    phone = StringField(required=False)
    address = DocumentField(required=False, t=Address)
    language = StringField(required=False, multiple=True)
    social = DocumentField(required=False, t=Social, multiple=True)

    founded = DateField()
    city = StringField()
    region = StringField(required=False)
    country = StringField(required=False)
"""


Builder.load_string('''
#:import get_hex_from_color kivy.utils.get_hex_from_color

<ProfileCard@BoxLayout>
    orientation: 'vertical'
    padding: dp(10)
    spacing: dp(10)
    size_hint_y: None
    height: self.minimum_height

    BoxLayout:
        size_hint_y: None
        height: self.minimum_height
        Widget:

        MDRoundFlatButton:
            text: "Free call"
        Widget:

        MDRoundFlatButton:
            text: "Free message"
        Widget:

    OneLineIconListItem:
        text: "Video call"
        IconLeftSampleWidget:
            icon: 'camera-front-variant'

    TwoLineIconListItem:
        text: "Call Viber Out"
        secondary_text: "[color=%s]Advantageous rates for calls[/color]" % get_hex_from_color(app.theme_cls.primary_color)
        IconLeftSampleWidget:
            icon: 'phone'

    TwoLineIconListItem:
        text: "Call over mobile network"
        secondary_text: "[color=%s]Operator's tariffs apply[/color]" % get_hex_from_color(app.theme_cls.primary_color)
        IconLeftSampleWidget:
            icon: 'remote'
''')


class IconLeftButtonListItem(ILeftBodyTouch, MDIconButton):
    pass


class ProfileCard(MDUserAnimationCard):
    """Short summary.

    Parameters
    ----------
    portfolio : Portfolio
        Description of parameter `portfolio`.

    Attributes
    ----------
    __person_build : type
        Description of attribute `__person_build`.
    __ministry_build : type
        Description of attribute `__ministry_build`.
    __church_build : type
        Description of attribute `__church_build`.
    portfolio

    """

    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio
        profile = portfolio.profile

        MDUserAnimationCard.__init__(
            user_name=PrintPolicy.title(self.portfolio),
            path_to_avatar=profile.picture,
            callback=lambda x: None
        )

        if self.portfolio.profile is PersonProfile:
            self.__person_build()
        elif self.portfolio.profile is MinistryProfile:
            self.__ministry_build()
        elif self.portfolio.profile is ChurchProfile:
            self.__church_build()

    def __person_build(self):
        profile = self.portfolio.profile

        line1, line2 = PrintPolicy.address(profile)
        self.__add_threeline(line1, line2, 'map-marker')
        self.__add_oneline(profile.email, 'email-outline')
        self.__add_oneline(profile.mobile, 'cellphone-basic')
        self.__add_oneline(profile.phone, 'phone')
        self.__add_oneline(", ".join(profile.language), 'flag-variant')
        for social in profile.social:
            self.__add_oneline(
                social.service+": "+social.token, 'contact-mail')
        self.__add_oneline(str(profile.sex).upper(), 'human-male-female')
        self.__add_oneline(profile.born, 'calendar')
        self.__add_oneline(profile.entity.id, 'barcode')

    def __ministry_build(self, profile):
        profile = self.portfolio.profile

        self.__add_threeline(profile.vision, '')
        line1, line2 = PrintPolicy.address(profile)
        self.__add_threeline(line1, line2, 'map-marker')
        self.__add_oneline(profile.email, 'email-outline')
        self.__add_oneline(profile.mobile, 'cellphone-basic')
        self.__add_oneline(profile.phone, 'phone')
        for social in profile.social:
            self.__add_oneline(
                social.service+": "+social.token, 'contact-mail')
        self.__add_oneline(profile.founded, 'calendar')
        self.__add_oneline(profile.entity.id, 'barcode')

    def __church_build(self, profile):
        profile = self.portfolio.profile

        line1, line2 = PrintPolicy.address(profile)
        self.__add_threeline(line1, line2, 'map-marker')
        self.__add_oneline(profile.email, 'email-outline')
        self.__add_oneline(profile.mobile, 'cellphone-basic')
        self.__add_oneline(profile.phone, 'phone')
        for social in profile.social:
            self.__add_oneline(
                social.service+": "+social.token, 'contact-mail')
        self.__add_oneline(profile.founded, 'calendar')
        self.__add_oneline(profile.entity.id, 'barcode')

    def __add_oneline(self, text, icon):
        self.box_content.add_widget(OneLineIconListItem(text=text, icon=icon))

    def __add_threeline(self, text, second, icon):
        self.box_content.add_widget(
            ThreeLineIconListItem(text=text, secondary_text=second, icon=icon))


class Example(App):
    theme_cls = ThemeManager()
    theme_cls.primary_palette = 'Teal'
    title = "Example Animation Card"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_animation_card = None

    def build(self):
        def main_back_callback():
            toast('Close card')
        if not self.user_animation_card:
            self.user_animation_card = MDUserAnimationCard(
                user_name="Lion Lion",
                path_to_avatar="./assets/african-lion-951778_1280.jpg",
                callback=main_back_callback)
            self.user_animation_card.box_content.add_widget(
                Factory.ProfileCard())
        self.user_animation_card.open()


Example().run()
