from dotenv import load_dotenv, find_dotenv
import os
import logging

logging.basicConfig(level=logging.INFO)

if not find_dotenv():
    exit('Переменные окружения не загружены. Отсутствует файл .env')
else:
    load_dotenv()

SECRET_KEY = os.getenv('MY_TOKEN')

DEFAULT_COMMANDS = (
    ('help', "Помощь по командам бота"),
    ('low', "Поиск отелей с минимальной стоимостью за номер"),
    ('high', "Поиск отелей с максимальной стоимостью за номер"),
    ('custom', "Поиск отелей в диапазоне стоимости за номер"),
    ('history', "Вывод истории запросов пользователей")
)

BOT_VERSION = 0.1
BOT_DB_NAME = "users_options"

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PASSWORD = None

RAPID_API_KEY = "41ab3025damshc061f7d76ce4dc0p1a130bjsn19033d53b54b"
RAPID_API_HOST = "hotels4.p.rapidapi.com"
city_search = "https://hotels4.p.rapidapi.com/locations/v3/search"
hotel_search = "https://hotels4.p.rapidapi.com/properties/v2/list"

headers_city_search = {
    "X-RapidAPI-Key": RAPID_API_KEY,
    "X-RapidAPI-Host": RAPID_API_HOST
}

headers_hotel_search = {
    "content-type": "application/json",
    "X-RapidAPI-Key": RAPID_API_KEY,
    "X-RapidAPI-Host": RAPID_API_HOST
}
