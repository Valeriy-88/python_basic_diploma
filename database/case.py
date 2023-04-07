import os
import logging
import sqlite3
from sqlite3 import Connection
from typing import Literal, Any
import redis
import ujson
from config_data import config


class Cache(redis.StrictRedis):
    """
    Класс Кэш. Родитель: redis.StrictRedis

    Args:
    host (str): передает имя хоста redis сервера
    port (int): передает номер порта redis сервера
    password (str): передает пароль от redis сервера
    charset (str): передает способ кодирования символов
    decode_responses (bool): передает истину для расшифровки каждого значения из базы данных
    """

    def __init__(self, host: str, port: int, password: str,
                 charset: str = "utf-8",
                 decode_responses: Literal[True] = True):
        super(Cache, self).__init__(host, port,
                                    password=password,
                                    charset=charset,
                                    decode_responses=decode_responses)
        logging.info("Redis start")

    def getting_json_file(self, name: str, value, time: int = 0) -> bool:
        """
        Функция конвертирует python-объект в Json и сохраняет его
        name str: имя пользователя
        value int: выбранная пользователем услуга
        time int: время истечения срока действия запроса в секундах
        :return: bool
        """
        return self.setex(name, time, ujson.dumps(value))

    def getting_python_object(self, name: str) -> Any | None:
        """
        Функция возвращает Json и конвертирует в python-объект
        name str: имя пользователя
        :return: Any | None
        """
        scroll_service = self.get(name)
        if scroll_service is None:
            return scroll_service
        return ujson.loads(scroll_service)


class Database:
    """
    Класс описывающий работу с базой данных

    Args:
        name (str): передается название базы данных
        _conn (Connection): передается соединение с базой данных
    """

    def __init__(self, name):
        self.name = name
        self._conn = self.connection()
        logging.info("Database connection established")

    def create_db(self) -> None:
        """
        Метод описывающий создание базы данных и таблицы в ней
        :return: None
        """
        connection = sqlite3.connect(f"{self.name}.db", check_same_thread=False)
        logging.info("Database created")
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE users
                          (id INTEGER PRIMARY KEY,
                           user_id INTEGER NOT NULL,
                           city_residence VARCHAR NOT NULL,
                           arrival_date INTEGER NOT NULL,
                           departure_date INTEGER NOT NULL,
                           minimum_room_price INTEGER NULL,
                           maximum_room_price INTEGER NULL,
                           number_hotels INTEGER NULL,
                           command VARCHAR NOT NULL,
                           date_creation INTEGER NOT NULL);''')
        connection.commit()
        cursor.close()

    def connection(self) -> Connection:
        """
        Метод описывающий подключение к базе данных
        :return: Connection
        """
        db_path = os.path.join(os.getcwd(), f"{self.name}.db")
        if not os.path.exists(db_path):
            self.create_db()
        return sqlite3.connect(f"{self.name}.db", check_same_thread=False)

    def _execute_query(self, query, select=False) -> Any:
        """
        Метод описывающий создание курсора который делает запросы и получает их результаты
        :return: Any
        """
        cursor = self._conn.cursor()
        cursor.execute(query)
        if select:
            records = cursor.fetchmany(10)
            cursor.close()
            return records
        else:
            self._conn.commit()
        cursor.close()

    def insert_users(self, user_id: int = 0, city_residence: str = None,
                     arrival_date: int = 0, departure_date: int = 0,
                     minimum_room_price: int = 0, maximum_room_price: int = 0,
                     number_hotels: int = 0, command: str = None, date_creation: int = 0) -> None:
        """
        Метод описывающий добавление пользователя и выбранные им параметры в таблицу базы данных
        :return: None
        """
        insert_query = f"""INSERT INTO users (user_id, city_residence, arrival_date, 
                                              departure_date, minimum_room_price, 
                                              maximum_room_price, number_hotels,
                                              command, date_creation)
                           VALUES ({user_id}, '{city_residence}', '{arrival_date}',
                                   '{departure_date}', {minimum_room_price}, {maximum_room_price}, 
                                   {number_hotels}, '{command}', '{date_creation}')"""
        self._execute_query(insert_query)
        logging.info(f"Options for user {user_id} added")

    def select_users(self, user_id: int) -> Any:
        """
        Метод описывающий выбор пользователя в таблице базы данных
        :return: Any
        """
        select_query = f"""SELECT city_residence, arrival_date, 
                                  departure_date, command, date_creation
                                  from users 
                           WHERE user_id = {user_id}
                           ORDER BY ID DESC"""

        record = self._execute_query(select_query, select=True)
        return record


cache = Cache(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    password=config.REDIS_PASSWORD
)
database = Database(config.BOT_DB_NAME)
