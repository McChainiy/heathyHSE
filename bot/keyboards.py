from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

BTN_LOG_WATER = "💧 Добавить воду"
BTN_LOG_FOOD = "🥑 Добавить еду"
BTN_LOG_WORKOUT = "🏃‍♂️ Добавить тренировку"
BTN_CHECK_PROGRESS = "📊 Прогресс"
BTN_GET_PROFILE = "👤 Профиль"

BTN_CHECK_HISTORY = "📋 История"
BTN_GET_RECOMMENDATION = "📝 Рекомендации"
BTN_BACK_TO_MAIN = "⬅️ Назад"


BTN_START = '/start'
BTN_HELP = '/help'
BTN_SET_PROFILE = '/set_profile'

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_GET_PROFILE), KeyboardButton(text=BTN_CHECK_PROGRESS)],
        [KeyboardButton(text=BTN_LOG_FOOD), KeyboardButton(text=BTN_LOG_WATER), KeyboardButton(text=BTN_LOG_WORKOUT)],
    ],
    resize_keyboard=True
)

profile_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_CHECK_HISTORY), KeyboardButton(text=BTN_GET_RECOMMENDATION)],
        [KeyboardButton(text=BTN_BACK_TO_MAIN)],
    ],
    resize_keyboard=True
)

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_START)],
        [KeyboardButton(text=BTN_HELP), 
         KeyboardButton(text=BTN_SET_PROFILE)],
    ],
    resize_keyboard=True
)

def build_products_keyboard(products, page, total_pages):
    keyboard = []

    for i, product in enumerate(products):
        keyboard.append([
            InlineKeyboardButton(
                text=product["name"],
                callback_data=f"food:{i}"
            )
        ])

    nav = []

    if page > 1:
        nav.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data="page:prev"
            )
        )

    nav.append(
        InlineKeyboardButton(
            text=f"{page}/{total_pages}",
            callback_data="noop"
        )
    )

    if page < total_pages:
        nav.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data="page:next"
            )
        )

    keyboard.append(nav)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)