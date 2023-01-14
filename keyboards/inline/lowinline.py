from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def menu() -> InlineKeyboardMarkup:
    CONFIG_KB = InlineKeyboardMarkup().row(
        InlineKeyboardButton('<- Назад', callback_data='main_window'),
        InlineKeyboardButton('Изменить', callback_data='edit_config#')
    ).add(InlineKeyboardButton("Удалить данные", callback_data='delete_config'))
    return CONFIG_KB
