from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu() -> InlineKeyboardMarkup:
    """
    Функция выводит кнопки выбора под сообщением от телеграмм бота в чате
    :return: InlineKeyboardMarkup
    """
    CONFIG_KB = InlineKeyboardMarkup().row(
        InlineKeyboardButton('<- Назад', callback_data='main_window'),
        InlineKeyboardButton('Изменить', callback_data='edit_config#')
    ).add(InlineKeyboardButton("Удалить данные", callback_data='delete_config'))
    return CONFIG_KB
