from telebot.types import Message
from loader import bot


@bot.message_handler(state=None)
def send_welcome(message: Message):
    if message.text.title() == 'Привет':
        bot.send_message(message.chat.id, 'Привет')
