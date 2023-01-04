from aiogram import Bot, Dispatcher, executor, types

my_token = '5925349398:AAHNT0yAAOEfDE7zG81OK_boPoim-c0c3qU'

bot = Bot(token=my_token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['hello-world'])
async def send_welcome(message: types.Message):
    await bot.send_message(message.chat.id, 'Hello my creator')


@dp.message_handler(content_types=["text"])
async def send_welcome(message: types.Message):
    if message.text.title() == 'Привет':
        await bot.send_message(message.chat.id, 'Привет')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
