from telebot.types import Message
from database.case import database
from loader import bot


@bot.message_handler(commands=['history'])
def user_request_history(message: Message):
    scroll_request_history = database.select_users(message.from_user.id)
    for requests_user in scroll_request_history:
        bot.send_message(message.chat.id, f'Дата запроса: {requests_user[4]}\n'
                                          f'Команда: {requests_user[3]}\n'
                                          f'Город: {requests_user[0]}\n'
                                          f'Пребывание с {requests_user[1]} по {requests_user[2]}')
