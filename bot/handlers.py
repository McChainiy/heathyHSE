from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardRemove, InputFile, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from db.db import get_session

from bot.states import ProfileStates, WaterStates, CaloriesStates, WorkoutStates
from bot.keyboards import main_kb, build_products_keyboard, start_kb, profile_kb
from bot.keyboards import BTN_GET_PROFILE, BTN_CHECK_PROGRESS, BTN_CHECK_HISTORY, BTN_GET_RECOMMENDATION, BTN_BACK_TO_MAIN, BTN_UPDATE_PROFILE
from bot.keyboards import BTN_LOG_FOOD, BTN_LOG_WATER, BTN_LOG_WORKOUT

from services.user_service import UserService
from services.food_service import FoodService
from services.weather_service import WeatherService

import os

router = Router()


### /help и /start

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(f"/start - создание пользователя",
                        f"/set_profile - настройка профиля",
                        f"/delete_profile - удаление профиля",
                        f"/get_profile - просмотр профиля",
                        f"/log_water - добавление воды",
                        f"/log_food - добавление еды",
                        f"/log_workout - добавление тренировки",
                        f"/check_progress - просмотр прогресса",
                        f"/check_history - просмотр истории",
                        f"/get_recommendation - получить рекомендацию",
                        reply_markup=start_kb)

@router.message(Command("start"))
async def cmd_start(message: Message):
    with get_session() as session:
        service = UserService(session)
        user, created = service.get_or_create(message.from_user.id)
    if created:
        await message.answer("Добро пожаловать! 🎉", reply_markup=start_kb)
    else:
        await message.answer("Вы уже зарегистрированы!", reply_markup=main_kb)


### /set_profile

### /get_profile
@router.message(F.text == BTN_UPDATE_PROFILE)
async def set_profile_btn(message: Message, state: FSMContext):
    await start_profile(message=message, state=state)

@router.message(Command("set_profile"))
async def start_profile(message: Message, state: FSMContext):
    with get_session() as session:
        service = UserService(session)
        user = service.get_profile(message.from_user.id)
    if not user:
        await message.answer("❌ Профиль не найден. Используйте /start", reply_markup=start_kb)
        return
    await state.clear()
    await state.set_state(ProfileStates.weight)
    await message.answer("Введите ваш вес (в кг):", reply_markup=ReplyKeyboardRemove())

@router.message(ProfileStates.weight)
async def set_weight(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число (кг):")
        return

    await state.update_data(weight=int(message.text))
    await state.set_state(ProfileStates.height)
    await message.answer("Введите ваш рост (в см):")

@router.message(ProfileStates.height)
async def set_height(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число (см):")
        return

    await state.update_data(height=int(message.text))
    await state.set_state(ProfileStates.age)
    await message.answer("Введите ваш возраст:")

@router.message(ProfileStates.age)
async def set_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число:")
        return

    await state.update_data(age=int(message.text))
    await state.set_state(ProfileStates.activity)
    await message.answer("Сколько минут активности у вас в день?")

@router.message(ProfileStates.activity)
async def set_activity(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число (минуты):")
        return

    await state.update_data(activity=int(message.text))
    await state.set_state(ProfileStates.city)
    await message.answer("В каком городе вы находитесь?")

@router.message(ProfileStates.city)
async def set_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)

    data = await state.get_data()
    await state.clear()
    weather_service = WeatherService()
    temp = await weather_service.check_weather(data['city'])
    # расчет воды
    water_goal = 30 * data['weight'] + 500 * (data['activity'] / 30) + 500
    # расчет калорий
    calorie_goal = 10 * data["weight"] + 6.25 * data["height"] - 5 * data["age"]

    print(temp)
    if temp is None or temp < 10:
        pass
    elif 10 < temp < 20:
        water_goal += 10 * data['weight']
        calorie_goal = 0.95 * calorie_goal
    else: 
        water_goal += 15 * data['weight']
        calorie_goal = 0.9 * calorie_goal
    with get_session() as session:
        service = UserService(session)
        service.update_user(
            tg_id=message.from_user.id,
            weight=data["weight"],
            height=data["height"],
            age=data["age"],
            activity=data["activity"],
            city=data["city"],
            water_goal=water_goal,
            calorie_goal=calorie_goal
        )

    await message.answer(f"✅ Профиль успешно сохранён!", reply_markup=main_kb)


### /get_profile
@router.message(F.text == BTN_GET_PROFILE)
async def get_profile_btn(message: Message, state: FSMContext):
    await get_profile(message=message)

@router.message(Command("get_profile"))
async def get_profile(message: Message):
    with get_session() as session:
        service = UserService(session)
        user = service.get_profile(message.from_user.id)
        if user:
            service.create_log(user, 'get_profile')
    if not user:
        await message.answer("❌ Профиль не найден. Используйте /start", reply_markup=start_kb)
        return
    if not user.age:
        await message.answer("❌ Профиль не настроен. Используйте /set_profile", reply_markup=start_kb)
        return
    calorie_goal = f"{user.calorie_goal:.1f}" if user.calorie_goal else "-"
    water_goal = f"{user.water_goal:.1f}" if user.water_goal else "-"
    text = (
        "Ваш профиль:\n\n"
        f"⚖️ Вес: {user.weight} кг\n"
        f"📏 Рост: {user.height} см\n"
        f"🎂 Возраст: {user.age}\n"
        f"🏃 Активность: {user.activity} мин/день\n"
        f"🌍 Город: {user.city}\n"
        f"🔥 Цель калорий: {calorie_goal}\n"
        f"💧 Цель воды: {water_goal}"
    )
    await message.answer(text, reply_markup=profile_kb)


### /delete_profile
@router.message(Command("delete_profile"))
async def delete_profile_confirm(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да, удалить", callback_data="delete_yes"),
                InlineKeyboardButton(text="❌ Нет, отменить", callback_data="delete_no")
            ]
        ]
    )
    await message.answer("Вы уверены, что хотите удалить профиль?", reply_markup=keyboard)

@router.callback_query(lambda c: c.data in ["delete_yes", "delete_no"])
async def process_delete_callback(callback: CallbackQuery):
    tg_id = callback.from_user.id

    if callback.data == "delete_no":
        await callback.message.edit_text("❌ Удаление отменено", reply_markup=main_kb)
        await callback.answer()
        return

    with get_session() as session:
        service = UserService(session)
        deleted = service.delete_profile(tg_id)

    if deleted:
        await callback.message.edit_text("🗑 Профиль успешно удалён")
        await callback.message.answer("Нажмите /start, чтобы создать профиль заново", reply_markup=start_kb)

    else:
        await callback.message.edit_text("❌ Профиль не найден", reply_markup=start_kb)

    await callback.answer()


### /log_water

@router.message(F.text == BTN_LOG_WATER)
async def log_water_btn(message: Message, state: FSMContext):
    await log_water(message=message, state=state)

@router.message(Command("log_water"))
async def log_water(message: Message, state: FSMContext):
    parts = message.text.split()

    with get_session() as session:
        service = UserService(session)
        user = service.get_profile(message.from_user.id)
    if not user:
        await message.answer("❌ Профиль не найден. Используйте /start", reply_markup=start_kb)
        return
    if not user.age:
        await message.answer("❌ Профиль не настроен. Используйте /set_profile", reply_markup=start_kb)
        return

    if len(parts) == 2 and parts[1].isdigit():
        water = int(parts[1])

        with get_session() as session:
            service = UserService(session)
            service.add_water(message.from_user.id, water)

        await message.answer(f"✅ Записано {water} мл воды", reply_markup=main_kb)
        return

    await state.set_state(WaterStates.waiting_for_amount)
    await message.answer("💧 Введите количество воды (в мл):", reply_markup=ReplyKeyboardRemove())

@router.message(WaterStates.waiting_for_amount)
async def log_water_amount(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число (мл):")
        return

    water = int(message.text)

    with get_session() as session:
        service = UserService(session)
        service.add_water(message.from_user.id, water)

    await state.clear()
    await message.answer(f"✅ Записано {water} мл воды", reply_markup=main_kb)


### /log_food

@router.message(F.text == BTN_LOG_FOOD)
async def log_food_btn(message: Message, state: FSMContext):
    await log_food_start(message=message, state=state)

@router.message(Command("log_food"))
async def log_food_start(message: Message, state: FSMContext):
    parts = message.text.split()

    with get_session() as session:
        service = UserService(session)
        user = service.get_profile(message.from_user.id)

    if not user:
        await message.answer("❌ Профиль не найден. Используйте /start", reply_markup=start_kb)
        return
    if not user.age:
        await message.answer("❌ Профиль не настроен. Используйте /set_profile", reply_markup=start_kb)
        return
    
    if len(parts) >= 2 and message.text != BTN_LOG_FOOD:
        query = parts[1]
        page = 1
        food_service = FoodService()
        products, total_pages = await food_service.search_products(query, page)

        if not products:
            await message.answer("❌ Ничего не найдено", reply_markup=main_kb)
            return

        await state.update_data(
            query=query,
            page=page,
            total_pages=total_pages
        )

        keyboard = build_products_keyboard(products, page, total_pages)

        await state.set_state(CaloriesStates.browsing_results)
        # await message.answer("", reply_markup=ReplyKeyboardRemove())
        await message.answer("⬇️", reply_markup=ReplyKeyboardRemove())
        await message.answer("Выберите продукт:", reply_markup=keyboard)
    else:
        await state.set_state(CaloriesStates.waiting_for_query)
        await message.answer("Введите название продукта:", reply_markup=ReplyKeyboardRemove())


@router.message(CaloriesStates.waiting_for_query)
async def show_products(message: Message, state: FSMContext):
    query = message.text
    page = 1
    food_service = FoodService()
    products, total_pages = await food_service.search_products(query, page)

    if not products:
        await message.answer("❌ Ничего не найдено", reply_markup=main_kb)
        return

    await state.update_data(
        query=query,
        page=page,
        total_pages=total_pages
    )

    keyboard = build_products_keyboard(products, page, total_pages)

    await state.set_state(CaloriesStates.browsing_results)
    await message.answer("Выберите продукт:", reply_markup=keyboard)


@router.callback_query(
    CaloriesStates.browsing_results,
    lambda c: c.data in ["page:prev", "page:next"]
)
async def paginate_products(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    page = data["page"]
    query = data["query"]
    total_pages = data["total_pages"]
    food_service = FoodService()

    if callback.data == "page:prev" and page > 1:
        page -= 1
    elif callback.data == "page:next" and page < total_pages:
        page += 1

    products, _ = await food_service.search_products(query, page)

    await state.update_data(page=page)

    keyboard = build_products_keyboard(products, page, total_pages)
    try:
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    except TelegramBadRequest:
        pass

    await callback.answer()


@router.callback_query(
    CaloriesStates.browsing_results,
    lambda c: c.data.startswith("food:")
)
async def choose_product(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.split(":")[1])

    data = await state.get_data()
    page = data["page"]
    query = data["query"]
    food_service = FoodService()

    products, _ = await food_service.search_products(query, page)
    product = products[index]

    await state.clear()

    try:
        await callback.message.edit_text(
            f"🍽 {product['name']}\n"
            f"🔥 {product['calories']} ккал / 100 г\n\n"
            f"⚖️ Введите количество граммов:"
        )
    except TelegramBadRequest:
        pass
    await state.update_data(
        selected_product=product
    )

    await state.set_state(CaloriesStates.setting_calories)
    await callback.answer()

@router.message(CaloriesStates.setting_calories)
async def set_calories(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число (граммы):")
        return

    grams = int(message.text)
    data = await state.get_data()
    product = data["selected_product"]

    calories = int(product["calories"] * grams / 100)

    with get_session() as session:
        service = UserService(session)
        service.add_calories(message.from_user.id, calories)

    await state.clear()

    await message.answer(
        f"✅ Добавлено:\n"
        f"🍽 {product['name']}\n"
        f"⚖️ {grams} г\n"
        f"🔥 {calories} ккал", 
        reply_markup=main_kb
    )


### /log_workout

@router.message(F.text == BTN_LOG_WORKOUT)
async def log_workout_btn(message: Message, state: FSMContext):
    await log_workout(message=message, state=state)

@router.message(Command("log_workout"))
async def log_workout(message: Message, state: FSMContext):
    parts = message.text.split()

    with get_session() as session:
        service = UserService(session)
        user = service.get_profile(message.from_user.id)

    if not user:
        await message.answer("❌ Профиль не найден. Используйте /start", reply_markup=start_kb)
        return
    if not user.age:
        await message.answer("❌ Профиль не настроен. Используйте /set_profile", reply_markup=start_kb)
        return
    
    if len(parts) >= 2 and parts[-1].isdigit():
        mins = int(parts[-1])

        with get_session() as session:
            service = UserService(session)
            service.add_workout(message.from_user.id, mins)
        if len(parts) == 2:
            answer = f"Записано {mins} минут тренировки - {mins * 10} ккал. Дополнительно: выпейте {mins / 30 * 200:.0f} мл воды"
        else:
            answer = f" {parts[1].capitalize()}: {mins} минут тренировки - {mins * 10} ккал. Дополнительно: выпейте {mins / 30 * 200:.0f} мл воды"
        await message.answer(answer, reply_markup=main_kb)
        return

    await state.set_state(WorkoutStates.waiting_for_amount)
    await message.answer("Введите количество минут тренировки:", reply_markup=ReplyKeyboardRemove())

@router.message(WorkoutStates.waiting_for_amount)
async def log_workout_min(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите количество минут тренировки:")
        return

    mins = int(message.text)

    with get_session() as session:
        service = UserService(session)
        service.add_workout(message.from_user.id, mins)

    await state.clear()
    answer = f"Записано {mins} минут тренировки - {mins * 10} ккал. Дополнительно: выпейте {mins / 30 * 200:.0f} мл воды"
    await message.answer(answer, reply_markup=main_kb)


### /check_progress

@router.message(F.text == BTN_CHECK_PROGRESS)
async def check_progress_btn(message: Message):
    await check_progress(message=message)

@router.message(Command("check_progress"))
async def check_progress(message: Message):
    with get_session() as session:
        service = UserService(session)
        user = service.get_profile(message.from_user.id)
        if user:
            service.create_log(user, 'check_progress')
            img_path = service.build_today_stats(user.tg_id)
    if not user:
        await message.answer("❌ Профиль не найден. Используйте /start", reply_markup=start_kb)
        return
    if not user.age:
        await message.answer("❌ Профиль не настроен. Используйте /set_profile", reply_markup=start_kb)
        return
    
    text = (
        f"Прогресс:\n"
        f"💧 Вода:\n"
        f"- Выпито: {int(user.logged_water - user.added_water)} мл из {int(user.water_goal)} мл.\n"
        f"- Осталось: {int(user.water_goal + user.added_water) - int(user.logged_water)}\n\n"
        f"🔥 Калории:\n"
        f"- Потреблено: {int(user.logged_calories)} ккал из {int(user.calorie_goal)} ккал.\n"
        f"- Сожжено: {int(user.burned_calories)}.\n"
        f"- Баланс: {int(user.logged_calories) - int(user.burned_calories)} ккал."
    )
    await message.answer(text, reply_markup=main_kb)
    if img_path:
        await message.answer_photo(photo=FSInputFile(img_path))
        os.remove(img_path)



### /check_history

@router.message(F.text == BTN_CHECK_HISTORY)
async def check_history_btn(message: Message):
    await check_history(message=message)

@router.message(Command("check_history"))
async def check_history(message: Message):
    with get_session() as session:
        service = UserService(session)
        user = service.get_profile(message.from_user.id)
        if user:
            service.create_log(user, 'check_history')
            history = service.get_history(user.tg_id)
            if len(history) == 0:
                await message.answer("История пуста", reply_markup=profile_kb)
                return
    if not user:
        await message.answer("❌ Профиль не найден. Используйте /start", reply_markup=start_kb)
        return
    if not user.age:
        await message.answer("❌ Профиль не настроен. Используйте /set_profile", reply_markup=start_kb)
        return

    final_text = []
    for key, value in history.items():
        final_text.append(
            f"{key}:\n"
            f"Цель по воде:    {value[0]:>5} | Цель по калориям: {value[1]:>8}\n"
            f"Выпито воды:     {value[2]:>5} | Баланс калорий:   {value[3] - value[4]:>10}\n"
        )
    await message.answer("".join(final_text), reply_markup=profile_kb)



### /get_recommendation
@router.message(F.text == BTN_GET_RECOMMENDATION)
async def get_recommendation_btn(message: Message):
    await get_recommendation(message=message)

@router.message(Command("get_recommendation"))
async def get_recommendation(message: Message):
    with get_session() as session:
        service = UserService(session)
        user = service.get_profile(message.from_user.id)
        if user:
            service.create_log(user, 'get_recommendation')
            rec = service.get_recommendation(user.tg_id)
    if not user:
        await message.answer("❌ Профиль не найден. Используйте /start", reply_markup=start_kb)
        return
    if not user.age:
        await message.answer("❌ Профиль не настроен. Используйте /set_profile", reply_markup=start_kb)
        return
    
    await message.answer(rec, reply_markup=profile_kb)


### /back_to_main
@router.message(F.text == BTN_BACK_TO_MAIN)
async def back_to_main(message: Message):
    await message.answer("Переход в меню...", reply_markup=main_kb)