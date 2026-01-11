from aiogram.fsm.state import StatesGroup, State

class ProfileStates(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity = State()
    city = State()


class WaterStates(StatesGroup):
    waiting_for_amount = State()


class WorkoutStates(StatesGroup):
    waiting_for_amount = State()


class CaloriesStates(StatesGroup):
    waiting_for_query = State()
    browsing_results = State()
    setting_calories = State()
    waiting_for_amount = State()
