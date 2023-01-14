from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config

storage = StateMemoryStorage()
bot = TeleBot(token=config.SECRET_KEY, state_storage=storage)
