import datetime
import logging
from typing import Callable

from kivy.app import App
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.screenmanager import Screen
from kivymd.theming import ThemableBehavior
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.picker import MDDatePicker
from libangelos.const import Const
from libangelos.document.entities import Church, Ministry, Person
from libangelos.document.entity_mixin import ChurchMixin, MinistryMixin, PersonMixin
from libangelos.facade.facade import Facade
from libangelos.library.nacl import SecretBox
from libangelos.misc import Loop
from libangelos.operation.setup import SetupChurchOperation, SetupMinistryOperation, SetupPersonOperation
from libangelos.policy.types import ChurchData, MinistryData, PersonData

from logo import strings

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


class AbstractSetupGuide(ThemableBehavior, Screen):
    """Abstract setup guide."""
    entity = None
    compilation = StringProperty("")
    tmpl = lambda self, x: f"Compilation template not configured"

    def __init__(self, entity, **kwargs):
        Screen.__init__(self, **kwargs)
        self.entity = entity
        self._compile()

    def set_field(self, field, value, widget=None):
        if value:
            if widget:
                widget.text = value
            setattr(self.entity, field, value.strip())
            self._compile()

    def set_date(self, field, value):
        try:
            if not isinstance(value, datetime.date):
                value = datetime.date.fromisoformat(str(value).strip())
        except ValueError:
            value = None

        if value:
            setattr(self.entity, field, value)
            self._compile()

    def set_several(self, field, value, widget=None):
        if value:
            if widget:
                widget.text = value
            setattr(self.entity, field, list(filter(None, value.strip().split(" "))))
            self._compile()

    def datepicker(self, field, widget):
        def set_date(result):
            self.set_date(field, result)
            widget.text = str(result)

        try:
            pd = datetime.date.fromisoformat(widget.text)
            MDDatePicker(set_date, pd.year, pd.month, pd.day).open()
        except (AttributeError, ValueError):
            MDDatePicker(set_date).open()

    def dialog_confirm(
            self, title, message, callback=lambda x, y: None,
            size=(.5, .5), ok=strings.TEXT_OK, cancel=strings.TEXT_CANCEL
    ):
        """Show confirm dialog with custom message and accept callback."""
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDFlatButton(
                    text=cancel,
                    text_color=App.get_running_app().theme_cls.primary_color,
                    on_press=lambda x: dialog.dismiss()
                ),
                MDFlatButton(
                    text=ok,
                    text_color=App.get_running_app().theme_cls.primary_color,
                    on_press=lambda x: (callback(x), dialog.dismiss())
                ),
            ],
            size_hint=size,
            pos_hint={"center_x": .5, "center_y": .5}  # Necessary to center on macOS
        )
        dialog.open()

    def dialog_alert(
            self, title: str, message: str, callback: Callable = lambda x: None,
            size=(.5, .5), dismiss: str = strings.TEXT_DISMISS
    ):
        """Show dialog alert with custom message and dismiss callback."""
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDFlatButton(
                    text=dismiss,
                    text_color=App.get_running_app().theme_cls.primary_color,
                    on_press=lambda x: (callback(x), dialog.dismiss()),
                )
            ],
            size_hint=size,
            pos_hint={"center_x": .5, "center_y": .5}  # Necessary to center on macOS
        )
        dialog.open()

    def dialog_prompt(self):
        pass

    def _compile(self):
        self.compilation = self.tmpl(x=self.entity)

    def _validate(self):
        """Validates the form data or throws an exception.

        Returns (bool):
            Return True if validation went fine.

        """
        raise NotImplementedError()

    def _lock(self):
        """Lock all form widgets by setting disabled to True."""
        raise NotImplementedError()

    def lock(self, x):
        self._lock()
        self.setup(*self._confirm())
        self.goto_app()

    def _confirm(self):
        """Populate entity data class and return data and what operation to use.

        Returns (EntityData, SetupEntityOperation):
            Entity data class instance and setup operation class.

        """
        raise NotImplementedError()

    def confirm(self):
        try:
            self._validate()
        except Exception as e:
            self.dialog_alert(
                strings.TEXT_DIALOG_INVALID_TITLE,
                strings.TEXT_DIALOG_INVALID + str(e), size=(.9, .3)
            )
        else:
            self.dialog_confirm(
                strings.TEXT_DIALOG_INFO_CORRECT_TITLE, strings.TEXT_DIALOG_INFO_CORRECT,
                callback=self.lock,
                ok=strings.TEXT_YES,
                cancel=strings.TEXT_NO,
                size=(.9, .3)
            )

    def setup(self, entity_data, operation_class):
        app = App.get_running_app()
        secret = SecretBox().sk
        app.key_loader.set(secret)
        portfolio = operation_class.create(entity_data, server=True)
        facade = Loop.main().run(
            Facade.setup(
                app.user_data_dir,
                secret,
                Const.A_ROLE_PRIMARY,
                False,
                portfolio=portfolio
            ), wait=True
        )
        app.ioc.facade = facade
        app.ioc.facade.data.prefs["NightMode"] = False

    def goto_app(self):
        self.parent.current = "home"


class ChurchSetupGuide(AbstractSetupGuide):
    tmpl = lambda self, x: f"{strings.TEXT_CITY}: {x.city or ''}\n{strings.TEXT_REGION}: {x.region or ''}\n{strings.TEXT_COUNTRY}: {x.country or ''}\n{strings.TEXT_FOUNDED}: {x.founded or ''}"
    countries = []
    country = ObjectProperty()

    def __init__(self, **kwargs):
        AbstractSetupGuide.__init__(self, Church(), **kwargs)

        for i in COUNTRIES.keys():
            self.countries.append({
                "viewclass": "MDMenuItem",
                "text": i,
                "callback": lambda x: self.set_field("country", x, self.country)
            })

    def country_menu(self):
        MDDropdownMenu(items=self.countries, width_mult=4).open(self)

    def _validate(self):
        for name in ChurchMixin._fields.keys():
            self.entity._fields[name].validate(getattr(self.entity, name), name)
        return True

    def _lock(self):
        self.ids.city.disabled = True
        self.ids.founded.disabled = True
        self.ids.region.disabled = True
        self.ids.country.disabled = True
        self.ids.country_btn.disabled = True
        self.ids.date_btn.disabled = True

    def _confirm(self):
        entity_data = ChurchData()

        entity_data.city = self.entity.city
        entity_data.founded = self.entity.founded
        entity_data.region = self.entity.region
        entity_data.country = self.entity.country

        return entity_data, SetupChurchOperation


class MinistrySetupGuide(AbstractSetupGuide):
    tmpl = lambda self, x: f"{strings.TEXT_MINISTRY}: {x.ministry or ''}\n{strings.TEXT_FOUNDED}: {x.founded or ''}\n{strings.TEXT_VISION}: {x.vision or ''}"

    def __init__(self, **kwargs):
        AbstractSetupGuide.__init__(self, Ministry(), **kwargs)

    def _validate(self):
        for name in MinistryMixin._fields.keys():
            self.entity._fields[name].validate(getattr(self.entity, name), name)
        return True

    def _lock(self):
        self.ids.ministry.disabled = True
        self.ids.vision.disabled = True
        self.ids.founded.disabled = True
        self.ids.date_btn.disabled = True

    def _confirm(self):
        entity_data = MinistryData()

        entity_data.ministry = self.entity.ministry
        entity_data.vision = self.entity.vision
        entity_data.founded = self.entity.founded

        return entity_data, SetupMinistryOperation


class PersonSetupGuide(AbstractSetupGuide):
    tmpl = lambda self, x: f"{strings.TEXT_NAME}: {x.given_name or ''} {x.family_name or ''}\n{strings.TEXT_FORNAME}: {x if not list else ' '.join(x.names) if x.names else ''}\n{strings.TEXT_SEX}: {str(x.sex).capitalize() if x.sex else ''}\n{strings.TEXT_BIRTHDATE}: {x.born or ''}"

    def __init__(self, **kwargs):
        AbstractSetupGuide.__init__(self, Person(), **kwargs)

    def _validate(self):
        for name in PersonMixin._fields.keys():
            self.entity._fields[name].validate(getattr(self.entity, name), name)
        PersonMixin._check_names(self.entity)
        return True

    def _lock(self):
        self.ids.given_name.disabled = True
        self.ids.names.disabled = True
        self.ids.family_name.disabled = True
        self.ids.woman.disabled = True
        self.ids.man.disabled = True
        self.ids.third.disabled = True
        self.ids.born.disabled = True
        self.ids.date_btn.disabled = True

    def _confirm(self):
        entity_data = PersonData()

        entity_data.given_name = self.entity.given_name
        entity_data.names = self.entity.names
        entity_data.family_name = self.entity.family_name
        entity_data.sex = self.entity.sex
        entity_data.born = self.entity.born

        return entity_data, SetupPersonOperation


class SetupGuide(Screen):
    pass
