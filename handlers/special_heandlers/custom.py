import time
from typing import Any
from keyboards.inline.custom_button import city_residence, scroll_city, choice_answer
from states.answer_user import UserAnswerState
from telebot.types import Message
from loader import bot
from database.case import database
from datetime import datetime, timedelta
from handlers.special_heandlers.hotel_search import search_id_city, data_collection
from yahoo_fin import stock_info
import json


@bot.message_handler(commands=['custom'])
def survey(message: Message) -> None:
    """
    Функция реагирует при вводе команды /custom.
    При вводе команды, выводиться сообщение с вопросом,
    в каком городе пользователь собирается снять номер в отеле
    :param message: Message.text
    :return: None
    """
    bot.set_state(message.from_user.id, UserAnswerState.city, message.chat.id)
    bot.send_message(message.from_user.id, 'Введите город в котором собираетесь бронировать номер в отеле')


@bot.message_handler(state=UserAnswerState.city)
def choice_city(message: Message) -> None:
    """
    Функция ожидает от пользователя ввод названия города, в котором он будет бронировать номер в отеле.
    При вводе слова, записывает его в класс состояний для дальнейшего использования в программе.
    :param message: Message.text
    :return: None
    """
    with open('scroll_city_russia.json', 'r', encoding='utf-8') as file:
        ban_city = json.load(file)

    scroll_cities = list(ban_city.values())
    try:
        if message.text.title() not in scroll_cities:
            replacing_characters = message.text.replace('-', '')
            re_change_characters = replacing_characters.replace(' ', '')
            if re_change_characters.isalpha():
                bot.send_message(message.from_user.id, 'Выберите город:', reply_markup=city_residence(message.text))
            else:
                bot.send_message(message.from_user.id, 'Название города должно быть только из букв')
        else:
            bot.send_message(message.from_user.id, 'Поиск отелей по России временно недоступен. '
                                                   'Приносим свои извинения.')
            bot.send_message(message.from_user.id, 'Введите город в котором собираетесь бронировать номер в отеле')
    except (TypeError, SyntaxError):
        bot.send_message(message.from_user.id, 'Некорректный ввод названия города')
        bot.send_message(message.from_user.id, 'Введите город в котором собираетесь бронировать номер в отеле')


@bot.callback_query_handler(func=lambda custom: custom.data[:21] in 'city_residence_custom')
def host_city(call) -> None:
    """
    Функция ожидает от пользователя выбор города в котором он будет бронировать номер в отеле.
    И записывает его в класс состояний для дальнейшего использования в программе.
    :param call: Callback_data
    :return: None
    """
    bot.send_message(call.from_user.id, 'Введите дату заезда в отель в формате dd.mm.yyyy')
    bot.set_state(call.from_user.id, UserAnswerState.arrival_date)

    index_city = call.data.split("#")[-1]
    with bot.retrieve_data(call.from_user.id) as data:
        data['city'] = scroll_city[int(index_city)]


def amount_days_in_month(date: list) -> int:
    """
    Функция получает дату в виде списка,
    и определяет количество дней в месяце введенном пользователем
    :param date: list
    :return: Integer
    """
    days_in_month = 31
    leap_year = True
    if not date[2] % 400 == 0 or not date[2] % 100 == 0 or not date[2] % 4 == 0:
        leap_year = False
    if (date[1] == 2) and (leap_year is True):
        days_in_month = 29
    elif (date[1] == 2) and (leap_year is False):
        days_in_month = 28
    elif (date[1] == 4) or (date[1] == 6) or (date[1] == 9) or (date[1] == 11):
        days_in_month = 30
    return days_in_month


@bot.message_handler(state=UserAnswerState.arrival_date)
def day_arrival_city(message: Message) -> None:
    """
    Функция ожидает от пользователя ввод даты заезда в отель.
    Проверяет дату на корректность ввода.
    И записывает её в класс состояний для дальнейшего использования в программе.
    :param message: Message.text
    :return: None
    """
    try:
        replacing_characters_date_arrival = message.text.replace('.', ' ')
        date_arrival = replacing_characters_date_arrival.split(' ')
        arrival = [int(date_arrival[0]), int(date_arrival[1]), int(date_arrival[2])]
        now_date = time.strftime("%d,%m,%Y", time.localtime())
        date = now_date.split(',')
        days_in_month = amount_days_in_month(arrival)
        if arrival[1] == int(date[1]) and arrival[2] == int(date[2]):
            if int(date[0]) <= arrival[0] <= days_in_month:
                bot.send_message(message.from_user.id, 'Введите дату отъезда из отеля в формате dd.mm.yyyy')
                bot.set_state(message.from_user.id, UserAnswerState.departure_date, message.chat.id)

                with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data['arrival_date'] = message.text
            else:
                bot.send_message(message.from_user.id, 'Некорректный ввод даты')
                bot.send_message(message.from_user.id, 'Введите дату заезда в отель в формате dd.mm.yyyy')

        elif int(date[1]) < arrival[1] < 13 and int(date[2]) <= arrival[2] <= int(date[2]) + 1:
            if arrival[0] <= days_in_month:
                bot.send_message(message.from_user.id, 'Введите дату отъезда из отеля в формате dd.mm.yyyy')
                bot.set_state(message.from_user.id, UserAnswerState.departure_date, message.chat.id)

                with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data['arrival_date'] = message.text
            else:
                bot.send_message(message.from_user.id, 'Некорректный ввод даты')
                bot.send_message(message.from_user.id, 'Введите дату заезда в отель в формате dd.mm.yyyy')
        else:
            bot.send_message(message.from_user.id, 'Некорректный ввод даты')
            bot.send_message(message.from_user.id, 'Введите дату заезда в отель в формате dd.mm.yyyy')
    except (ValueError, IndexError):
        bot.send_message(message.from_user.id, 'Ожидался ввод даты в формате dd.mm.yyyy')
        bot.send_message(message.from_user.id, 'Введите дату заезда в отель')


@bot.message_handler(state=UserAnswerState.departure_date)
def day_departure_city(message: Message) -> None:
    """
    Функция ожидает от пользователя ввод даты отъезда из отеля.
    Проверяет дату на корректность ввода.
    И записывает её в класс состояний для дальнейшего использования в программе.
    :param message: Message.text
    :return: None
    """
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            day_arrival = data['arrival_date']
        replacing_characters_date_arrival = day_arrival.replace('.', ' ')
        date_arrival = replacing_characters_date_arrival.split(' ')
        arrival = [int(date_arrival[0]), int(date_arrival[1]), int(date_arrival[2])]

        replacing_characters_date_departure = message.text.replace('.', ' ')
        date_departure = replacing_characters_date_departure.split(' ')
        departure = [int(date_departure[0]), int(date_departure[1]), int(date_departure[2])]

        now_date = time.strftime("%d,%m,%Y", time.localtime())
        date = now_date.split(',')
        days_in_month = amount_days_in_month(departure)
        if departure[1] == arrival[1] and departure[2] == arrival[2]:
            if arrival[0] < departure[0] <= days_in_month:
                bot.send_message(message.from_user.id, 'Введите минимальную стоимость номера в отеле за сутки в рублях')
                bot.set_state(message.from_user.id, UserAnswerState.low_value)

                with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data['departure_date'] = message.text
            else:
                bot.send_message(message.from_user.id, 'Некорректный ввод даты')
                bot.send_message(message.from_user.id, 'Введите дату отъезда из отеля в формате dd.mm.yyyy')

        elif (departure[1] > arrival[1]) and (departure[2] == arrival[2]) \
                and (departure[0] <= days_in_month) and (departure[1] < 13):
            bot.send_message(message.from_user.id, 'Введите минимальную стоимость номера в отеле за сутки в рублях')
            bot.set_state(message.from_user.id, UserAnswerState.low_value)

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['departure_date'] = message.text

        elif arrival[2] < departure[2] <= int(date[2]) + 1 and departure[0] <= days_in_month and departure[1] < 13:
            bot.send_message(message.from_user.id, 'Введите минимальную стоимость номера в отеле за сутки в рублях')
            bot.set_state(message.from_user.id, UserAnswerState.low_value)

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['departure_date'] = message.text
        else:
            bot.send_message(message.from_user.id, 'Некорректный ввод даты')
            bot.send_message(message.from_user.id, 'Введите дату отъезда из отеля в формате dd.mm.yyyy')
    except (ValueError, IndexError):
        bot.send_message(message.from_user.id, 'Ожидался ввод даты в формате dd.mm.yyyy')
        bot.send_message(message.from_user.id, 'Введите дату отъезда из отеля')


@bot.message_handler(state=UserAnswerState.low_value)
def minimum_room_price(message: Message) -> None:
    """
    Функция ожидает от пользователя ввод минимальной стоимости номера в отеле за сутки.
    При вводе числа, конвертирует его в доллары записывает в класс состояний для дальнейшего использования в программе.
    :param message: Message.text
    :return: None
    """
    if message.text.isdigit():
        if int(message.text) > 0:
            symbol = f"RUBUSD=X"
            latest_data = stock_info.get_data(symbol, interval="1m", start_date=datetime.now() - timedelta(days=3))
            latest_price = latest_data.iloc[-1].close
            currency_converter = round(latest_price * int(message.text), 2)

            bot.send_message(message.from_user.id, 'Введите максимальную стоимость номера в отеле за сутки в рублях')
            bot.set_state(message.from_user.id, UserAnswerState.high_value, message.chat.id)

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['low_value'] = currency_converter
        else:
            bot.send_message(message.from_user.id, 'Минимальная стоимость должна быть больше нуля')
            bot.send_message(message.from_user.id, 'Введите минимальную стоимость номера в отеле за сутки в рублях')
    else:
        bot.send_message(message.from_user.id, 'Стоимость номера может быть только числом')
        bot.send_message(message.from_user.id, 'Введите минимальную стоимость номера в отеле за сутки в рублях')


@bot.message_handler(state=UserAnswerState.high_value)
def maximum_room_price(message: Message) -> None:
    """
    Функция ожидает от пользователя ввод максимальной стоимости номера в отеле за сутки.
    При вводе числа, конвертирует его в доллары записывает в класс состояний для дальнейшего использования в программе.
    :param message: Message.text
    :return: None
    """
    if message.text.isdigit():
        symbol = f"RUBUSD=X"
        latest_data = stock_info.get_data(symbol, interval="1m", start_date=datetime.now() - timedelta(days=3))
        latest_price = latest_data.iloc[-1].close
        currency_converter = round(latest_price * int(message.text), 2)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            low_price = data['low_value']

        if currency_converter > low_price:
            bot.send_message(message.from_user.id, 'Введите интересующее количество отелей')
            bot.set_state(message.from_user.id, UserAnswerState.amount_product)

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['high_value'] = currency_converter
        else:
            bot.send_message(message.from_user.id, 'Максимальная стоимость не может быть меньше минимальной')
    else:
        bot.send_message(message.from_user.id, 'Стоимость номера может быть только числом')


@bot.message_handler(state=UserAnswerState.amount_product)
def number_hotels(message: Message) -> None:
    """
    Функция ожидает от пользователя ввод количества отелей.
    При вводе числа, записывает его в класс состояний для дальнейшего использования в программе.
    Записывает выбранные пользователем настройки в таблицу базы данных.
    Выводит сообщение о выбранных настройках и список отелей на основании этих настроек.
    :param message: Message.text
    :return: None
    """
    try:
        if message.text.isdigit():
            if int(message.text) < 1:
                bot.send_message(message.from_user.id, 'Количество отелей должно быть больше нуля')
            else:
                date_now = datetime.now().date()
                with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data['amount_product'] = int(message.text)
                    database.insert_users(user_id=message.from_user.id,
                                          city_residence=data['city'],
                                          arrival_date=data['arrival_date'],
                                          departure_date=data['departure_date'],
                                          minimum_room_price=data['low_value'],
                                          maximum_room_price=data['high_value'],
                                          number_hotels=message.text,
                                          command='/custom',
                                          date_creation=str(date_now)
                                          )

                    info = f'Выбранные вами настройки:\n' \
                           f'Город проживания - {data["city"]}\n' \
                           f'Дата заезда в отель - {data["arrival_date"]}\n' \
                           f'Дата отъезда из отеля - {data["departure_date"]}\n' \
                           f'Минимальная стоимость номера за сутки - {data["low_value"]} $\n' \
                           f'Максимальная стоимость номера за сутки - {data["high_value"]} $\n' \
                           f'Количество отелей - {message.text}\n' \

                    bot.send_message(message.from_user.id, info)
                    bot.send_message(message.from_user.id, text="Настройки сохранены")
                    bot.send_message(message.from_user.id, 'Список отелей по интересующим вас настройкам:')
                    city_stay = data['city'].split(', ')
                    id_town = search_id_city(city_stay[0])
                    data['data_hotels'] = data_collection(id_town,
                                                          int(data['arrival_date'][:2]),
                                                          int(data['arrival_date'][3:5]),
                                                          int(data['arrival_date'][6:]),
                                                          int(data['departure_date'][:2]),
                                                          int(data['departure_date'][3:5]),
                                                          int(data['departure_date'][6:]),
                                                          int(message.text), data['low_value'], data['high_value'])
                    data['lower_value_threshold'] = 0
                    data['upper_value_threshold'] = 10
                    count_hotels = len(data['data_hotels'])

                    if int(message.text) < 10 or count_hotels < 10:
                        print_info_hotels(message.from_user.id,
                                          price_list_hotels=data['data_hotels'],
                                          quantity_hotels=int(message.text)
                                          )
                        bot.send_message(message.from_user.id, 'Выберите из меню интересующую вас команду')
                        bot.set_state(message.from_user.id, UserAnswerState.choice)
                    else:
                        print_info_hotels(message.from_user.id, price_list_hotels=data['data_hotels'])
                        bot.send_message(message.from_user.id,
                                         'Желаете ли просмотреть еще отели?',
                                         reply_markup=choice_answer())
        else:
            bot.send_message(message.from_user.id, 'Количество отелей может быть только числом')
    except TypeError:
        bot.send_message(message.from_user.id, 'По заданной стоимости отели не найдены. '
                                               'Измените диапазон цен стоимости номера в отеле.')
        bot.set_state(message.from_user.id, UserAnswerState.low_value)


def print_info_hotels(message, price_list_hotels: dict, quantity_hotels: int = 10, offset: int = 0):
    """
    Функция выводит список отелей в диапазоне значений.
    :param message: Callback
    :param price_list_hotels: Dict
    :param quantity_hotels: Int
    :param offset: Int
    """
    minimum_value, maximum_value = 0 + offset, quantity_hotels + offset
    for index, data in enumerate(price_list_hotels.values()):
        if minimum_value <= index < maximum_value:
            parameter_value = list(data.values())
            bot.send_photo(message,
                           photo=f'{parameter_value[1]}',
                           caption=f'Название отеля: {parameter_value[0]} \n'
                                   f'Расстояние от центра: {parameter_value[2]} \n'
                                   f'Стоимость: {parameter_value[3]} \n'
                           )
    return


@bot.callback_query_handler(func=lambda exit_from_command: exit_from_command.data in ('yes', 'no'))
def leaving_the_command(call: Any) -> None:
    """
    Функция реагирует на выбор пользователем кнопки.
    При нажатии на кнопку "да" функция выводит следующие 10 отелей из списка.
    При нажатии на кнопку "нет" функция выводит сообщение и завершает выполнение команды.
    Если количество отелей больше 10, то выводит сообщение и ожидает ответ от пользователя
    :param call: Callback
    :return: None
    """
    with bot.retrieve_data(call.from_user.id) as data:
        scroll_hotels = data['data_hotels']
        data['lower_value_threshold'] += 10
        data['upper_value_threshold'] += 10
    if call.data == 'yes':
        print_info_hotels(call.from_user.id, price_list_hotels=scroll_hotels, offset=data['lower_value_threshold'])
    elif call.data == 'no':
        bot.send_message(call.from_user.id, 'Выберите из меню интересующую вас команду')
        bot.set_state(call.from_user.id, UserAnswerState.choice)
    if call.data != 'no':
        if data['upper_value_threshold'] < data['amount_product']:
            bot.send_message(call.from_user.id, 'Желаете ли просмотреть еще отели?',
                             reply_markup=choice_answer())
        else:
            bot.send_message(call.from_user.id, 'Выберите из меню интересующую вас команду')
            bot.set_state(call.from_user.id, UserAnswerState.choice)
