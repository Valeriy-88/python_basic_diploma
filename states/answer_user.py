from telebot.handler_backends import State, StatesGroup


class UserAnswerState(StatesGroup):
    city = State()
    city_high = State()
    city_low = State()
    arrival_date = State()
    arrival_date_high = State()
    arrival_date_low = State()
    departure_date = State()
    departure_date_high = State()
    departure_date_low = State()
    low_value = State()
    low_value_low = State()
    high_value = State()
    high_value_high = State()
    amount_product = State()
    amount_product_low = State()
    amount_product_high = State()
    choice = State()
