from telebot.types import Message
from loader import bot


@bot.message_handler(commands=['history'])
def send_welcome(message: Message):
    bot.send_message(message.chat.id, 'history')
