from telebot.handler_backends import State, StatesGroup


class UserAnswerState(StatesGroup):
    service = State()
    low_value = State()
    high_value = State()
    amount_product = State()
