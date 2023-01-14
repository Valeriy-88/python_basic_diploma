from telebot.types import Message

from loader import bot


@bot.message_handler(commands=['hello-world'])
def send_welcome(message: Message):
    bot.send_message(message.chat.id, 'Hello my creator')
