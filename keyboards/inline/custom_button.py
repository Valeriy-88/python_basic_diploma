from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from geopy.geocoders import Nominatim

scroll_city = {}


def city_residence(town: str) -> InlineKeyboardMarkup:
    """
    Функция отображает в телеграм боте список городов в виде кнопок.
    Добавляется в словарь id городов и сами города.
    При на нажатии на кнопку записывается id нужного города.
    :return: InlineKeyboardMarkup
    """
    geolocator = Nominatim(user_agent="valeravoronov88@gmail.com")
    location = geolocator.geocode(query={'city': town}, exactly_one=False)
    keyboard = InlineKeyboardMarkup()
    for index, city in enumerate(location):
        keyboard.add(InlineKeyboardButton(
            city.address,
            callback_data=f'city_residence_custom_#{index}'
        ))
        scroll_city[index] = f'{city}'
    return keyboard


def choice_answer() -> InlineKeyboardMarkup:
    """
    Функция выводит кнопки выбора под сообщением от телеграмм бота в чате
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Да", callback_data='yes'),
                 InlineKeyboardButton("Нет", callback_data='no'))
    return keyboard
