# cython: language_level=3
#
# Copyright (c) 2018-2019 by:
# Kristoffer Paulsson <kristoffer.paulsson@talenten.se>
# This file is distributed under the terms of the MIT license.
#
"""Module docstring"""
import datetime

import libnacl
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.picker import MDDatePicker
from libangelos.const import Const
from libangelos.document.entities import Person, Ministry, Church
from libangelos.error import FieldRequiredNotSet
from libangelos.facade.facade import Facade
from libangelos.helper import Glue
from libangelos.operation.setup import SetupMinistryOperation, SetupPersonOperation, SetupChurchOperation
from libangelos.policy.lock import KeyLoader
from libangelos.policy.types import PersonData, MinistryData, ChurchData
from logo.uix.common import MainWidgetBase, WidgetFactoryBehavior
from logo.uix.navigation import AppScreen

COUNTRIES = {'Afghanistan': 'AF', 'Åland Islands': 'AX', 'Albania': 'AL', 'Algeria': 'DZ', 'American Samoa': 'AS',
             'Andorra': 'AD', 'Angola': 'AO', 'Anguilla': 'AI', 'Antarctica': 'AQ', 'Antigua And Barbuda': 'AG',
             'Argentina': 'AR', 'Armenia': 'AM', 'Aruba': 'AW', 'Australia': 'AU', 'Austria': 'AT', 'Azerbaijan': 'AZ',
             'Bahamas': 'BS', 'Bahrain': 'BH', 'Bangladesh': 'BD', 'Barbados': 'BB', 'Belarus': 'BY', 'Belgium': 'BE',
             'Belize': 'BZ', 'Benin': 'BJ', 'Bermuda': 'BM', 'Bhutan': 'BT', 'Bolivia': 'BO',
             'Bosnia And Herzegovina': 'BA', 'Botswana': 'BW', 'Bouvet Island': 'BV', 'Brazil': 'BR',
             'British Indian Ocean Territory': 'IO', 'Brunei Darussalam': 'BN', 'Bulgaria': 'BG', 'Burkina Faso': 'BF',
             'Burundi': 'BI', 'Cambodia': 'KH', 'Cameroon': 'CM', 'Canada': 'CA', 'Cape Verde': 'CV',
             'Cayman Islands': 'KY', 'Central African Republic': 'CF', 'Chad': 'TD', 'Chile': 'CL', 'China': 'CN',
             'Christmas Island': 'CX', 'Cocos (Keeling) Islands': 'CC', 'Colombia': 'CO', 'Comoros': 'KM',
             'Congo': 'CG', 'Congo, Democratic Republic': 'CD', 'Cook Islands': 'CK', 'Costa Rica': 'CR',
             'Cote D\'Ivoire': 'CI', 'Croatia': 'HR', 'Cuba': 'CU', 'Cyprus': 'CY', 'Czech Republic': 'CZ',
             'Denmark': 'DK', 'Djibouti': 'DJ', 'Dominica': 'DM', 'Dominican Republic': 'DO', 'Ecuador': 'EC',
             'Egypt': 'EG', 'El Salvador': 'SV', 'Equatorial Guinea': 'GQ', 'Eritrea': 'ER', 'Estonia': 'EE',
             'Ethiopia': 'ET', 'Falkland Islands (Malvinas)': 'FK', 'Faroe Islands': 'FO', 'Fiji': 'FJ',
             'Finland': 'FI', 'France': 'FR', 'French Guiana': 'GF', 'French Polynesia': 'PF',
             'French Southern Territories': 'TF', 'Gabon': 'GA', 'Gambia': 'GM', 'Georgia': 'GE', 'Germany': 'DE',
             'Ghana': 'GH', 'Gibraltar': 'GI', 'Greece': 'GR', 'Greenland': 'GL', 'Grenada': 'GD', 'Guadeloupe': 'GP',
             'Guam': 'GU', 'Guatemala': 'GT', 'Guernsey': 'GG', 'Guinea': 'GN', 'Guinea-Bissau': 'GW', 'Guyana': 'GY',
             'Haiti': 'HT', 'Heard Island And Mcdonald Islands': 'HM', 'Holy See (Vatican City State)': 'VA',
             'Honduras': 'HN', 'Hong Kong': 'HK', 'Hungary': 'HU', 'Iceland': 'IS', 'India': 'IN', 'Indonesia': 'ID',
             'Iran': 'IR', 'Iraq': 'IQ', 'Ireland': 'IE', 'Isle Of Man': 'IM', 'Israel': 'IL', 'Italy': 'IT',
             'Jamaica': 'JM', 'Japan': 'JP', 'Jersey': 'JE', 'Jordan': 'JO', 'Kazakhstan': 'KZ', 'Kenya': 'KE',
             'Kiribati': 'KI', 'Korea (North)': 'KP', 'Korea (South)': 'KR', 'Kosovo': 'XK', 'Kuwait': 'KW',
             'Kyrgyzstan': 'KG', 'Laos': 'LA', 'Latvia': 'LV', 'Lebanon': 'LB', 'Lesotho': 'LS', 'Liberia': 'LR',
             'Libyan Arab Jamahiriya': 'LY', 'Liechtenstein': 'LI', 'Lithuania': 'LT', 'Luxembourg': 'LU',
             'Macao': 'MO', 'Macedonia': 'MK', 'Madagascar': 'MG', 'Malawi': 'MW', 'Malaysia': 'MY', 'Maldives': 'MV',
             'Mali': 'ML', 'Malta': 'MT', 'Marshall Islands': 'MH', 'Martinique': 'MQ', 'Mauritania': 'MR',
             'Mauritius': 'MU', 'Mayotte': 'YT', 'Mexico': 'MX', 'Micronesia': 'FM', 'Moldova': 'MD', 'Monaco': 'MC',
             'Mongolia': 'MN', 'Montserrat': 'MS', 'Morocco': 'MA', 'Mozambique': 'MZ', 'Myanmar': 'MM',
             'Namibia': 'NA', 'Nauru': 'NR', 'Nepal': 'NP', 'Netherlands': 'NL', 'Netherlands Antilles': 'AN',
             'New Caledonia': 'NC', 'New Zealand': 'NZ', 'Nicaragua': 'NI', 'Niger': 'NE', 'Nigeria': 'NG',
             'Niue': 'NU', 'Norfolk Island': 'NF', 'Northern Mariana Islands': 'MP', 'Norway': 'NO', 'Oman': 'OM',
             'Pakistan': 'PK', 'Palau': 'PW', 'Palestinian Territory, Occupied': 'PS', 'Panama': 'PA',
             'Papua New Guinea': 'PG', 'Paraguay': 'PY', 'Peru': 'PE', 'Philippines': 'PH', 'Pitcairn': 'PN',
             'Poland': 'PL', 'Portugal': 'PT', 'Puerto Rico': 'PR', 'Qatar': 'QA', 'Reunion': 'RE', 'Romania': 'RO',
             'Russian Federation': 'RU', 'Rwanda': 'RW', 'Saint Helena': 'SH', 'Saint Kitts And Nevis': 'KN',
             'Saint Lucia': 'LC', 'Saint Pierre And Miquelon': 'PM', 'Saint Vincent And The Grenadines': 'VC',
             'Samoa': 'WS', 'San Marino': 'SM', 'Sao Tome And Principe': 'ST', 'Saudi Arabia': 'SA', 'Senegal': 'SN',
             'Serbia': 'RS', 'Montenegro': 'ME', 'Seychelles': 'SC', 'Sierra Leone': 'SL', 'Singapore': 'SG',
             'Slovakia': 'SK', 'Slovenia': 'SI', 'Solomon Islands': 'SB', 'Somalia': 'SO', 'South Africa': 'ZA',
             'South Georgia And The South Sandwich Islands': 'GS', 'Spain': 'ES', 'Sri Lanka': 'LK', 'Sudan': 'SD',
             'Suriname': 'SR', 'Svalbard And Jan Mayen': 'SJ', 'Swaziland': 'SZ', 'Sweden': 'SE', 'Switzerland': 'CH',
             'Syrian Arab Republic': 'SY', 'Taiwan, Province Of China': 'TW', 'Tajikistan': 'TJ', 'Tanzania': 'TZ',
             'Thailand': 'TH', 'Timor-Leste': 'TL', 'Togo': 'TG', 'Tokelau': 'TK', 'Tonga': 'TO',
             'Trinidad And Tobago': 'TT', 'Tunisia': 'TN', 'Turkey': 'TR', 'Turkmenistan': 'TM',
             'Turks And Caicos Islands': 'TC', 'Tuvalu': 'TV', 'Uganda': 'UG', 'Ukraine': 'UA',
             'United Arab Emirates': 'AE', 'United Kingdom': 'GB', 'United States': 'US',
             'United States Minor Outlying Islands': 'UM', 'Uruguay': 'UY', 'Uzbekistan': 'UZ', 'Vanuatu': 'VU',
             'Venezuela': 'VE', 'Viet Nam': 'VN', 'Virgin Islands, British': 'VG', 'Virgin Islands, U.S.': 'VI',
             'Wallis And Futuna': 'WF', 'Western Sahara': 'EH', 'Yemen': 'YE', 'Zambia': 'ZM',
             'Zimbabwe': 'ZW'}  # noqa E501

Builder.load_string("""
<PersonSetupGuide@Screen>:
    MDBottomNavigation
        id: entity
        tab_display_mode: 'icons'
        MDBottomNavigationItem:
            name: 'info'
            text: "Info"
            icon: 'information-outline'
            GridLayout:
                cols: 1
                orientation: 'vertical'
                size_hint_x: None
                width: root.width
                padding: '25dp'
                spacing: '25dp'
                valign: 'top'
                MDLabel:
                    font_style: 'H3'
                    theme_text_color: 'Primary'
                    text: "Welcome"
                    halign: 'justify'
                    valign: 'top'
                    height: self.texture_size[1]
                MDLabel:
                    font_style: 'Body1'
                    theme_text_color: 'Primary'
                    text: root.label_intro
                    markup: True
                    halign: 'justify'
                    valign: 'top'
                    height: self.texture_size[1]
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    spacing: '25dp'
                    MDRaisedButton:
                        text: "I agree"
                        on_release: entity.current = 'identity'
                    MDFlatButton:
                        text: "Decline"
                        on_release: app.stop()
        MDBottomNavigationItem:
            name: 'identity'
            text: "Person"
            icon: 'account-outline'
            BoxLayout:
                orientation: 'vertical'
                size_hint_x: None
                width: root.width
                padding: '25dp'
                spacing: '25dp'
                valign: 'top'
                MDTextField:
                    id: given_name
                    hint_text: "Given name"
                    helper_text: "Your legal first name"
                    helper_text_mode: "persistent"
                    required: True
                    multiline: False
                    color_mode: 'custom'
                    valign: 'top'
                MDTextField:
                    id: names
                    hint_text: "Names"
                    helper_text: "Your full name (given + middle names)"
                    helper_text_mode: "persistent"
                    required: True
                    multiline: False
                    color_mode: 'custom'
                    valign: 'top'
                MDTextField:
                    id: family_name
                    hint_text: "Family name"
                    helper_text: "Your legal family name"
                    helper_text_mode: "persistent"
                    required: True
                    multiline: False
                    color_mode: 'custom'
                    valign: 'top'
                MDLabel:
                    font_style: 'Body1'
                    theme_text_color: 'Hint'
                    text: root.label_gender
                    markup: True
                    halign: 'justify'
                    valign: 'top'
                GridLayout:
                    cols: 3
                    MDLabel:
                        text: 'Woman'
                        halign: 'center'
                        theme_text_color: 'Hint'
                    MDLabel:
                        text: 'Man'
                        halign: 'center'
                        theme_text_color: 'Hint'
                    MDLabel:
                        text: 'Undefined'
                        halign: 'center'
                        theme_text_color: 'Hint'
                    MDCheckbox:
                        id: woman
                        group: 'gender'
                    MDCheckbox:
                        id: man
                        group: 'gender'
                    MDCheckbox:
                        id: 3rd
                        group: 'gender'
                BoxLayout:
                    orientation: 'horizontal'
                    spacing: '25dp'
                    valign: 'top'
                    MDTextField:
                        id: born
                        hint_text: "Date of birth"
                        helper_text: "(YYYY-MM-DD)"
                        helper_text_mode: "persistent"
                        required: True
                        multiline: False
                        color_mode: 'custom'
                        valign: 'top'
                    MDRaisedButton:
                        text: "Date"
                        on_release: root.born_datepicker()
                        valign: 'top'
                MDRaisedButton:
                    text: "Next"
                    on_release: root.validate()
            BoxLayout:
        MDBottomNavigationItem:
            name: 'confirm'
            text: "Confirm"
            icon: 'shield-check-outline'
            BoxLayout:
                orientation: 'vertical'
                size_hint_x: None
                width: root.width
                padding: '25dp'
                spacing: '25dp'
                valign: 'top'
                MDLabel:
                    font_style: 'H3'
                    theme_text_color: 'Primary'
                    text: "Confirmation"
                    markup: True
                    halign: 'justify'
                    valign: 'top'
                MDLabel:
                    font_style: 'Body2'
                    theme_text_color: 'Primary'
                    text: root.compilation
                    markup: True
                    halign: 'justify'
                    valign: 'top'
                MDLabel:
                    font_style: 'Body1'
                    theme_text_color: 'Primary'
                    text: root.label_confirm
                    markup: True
                    halign: 'justify'
                    valign: 'top'
                MDRaisedButton:
                    text: "Confirm"
                    on_release: root.confirm(app)
            BoxLayout:

""")  # noqa E501

P_LABEL_INTRO = """
You have just installed the Logo Messenger™ app, which is a client for the Angelos network. This network is a community for Christians as well as non-believers, which enables safe and secure communication.

This community emphasizes friendliness, honesty, and security. Therefore the focus is on privacy and verifiability instead of anonymity!

You need to create a digital identity that represents your person by completing the form in this setup guide. This guide will generate a unique identity for your person, which is known to the network as an Entity document of type Person. [i]This information can not be changed later![/i]

[b]Legalese[/b]
Truthfulness is a requirement. False identifications are forbidden!
"""  # noqa E501

P_LABEL_NAME = """
[size=32sp]Name[/size]

The name is very important for other people to know who you are. We ask that you'll be completely truthful about this.
"""  # noqa E501

P_LABEL_NAME_INVALID = """
The names specified is either incomplete or your given name is not mentioned in the names field!
"""  # noqa E501

P_LABEL_GENDER = """
What is your biological sex?
[size=12sp]Others need to know if you are a man or a woman. Only if you don't know, you may choose undefined.[/size]
"""  # noqa E501

P_LABEL_GENDER_INVALID = """
There is not gender set!
"""  # noqa E501

P_LABEL_BIRTH = """
[size=32sp]Date of birth[/size]

Your date of birth is needed.
"""  # noqa E501

P_LABEL_CONFIRM = """
[b]Legalese[/b]
The information you have provided in this registration form must be material facts. This information is presented to other participants as an identity when you engage with them on the Angelos network. Falsification of material facts implies misrepresentation or deceit!

You confirm that all the information you have specified is truthful and correct!
"""  # noqa E501

P_LABEL_CONFIRM_INVALID = """
The information you have specified is either invalid or incomplete. Please review the form again!
"""  # noqa E501


class PersonSetupGuide(MainWidgetBase, WidgetFactoryBehavior):
    entity = Person()
    confirmed = False
    label_intro = P_LABEL_INTRO
    label_name = P_LABEL_NAME
    label_gender = P_LABEL_GENDER
    label_birth = P_LABEL_BIRTH
    label_confirm = P_LABEL_CONFIRM
    compilation = StringProperty("")

    def set_born(self, date_obj):
        self.entity.born = date_obj
        self.ids.born.text = str(date_obj)

    def born_datepicker(self):
        try:
            pd = datetime.date.fromisoformat(self.ids.born.text)
            MDDatePicker(self.set_born,
                         pd.year, pd.month, pd.day).open()
        except (AttributeError, ValueError):
            MDDatePicker(self.set_born).open()

    def show_alert(self, title, message):
        dialog = MDDialog(
            title=title, size_hint=(.8, .3),
            text_button_ok='Yes', text=message,
            events_callback=lambda x, y: None)
        dialog.open()

    def validate(self):
        err = False
        try:
            gn = self.ids.given_name.text.strip()
            self.entity.given_name = gn

            names = list(filter(
                None, self.ids.names.text.strip().split(' ')))
            self.entity.names = names

            fm = self.ids.family_name.text.strip()
            self.entity.family_name = fm

            if self.ids.woman.active:
                self.entity.sex = 'woman'
            elif self.ids.man.active:
                self.entity.sex = 'man'
            elif self.ids["3rd"].active:
                self.entity.sex = 'undefined'
            else:
                self.entity.sex = None

            b = datetime.date.fromisoformat(
                self.ids.born.text.strip())
            self.entity.born = b

            if self.entity.given_name not in self.entity.names:
                err = True
        except FieldRequiredNotSet:
            err = True
        except (AttributeError, ValueError, TypeError) as e:
            print(e)
            err = True

        if err:
            self.show_alert('Error', P_LABEL_CONFIRM_INVALID)
        else:
            self.ids.entity.current = 'confirm'
            self.compilation = "" \
                               "Name: {given_name} {family_name}\nMiddle names: {names}\n" \
                               "Sex: {sex}\nBirth date: {born}".format(
                given_name=self.entity.given_name,
                family_name=self.entity.family_name,
                names=', '.join(self.entity.names),
                sex=str(self.entity.sex).capitalize(),
                born=self.entity.born)

    def confirm(self, app):
        err = False
        entity_data = PersonData()
        try:
            gn = self.ids.given_name.text.strip()
            self.entity.given_name = gn
            entity_data.given_name = gn

            names = list(filter(
                None, self.ids.names.text.strip().split(' ')))
            self.entity.names = names
            entity_data.names = names

            fm = self.ids.family_name.text.strip()
            self.entity.family_name = fm
            entity_data.family_name = fm

            if self.ids.woman.active:
                self.entity.sex = 'woman'
            elif self.ids.man.active:
                self.entity.sex = 'man'
            elif self.ids["3rd"].active:
                self.entity.sex = 'undefined'
            else:
                self.entity.sex = None
            entity_data.sex = self.entity.sex

            b = datetime.date.fromisoformat(
                self.ids.born.text.strip())
            self.entity.born = b
            entity_data.born = b

            if self.entity.given_name not in self.entity.names:
                err = True
        except FieldRequiredNotSet:
            err = True
        except (AttributeError, ValueError, TypeError) as e:
            print(e)
            err = True

        if err:
            self.show_alert('Error', P_LABEL_CONFIRM_INVALID)
        else:
            secret = libnacl.secret.SecretBox().sk
            KeyLoader.set(secret)
            portfolio = SetupPersonOperation.create(entity_data, server=True)
            facade = Glue.run_async(
                Facade.setup(app.user_data_dir, secret, Const.A_ROLE_PRIMARY, False, portfolio=portfolio))
            app.ioc.facade = facade

            self.goto_app()

    def goto_app(self):
        self.parent.switch_to(AppScreen.create(name="app"))


Builder.load_string("""
<MinistrySetupGuide@Screen>:
    MDBottomNavigation
        id: entity
        tab_display_mode: 'icons'
        MDBottomNavigationItem:
            name: 'info'
            text: "Info"
            icon: 'information-outline'
            GridLayout:
                cols: 1
                orientation: 'vertical'
                size_hint_x: None
                width: root.width
                padding: '25dp'
                spacing: '25dp'
                valign: 'top'
                MDLabel:
                    font_style: 'H3'
                    theme_text_color: 'Primary'
                    text: "Welcome"
                    halign: 'justify'
                    valign: 'top'
                    height: self.texture_size[1]
                MDLabel:
                    font_style: 'Body1'
                    theme_text_color: 'Primary'
                    text: root.label_intro
                    markup: True
                    halign: 'justify'
                    valign: 'top'
                    height: self.texture_size[1]
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    spacing: '25dp'
                    MDRaisedButton:
                        text: "I agree"
                        on_release: entity.current = 'identity'
                    MDFlatButton:
                        text: "Decline"
                        on_release: app.stop()
        MDBottomNavigationItem:
            name: 'identity'
            text: "Ministry"
            icon: 'sword'
            BoxLayout:
                orientation: 'vertical'
                size_hint_x: None
                width: root.width
                padding: '25dp'
                spacing: '25dp'
                valign: 'top'
                MDLabel:
                    font_style: 'Body1'
                    theme_text_color: 'Primary'
                    text: "What is the ministrys name?"
                    markup: True
                    halign: 'justify'
                    valign: 'top'
                MDTextField:
                    id: ministry
                    hint_text: "Ministry"
                    helper_text: "The name of the ministry"
                    helper_text_mode: "persistent"
                    required: True
                    multiline: False
                    color_mode: 'custom'
                    valign: 'top'
                BoxLayout:
                    orientation: 'horizontal'
                    spacing: '25dp'
                    valign: 'top'
                    MDTextField:
                        id: founded
                        hint_text: "Date when founded"
                        helper_text: "(YYYY-MM-DD) When where the ministry founded?"
                        helper_text_mode: "persistent"
                        required: True
                        multiline: False
                        color_mode: 'custom'
                        valign: 'top'
                    MDRaisedButton:
                        text: "Date"
                        on_release: root.founded_datepicker()
                        valign: 'top'
                MDTextField:
                    id: vision
                    hint_text: "Vision"
                    helper_text: "Describe the vision of the ministry"
                    helper_text_mode: "persistent"
                    required: True
                    multiline: True
                    color_mode: 'custom'
                    valign: 'top'
                MDRaisedButton:
                    text: "Next"
                    on_release: root.validate()
            BoxLayout:
        MDBottomNavigationItem:
            name: 'confirm'
            text: "Confirm"
            icon: 'shield-check-outline'
            BoxLayout:
                orientation: 'vertical'
                size_hint_x: None
                width: root.width
                padding: '25dp'
                spacing: '25dp'
                valign: 'top'
                MDLabel:
                    font_style: 'H3'
                    theme_text_color: 'Primary'
                    text: "Confirmation"
                    markup: True
                    halign: 'justify'
                    valign: 'top'
                MDLabel:
                    font_style: 'Body2'
                    theme_text_color: 'Primary'
                    text: root.compilation
                    markup: True
                    halign: 'justify'
                    valign: 'top'
                MDLabel:
                    font_style: 'Body1'
                    theme_text_color: 'Primary'
                    text: root.label_confirm
                    markup: True
                    halign: 'justify'
                    valign: 'top'
                MDRaisedButton:
                    text: "Confirm"
                    on_release: root.confirm(app)
            BoxLayout:

""")  # noqa E501

M_LABEL_INTRO = """
You have just installed the Logo Messenger™ app, which is a client for the Angelos network. This network is a community for Christians as well as non-believers, which enables safe and secure communication.

This community emphasizes friendliness, honesty, and security. Therefore the focus is on privacy and verifiability instead of anonymity!

You need to create a digital identity that represents your ministry by completing the form in this setup guide. This guide will generate a unique identity for the ministry, which is known to the network as an Entity document of type Ministry. [i]This information can not be changed later![/i]

[b]Legalese[/b]
Truthfulness is a requirement. False identifications are forbidden!
"""  # noqa E501

M_LABEL_CONFIRM = """
[b]Legalese[/b]
The information you have provided in this registration form must be material facts. This information is presented to other participants as an identity when you engage with them on the Angelos network. Falsification of material facts implies misrepresentation or deceit!

You confirm that all the information you have specified is truthful and correct!
"""  # noqa E501

M_LABEL_CONFIRM_INVALID = """
The information you have specified is either invalid or incomplete. Please review the form again!
"""  # noqa E501


class MinistrySetupGuide(MainWidgetBase, WidgetFactoryBehavior):
    entity = Ministry()
    confirmed = False
    label_intro = M_LABEL_INTRO
    label_confirm = M_LABEL_CONFIRM
    compilation = StringProperty("")

    def set_founded(self, date_obj):
        self.entity.founded = date_obj
        self.ids.founded.text = str(date_obj)

    def founded_datepicker(self):
        try:
            pd = datetime.date.fromisoformat(self.ids.founded.text)
            MDDatePicker(self.set_founded,
                         pd.year, pd.month, pd.day).open()
        except (AttributeError, ValueError):
            MDDatePicker(self.set_founded).open()

    def show_alert(self, title, message):
        dialog = MDDialog(
            title=title, size_hint=(.8, .3),
            text_button_ok='Yes', text=message,
            events_callback=lambda x, y: None)
        dialog.open()

    def validate(self):
        err = False
        try:
            m = self.ids.ministry.text.strip()
            self.entity.ministry = m

            v = self.ids.vision.text.strip()
            self.entity.vision = v

            b = datetime.date.fromisoformat(
                self.ids.founded.text.strip())
            self.entity.founded = b
        except (FieldRequiredNotSet, ValueError):
            err = True
        except (AttributeError, TypeError) as e:
            err = True
            raise e

        if err:
            self.show_alert('Error', C_LABEL_CHURCH_INVALID)
        else:
            self.ids.entity.current = 'confirm'
            self.compilation = "" \
                               "Ministry: {ministry}\nVision: {vision}\nFounded:" \
                               " {founded}".format(
                ministry=self.entity.ministry, vision=self.entity.vision,
                founded=self.entity.founded)

    def confirm(self, app):
        err = False
        entity_data = MinistryData()
        try:
            m = self.ids.ministry.text.strip()
            self.entity.ministry = m
            entity_data.ministry = m

            v = self.ids.vision.text.strip()
            self.entity.vision = v
            entity_data.vision = v

            b = datetime.date.fromisoformat(
                self.ids.founded.text.strip())
            self.entity.founded = b
            entity_data.founded = b

        except FieldRequiredNotSet:
            err = True
        except (AttributeError, ValueError, TypeError) as e:
            print(e)
            err = True

        if err:
            self.show_alert('Error', M_LABEL_CONFIRM_INVALID)
        else:
            secret = libnacl.secret.SecretBox().sk
            KeyLoader.set(secret)
            portfolio = SetupMinistryOperation.create(entity_data, server=True)
            facade = Glue.run_async(
                Facade.setup(app.user_data_dir, secret, Const.A_ROLE_PRIMARY, False, portfolio=portfolio))
            app.ioc.facade = facade
            self.goto_app()

    def goto_app(self):
        self.parent.switch_to(AppScreen.create(name="app"))


Builder.load_string("""
<ChurchSetupGuide>:
    MDBottomNavigation
        id: entity
        tab_display_mode: 'icons'
        MDBottomNavigationItem:
            name: 'info'
            text: "Info"
            icon: 'information-outline'
            GridLayout:
                cols: 1
                orientation: 'vertical'
                size_hint_x: None
                width: root.width
                padding: '25dp'
                spacing: '25dp'
                valign: 'top'
                MDLabel:
                    font_style: 'H3'
                    theme_text_color: 'Primary'
                    text: "Welcome"
                    halign: 'justify'
                    valign: 'top'
                    height: self.texture_size[1]
                MDLabel:
                    font_style: 'Body1'
                    theme_text_color: 'Primary'
                    text: root.label_intro
                    markup: True
                    halign: 'justify'
                    valign: 'top'
                    height: self.texture_size[1]
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    spacing: '25dp'
                    MDRaisedButton:
                        text: "I agree"
                        on_release: entity.current = 'identity'
                    MDFlatButton:
                        text: "Decline"
                        on_release: app.stop()
        MDBottomNavigationItem:
            name: 'identity'
            text: "Church"
            icon: 'church'
            BoxLayout:
                orientation: 'vertical'
                size_hint_x: None
                width: root.width
                padding: '25dp'
                spacing: '25dp'
                valign: 'top'
                MDLabel:
                    font_style: 'Body1'
                    theme_text_color: 'Primary'
                    text: root.label_info
                    markup: True
                    halign: 'justify'
                    valign: 'top'
                MDTextField:
                    id: city
                    hint_text: "City"
                    helper_text: "The city that the church represents"
                    helper_text_mode: "persistent"
                    required: True
                    multiline: False
                    # color_mode: 'custom'
                    valign: 'top'
                BoxLayout:
                    orientation: 'horizontal'
                    spacing: '25dp'
                    valign: 'top'
                    MDTextField:
                        id: founded
                        hint_text: "Founded"
                        helper_text: "(YYYY-MM-DD) Date when the church was first founded"
                        helper_text_mode: "persistent"
                        required: True
                        multiline: False
                        color_mode: 'custom'
                        valign: 'top'
                    MDRaisedButton:
                        text: "Date"
                        on_release: root.founded_datepicker()
                        valign: 'top'
                MDTextField:
                    id: region
                    hint_text: "Region"
                    helper_text: "State or region. (If applicable)"
                    helper_text_mode: "persistent"
                    required: False
                    multiline: False
                    color_mode: 'custom'
                    valign: 'top'
                BoxLayout:
                    orientation: 'horizontal'
                    spacing: '25dp'
                    valign: 'top'
                    MDTextField:
                        id: country
                        hint_text: "Country"
                        helper_text: "Country that the church resides in"
                        helper_text_mode: "persistent"
                        required: True
                        disabled: True
                        multiline: False
                        color_mode: 'custom'
                        valign: 'top'
                    MDRaisedButton:
                        text: "Country"
                        on_release: root.country_menu()
                        valign: 'top'
                MDRaisedButton:
                    text: "Next"
                    on_release: root.validate()
        MDBottomNavigationItem:
            name: 'confirm'
            text: "Confirm"
            icon: 'shield-check-outline'
            BoxLayout:
                orientation: 'vertical'
                size_hint_x: None
                width: root.width
                padding: '25dp'
                spacing: '25dp'
                valign: 'top'
                MDLabel:
                    font_style: 'H3'
                    theme_text_color: 'Primary'
                    text: "Confirmation"
                    markup: True
                    halign: 'justify'
                    valign: 'top'
                MDLabel:
                    font_style: 'Body2'
                    theme_text_color: 'Primary'
                    text: root.compilation
                    markup: True
                    halign: 'justify'
                    valign: 'top'
                MDLabel:
                    font_style: 'Body1'
                    theme_text_color: 'Primary'
                    text: root.label_confirm
                    markup: True
                    halign: 'justify'
                    valign: 'top'
                MDRaisedButton:
                    text: "Confirm"
                    on_release: root.confirm(app)
            BoxLayout:

""")  # noqa E501

C_LABEL_INTRO = """
You have just installed the Logo Messenger™ app, which is a client for the Angelos network. This network is a community for Christians as well as non-believers, which enables safe and secure communication.

This community emphasizes friendliness, honesty, and security. Therefore the focus is on privacy and verifiability instead of anonymity!

You need to create a digital identity that represents your city-church by completing the form in this setup guide. This guide will generate a unique identity for the city-church, which is known to the network as an Entity document of type Church. [i]This information can not be changed later![/i]

[b]Legalese[/b]
Truthfulness is a requirement. False identifications are forbidden!
"""  # noqa E501

C_LABEL_INFO = """
You are about to register a church. The Angelos network doesn't recognize denominational churches. Only the Body of Christ that exists in a particular city can be considered an authentic church. Therefore, no church-name is needed.
"""  # noqa E501

C_LABEL_CHURCH_INVALID = """
The specified city or founded date is either incomplete or invalid!
"""  # noqa E501

C_LABEL_CONFIRM = """
[b]Legalese[/b]
The information you have provided in this registration form must be material facts. This information is presented to other participants as an identity when you engage with them on the Angelos network. Falsification of material facts implies misrepresentation or deceit!

You confirm that all the information you have specified is truthful and correct!
"""  # noqa E501

C_LABEL_CONFIRM_INVALID = """
The information you have specified is either invalid or incomplete. Please review the form again!
"""  # noqa E501


class ChurchSetupGuide(MainWidgetBase, WidgetFactoryBehavior, Screen):
    entity = Church()
    confirmed = False
    label_intro = C_LABEL_INTRO
    label_info = C_LABEL_INFO
    label_confirm = C_LABEL_CONFIRM
    countries = []
    compilation = StringProperty("")

    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)

        for i in COUNTRIES.keys():
            self.countries.append({
                'viewclass': 'MDMenuItem',
                'text': i,
                'callback': self.set_country
            })

    def set_founded(self, date_obj):
        self.entity.founded = date_obj
        self.ids.founded.text = str(date_obj)

    def set_country(self, country):
        self.entity.country = country
        self.ids.country.text = str(country)

    def founded_datepicker(self):
        try:
            pd = datetime.date.fromisoformat(self.ids.founded.text)
            MDDatePicker(self.set_founded,
                         pd.year, pd.month, pd.day).open()
        except (AttributeError, ValueError):
            MDDatePicker(self.set_founded).open()

    def country_menu(self):
        MDDropdownMenu(items=self.countries, width_mult=4).open(self)

    def show_alert(self, title, message):
        dialog = MDDialog(
            title=title, size_hint=(.8, .3),
            text_button_ok='Yes', text=message,
            events_callback=lambda x, y: None)
        dialog.open()

    def validate(self):
        err = False
        try:
            c = self.ids.city.text.strip()
            self.entity.city = c

            f = datetime.date.fromisoformat(
                self.ids.founded.text.strip())
            self.entity.founded = f

            r = self.ids.region.text.strip()
            self.entity.region = r

            c = self.ids.country.text.strip()
            self.entity.country = c
        except (FieldRequiredNotSet, ValueError):
            err = True
        except (AttributeError, TypeError) as e:
            err = True
            raise e

        if err:
            self.show_alert('Error', C_LABEL_CHURCH_INVALID)
        else:
            self.ids.entity.current = 'confirm'
            self.compilation = "" \
                               "Founded: {founded}\nCity: {city}\nRegion:" \
                               " {region}\nCountry: {country}".format(
                founded=self.entity.founded, city=self.entity.city,
                region=self.entity.region, country=self.entity.country)

    def confirm(self, app):
        err = False
        entity_data = ChurchData()
        try:
            c = self.ids.city.text.strip()
            self.entity.city = c
            entity_data.city = c

            f = datetime.date.fromisoformat(
                self.ids.founded.text.strip())
            self.entity.founded = f
            entity_data.founded = f

            r = self.ids.region.text.strip()
            self.entity.region = r
            entity_data.region = r

            c = self.ids.country.text.strip()
            self.entity.country = c
            entity_data.country = c

        except (FieldRequiredNotSet, ValueError):
            err = True
        except (AttributeError, TypeError) as e:
            print(e)
            err = True

        if err:
            self.show_alert('Error', C_LABEL_CONFIRM_INVALID)
        else:
            secret = libnacl.secret.SecretBox().sk
            KeyLoader.set(secret)
            portfolio = SetupChurchOperation.create(entity_data, server=True)
            facade = Glue.run_async(
                Facade.setup(app.user_data_dir, secret, Const.A_ROLE_PRIMARY, False, portfolio=portfolio))
            app.ioc.facade = facade
            self.goto_app()

    def goto_app(self):
        self.parent.switch_to(AppScreen.create(name="app"))


SSKV = """
<SetupScreen>:
    BoxLayout:
        orientation: 'vertical'
        width: '250dp'
        padding: dp(15)
        spacing: dp(15)
        pos_hint: {'center_x': .5, 'center_y': .7}
        Widget:
        MDLabel:
            text: root.label_welcome
            halign: 'center'
            valign: 'bottom'
            theme_text_color: 'Primary'
        MDIconButton:
            icon: 'account'
            on_release: root.goto_person_setup()
            pos_hint: {'center_x': .5}
        Widget:
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        padding: dp(15)
        spacing: dp(15)
        Widget:
        MDIconButton:
            icon: 'church'
            on_release: root.goto_church_setup()
            theme_text_color: 'Hint'
        MDIconButton:
            icon: 'sword'
            on_release: root.goto_ministry_setup()
            theme_text_color: 'Hint'
"""

LABEL_WELCOME = "Welcome to Logo Messenger!\nChoose your type of account:"


class SetupScreen(MainWidgetBase, WidgetFactoryBehavior):
    template = SSKV
    label_welcome = LABEL_WELCOME

    def goto_ministry_setup(self):
        self.parent.switch_to(MinistrySetupGuide.create(name="setup_ministry"))

    def goto_church_setup(self):
        self.parent.switch_to(ChurchSetupGuide.create(name="setup_church"))

    def goto_person_setup(self):
        self.parent.switch_to(PersonSetupGuide.create(name="setup_person"))
