from states.answer_user import UserAnswerState
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from loader import bot
from emoji import emojize
from config_data import config
from states import answer_user


scroll_service = []
offset = 0


@bot.message_handler(commands=['custom'])
def product_selection(message: Message) -> None:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("да", callback_data='yes'),
                 InlineKeyboardButton("нет", callback_data='no'))
    bot.send_message(message.from_user.id, 'Применить фильтр услуг?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda  c: c.data[:6] in ['yes', 'no'])
def callback(call):
    if call.data == 'yes':
        bot.send_message(call.from_user.id, 'Выберите интересующие вас услуги', reply_markup=choice([]))
        bot.set_state(call.from_user.id, UserAnswerState.service)
    elif call.data == 'no':
        bot.send_message(call.from_user.id, 'Введите минимальную стоимость номера в отеле за сутки')
        bot.set_state(call.from_user.id, UserAnswerState.low_value)


@bot.message_handler(state=UserAnswerState.service)
def choice(active_leagues: list) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    service_keys = list(config.BOT_SERVICE.keys())[0 + offset:9 + offset]
    for key in service_keys:
        if key in active_leagues:
            keyboard.add(InlineKeyboardButton(
                f"{emojize('✅')} {config.BOT_SERVICE[key]}",
                callback_data=f'del_league_#{offset}#{key}'
            ))
        else:
            keyboard.add(InlineKeyboardButton(
                config.BOT_SERVICE[key],
                callback_data=f'add_league_#{offset}#{key}'
            ))
    if offset > 8:
        keyboard.row(
            InlineKeyboardButton("<- Назад", callback_data='edit_config#0'),
            InlineKeyboardButton("Сохранить", callback_data='save_config'))
    else:
        keyboard.row(
            InlineKeyboardButton("Вперед ->", callback_data='edit_config#9'),
            InlineKeyboardButton("Сохранить", callback_data='save_config'))
    return keyboard


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global offset
    if call.data == 'edit_config#9':
        offset += 9
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Выберите интересующие вас услуги',
                              reply_markup=choice(scroll_service))
    elif call.data == 'edit_config#0':
        offset -= 9
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Выберите интересующие вас услуги',
                              reply_markup=choice(scroll_service))
    elif call.data == 'save_config':
        bot.set_state(call.from_user.id, UserAnswerState.low_value)
        answer_user.service = scroll_service
        bot.send_message(call.from_user.id, 'Введите минимальную стоимость номера в отеле за сутки')
    else:
        set_or_update_config(call)


def update_leagues(data: str):
    """Функция добавляет или удаляет id услуги"""
    global scroll_service
    service_id = data.split("#")[-1]
    if data.startswith("add"):
        scroll_service.append(service_id)
    else:
        scroll_service.remove(service_id)


@bot.callback_query_handler(func=lambda call: True)
def set_or_update_config(call):
    """Получение или обновление выбранных услуг"""
    update_leagues(call.data)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='Выберите интересующие вас услуги',
                          reply_markup=choice(scroll_service))


@bot.message_handler(state=UserAnswerState.low_value)
def minimum_index(message: Message) -> None:
    if message.text.isdigit():
        bot.send_message(message.from_user.id, 'Введите максимальную стоимость номера в отеле за сутки')
        bot.set_state(message.from_user.id, UserAnswerState.high_value, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['low_value'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Стоимость номера может быть только числом')


@bot.message_handler(state=UserAnswerState.high_value)
def highest_value(message: Message) -> None:
    if message.text.isdigit():
        bot.send_message(message.from_user.id, 'Введите интересующее количество отелей')
        bot.set_state(message.from_user.id, UserAnswerState.amount_product, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['high_value'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Стоимость номера может быть только числом')


@bot.message_handler(state=UserAnswerState.amount_product)
def number_hotels(message: Message) -> None:
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['amount_product'] = message.text
            bot.send_message(message.from_user.id, 'Вот список отелей по интересующим вас услугам:')
            bot.set_state(message.from_user.id, message.chat.id)
            bot.send_message(message.chat.id, 'Выберите из меню интересующую вас команду')
    else:
        bot.send_message(message.from_user.id, 'Количество отелей может быть только числом')
