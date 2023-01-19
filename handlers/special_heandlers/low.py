from states.answer_user import UserAnswerState
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from loader import bot
from emoji import emojize
from config_data import config
from states import answer_user


scroll_service = []
offset = 0


@bot.message_handler(commands=['low'])
def applying_service_filter(message: Message) -> None:
    """
    Функция реагирует при вводе команды /low.
    При вводе команды, выводиться сообщение с вариантами ответа в виде кнопок
    :param message: str
    :return: None
    """
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("да", callback_data='yes'),
                 InlineKeyboardButton("нет", callback_data='no'))
    bot.send_message(message.from_user.id, 'Применить фильтр услуг?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda answer_user: answer_user.data[:6] in ['yes', 'no'])
def reaction_user_choice(call) -> None:
    """
    Функция ожидает от пользователя нажатие на кнопку и соответственно реагирует.
    Если пользователь выбрал "да", то выводит сообщение и список услуг в виде кнопок.
    Если пользователь выбрал "нет", то пропускает выбор услуг и выводит сообщение с ожиданием ответа.
    :param call: Callback_data
    :return: None
    """
    if call.data == 'yes':
        bot.send_message(call.from_user.id, text='Выберите интересующие вас услуги',
                         reply_markup=displaying_scroll_services([]))
        bot.set_state(call.from_user.id, UserAnswerState.service)
    elif call.data == 'no':
        bot.send_message(call.from_user.id, text='Введите минимальную стоимость номера в отеле за сутки')
        bot.set_state(call.from_user.id, UserAnswerState.low_value)


@bot.message_handler(state=UserAnswerState.service)
def displaying_scroll_services(selected_services: list) -> InlineKeyboardMarkup:
    """
    Функция отображает в телеграм боте список услуг в виде кнопок.
    При на нажатии на кнопку ставится галочка и услуга записывается в список выбранных.
    При повторном нажатии на ту же кнопку, услуга удаляется из списка выбранных.
    :param selected_services: List
    :return: keyboard
    """
    keyboard = InlineKeyboardMarkup()
    service_keys = list(config.BOT_SERVICE.keys())[0 + offset:9 + offset]
    for key in service_keys:
        if key in selected_services:
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
def reaction_user_choice(call) -> None:
    """
    Функция реагирует при нажатии на кнопку.
    При нажатии "Вперед ->" функция выводит следующий список услуг.
    При нажатии "Назад <-" функция выводит изначальный список услуг.
    При нажатии "Сохранить" функция сохраняет выбранные услуги.
    :param call: Callback_data
    :return: None
    """
    global offset
    if call.data == 'edit_config#9':
        offset += 9
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Выберите интересующие вас услуги',
                              reply_markup=displaying_scroll_services(scroll_service))
    elif call.data == 'edit_config#0':
        offset -= 9
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Выберите интересующие вас услуги',
                              reply_markup=displaying_scroll_services(scroll_service))
    elif call.data == 'save_config':
        bot.send_message(call.from_user.id, 'Введите минимальную стоимость номера за сутки')
        bot.set_state(call.from_user.id, UserAnswerState.low_value)
        answer_user.service = scroll_service
    else:
        set_or_update_config(call)


def update_list_services(data: str) -> None:
    """
    Функция добавляет или удаляет id выбранной услуги.
    :param data: Str
    :return: None
    """
    global scroll_service
    service_id = data.split("#")[-1]
    if data.startswith("add"):
        scroll_service.append(service_id)
    else:
        scroll_service.remove(service_id)


@bot.callback_query_handler(func=lambda call: True)
def set_or_update_config(call) -> None:
    """
    Функция получает или обновляет список выбранных услуг
    :param call: Callback_data
    :return: None
    """
    update_list_services(call.data)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='Выберите интересующие вас услуги',
                          reply_markup=displaying_scroll_services(scroll_service))


@bot.message_handler(state=UserAnswerState.low_value)
def minimum_room_price(message: Message) -> None:
    """
    Функция ожидает от пользователя стоимость номера за сутки.
    При вводе числа, записывает его в класс состояний для дальнейшего использования в программе.
    :param message: Str
    :return: None
    """
    if message.text.isdigit():
        bot.send_message(message.from_user.id, 'Введите интересующее количество отелей')
        bot.set_state(message.from_user.id, UserAnswerState.amount_product, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['low_value'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Стоимость номера может быть только числом')


@bot.message_handler(state=UserAnswerState.amount_product)
def number_hotels(message: Message) -> None:
    """
    Функция ожидает от пользователя ввод количества отелей для вывода на дисплей.
    При вводе числа, записывает его в класс состояний для дальнейшего использования в программе.
    :param message: Str
    :return: None
    """
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['amount_product'] = message.text
            bot.send_message(message.from_user.id, 'Вот список отелей по интересующим вас услугам:')
            bot.set_state(message.from_user.id, message.chat.id)
            bot.send_message(message.chat.id, 'Выберите из меню интересующую вас команду')
    else:
        bot.send_message(message.from_user.id, 'Количество отелей может быть только числом')

