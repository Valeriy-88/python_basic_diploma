import requests
from config_data.config import city_search, hotel_search, headers_city_search, headers_hotel_search

# id:"473490" # для детального просмотра отеля


def search_id_city(city: str) -> int:
    """
    Функция выполняет поиск id города введенного пользователем запрашивая данные из api стороннего сайта.
    :param city: Str
    :return: Int
    """
    querystring = {"q": city, "locale": "ru_RU"}
    id_city = 0
    scroll_hotels = requests.request("GET", city_search, headers=headers_city_search, params=querystring)

    for parameter in scroll_hotels.json()['sr']:
        for key in parameter:
            if key == 'gaiaId':
                id_city = parameter[key]
                break
        if id_city != 0:
            break
    return id_city


def data_collection(id_town: int, day_arrival: int, month_arrival: int, year_arrival: int,
                    departure_day: int, departure_month: int, departure_year: int,
                    amount_hotels: int, minimum_price: int = 1, maximum_price: int = 99999):
    """
    Функция выполняет поиск отелей по заданным пользователем параметрам,
    запрашивая данные из api стороннего сайта.
    Сохраняет результат в словаре и выводит первые десять отелей в телеграм боте
    """
    selection_criteria = {
        "currency": "USD",
        "eapid": 1,
        "locale": "ru_RU",
        "siteId": 300000001,
        "destination": {"regionId": id_town},
        "checkInDate": {
            "day": day_arrival,
            "month": month_arrival,
            "year": year_arrival
        },
        "checkOutDate": {
            "day": departure_day,
            "month": departure_month,
            "year": departure_year
        },
        "rooms": [{"adults": 2}],
        "resultsStartingIndex": 0,
        "resultsSize": amount_hotels,
        "sort": "PRICE_LOW_TO_HIGH",
        "filters": {"price": {
            "max": maximum_price,
            "min": minimum_price
        }}
    }

    response = requests.request("POST", hotel_search, json=selection_criteria, headers=headers_hotel_search)
    info_hotels = {}
    properties_hotel = {}
    for index, scroll_parameters in enumerate(response.json()['data']['propertySearch']['properties']):
        hotel_information_search(scroll_parameters, index, info_hotels, properties_hotel)
        properties_hotel = {}
    return info_hotels


def hotel_information_search(hotel_information, count: int, scroll_hotels: dict, intelligence_hotel: dict):
    """
    Функция собирает необходимые данные об отеле. Выполняя рекурсивный поиск в словаре.
    :param hotel_information: Dict or tuple
    :param count: Int
    :param scroll_hotels: Dict
    :param intelligence_hotel: Dict
    :return: None
    """
    if isinstance(hotel_information, dict):
        for hotel_data in hotel_information.items():
            if hotel_data[0] in ('name', 'url', 'label', 'distanceFromMessaging'):
                intelligence_hotel[hotel_data[0]] = hotel_data[1]
            else:
                hotel_information_search(hotel_data, count, scroll_hotels, intelligence_hotel)
    elif isinstance(hotel_information, tuple):
        if isinstance(hotel_information[1], dict):
            hotel_information_search(hotel_information[1], count, scroll_hotels, intelligence_hotel)
        else:
            return
    else:
        return

    scroll_hotels[count] = intelligence_hotel
