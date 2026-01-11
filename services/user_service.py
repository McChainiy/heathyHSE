from db.models.user import User
from db.models.user_history import UserHistory
from db.models.user_log import UserLog

from datetime import date, timedelta, datetime, time

from sqlalchemy.exc import IntegrityError

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
import logging
from tempfile import NamedTemporaryFile


from random import randrange


logging.getLogger("matplotlib").setLevel(logging.WARNING)
matplotlib.use("Agg")

low_cal_snacks = {
    "огурец": 16,
    "помидор": 18,
    "сельдерей": 16,
    "редис": 19,
    "листовой салат": 15,
    "кабачок": 17,
    "болгарский перец": 20,
    "арбуз": 30,
    "дыня": 34,
    "клубника": 32,
    "малина": 52,
    "черника": 57,
    "яблоко": 52,
    "груша": 57,
    "апельсин": 47,
    "грейпфрут": 42,
    "киви": 61,
    "йогурт 0%": 59,
    "кефир 1%": 41,
    "творог 0%": 72,
    "яичный белок": 52,
    "куриная грудка (отварная)": 110,
    "тунец в собственном соку": 96,
    "рисовые хлебцы": 35,
    "попкорн без масла": 31
}

def find_closest_snack(target_kcal: int, snacks: dict) -> tuple:
    return min(
        snacks.items(),
        key=lambda item: abs(item[1] - target_kcal)
    )


def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)


class UserService:
    def __init__(self, session):
        self.session = session

    def get_or_create(self, tg_id: int):
        user = self.session.query(User).filter(User.tg_id == tg_id).first()
        
        if user:
            return user, False

        user = User(tg_id=tg_id, cur_date=date.today())
        self.session.add(user)
        try:
            self.session.commit()
            return user, True
        except IntegrityError:
            self.session.rollback()
            return self.session.query(User).filter(User.tg_id == tg_id).first(), False
        
    def update_user(self, tg_id: int, **fields):
        user = self.session.query(User).filter(User.tg_id == tg_id).first()
        if not user:
            return None

        for key, value in fields.items():
            if hasattr(user, key):
                setattr(user, key, value)

        self.session.commit()
        return user
    
    def get_profile(self, tg_id: int) -> User | None:
        user = (
            self.session
            .query(User)
            .filter(User.tg_id == tg_id)
            .first()
        )
        if user is None:
            return None
        
        # # рандомная дата для тестов
        # d1 = datetime.strptime('1/1/2000 1:30 PM', '%m/%d/%Y %I:%M %p')
        # d2 = datetime.strptime('1/1/2024 4:50 AM', '%m/%d/%Y %I:%M %p')
        # curdate = random_date(d1, d2)
        # #


        curdate = date.today()
        if user.cur_date != curdate:
            user_history = UserHistory(
                tg_id=user.tg_id,
                water_goal=user.water_goal,
                calorie_goal=user.calorie_goal,
                logged_water=user.logged_water,
                logged_calories=user.logged_calories,
                burned_calories=user.burned_calories,
                date=user.cur_date,
            )
            self.session.add(user_history)

            user.logged_water = 0
            user.logged_calories = 0
            user.burned_calories = 0
            user.added_water = 0
            user.cur_date = date.today()

            self.session.commit()
            self.session.refresh(user)
        return user

    def delete_profile(self, tg_id: int) -> bool:
        user = (
            self.session
            .query(User)
            .filter(User.tg_id == tg_id)
            .first()
        )

        if not user:
            return False

        self.session.delete(user)
        self.session.commit()
        return True
    
    def add_water(self, tg_id: int, amount: int):
        user = self.get_profile(tg_id)
        if not user:
            return False
        user.logged_water += amount
        self.create_log(user, 'add_water', amount)
        self.session.commit()
        return True
    
    def add_workout(self, tg_id: int, amount: int):
        user = self.get_profile(tg_id)
        if not user:
            return False
        user.burned_calories += amount * 10
        user.added_water += (amount / 30) * 200
        self.create_log(user, 'add_workout', amount)
        self.session.commit()
        return True

    def add_calories(self, tg_id: int, amount: int):
        user = self.get_profile(tg_id)
        if not user:
            return False
        user.logged_calories += amount
        self.create_log(user, 'add_calories', amount)
        self.session.commit()
        return True
    
    def create_log(self, user: User, action: str, value: float = 0):
        user_log = UserLog(
                tg_id=user.tg_id,
                created_at=datetime.now(),
                today_water=user.logged_water - user.added_water,
                today_calories=user.logged_calories - user.burned_calories,
                action=action,
                value=value,
            )
        self.session.add(user_log)
        self.session.commit()
        self.session.refresh(user)
        return True
    
    def build_today_stats(self, tg_id: int):
        today = date.today()
        start_dt = datetime.combine(today, time.min)
        end_dt = datetime.combine(today, time.max) 
        today_logs = (
                self.session
                .query(UserLog)
                .filter(UserLog.tg_id == tg_id)
                .filter(UserLog.value != 0)
                .filter(UserLog.created_at >= start_dt)
                .filter(UserLog.created_at <= end_dt)
                .all()
            )

        x = []
        y = []

        for log in today_logs:
            # x.append(log.created_at.strftime("%H:%M"))
            x.append(log.created_at)
            y.append((log.today_water, log.today_calories))

        y1 = [i[0] for i in y]
        y2 = [i[1] for i in y]

        user = self.get_profile(tg_id)
        
        plt.figure(figsize=(12, 6))
        plt.plot(x, y1, marker='o', label='Вода', color='blue', linewidth=2)
        plt.plot(x, y2, marker='s', label='Калории', color='orange', linewidth=2)

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
        plt.xticks(rotation=45)

        plt.axhline(
            y=user.water_goal,
            color='blue',
            linestyle='--',
            linewidth=2,
            label='Цель по воде'
        )

        plt.axhline(
            y=user.calorie_goal,
            color='orange',
            linestyle='--',
            linewidth=2,
            label='Цель по калориям'
        )

        plt.title('Данные за сутки', fontsize=16)
        plt.xlabel('Время', fontsize=14)
        plt.ylabel('Значения', fontsize=14)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend(fontsize=12)

        start_day = datetime.combine(today, datetime.min.time())
        end_day = datetime.combine(today, datetime.max.time())
        plt.xlim(start_day, end_day)

        plt.tight_layout()

        tmp_file = NamedTemporaryFile(suffix=".png", delete=False)
        plt.savefig(tmp_file.name)
        plt.close()
        return tmp_file.name
    

    # def build_history_stats(self, tg_id: int):
    #     today_logs = (
    #             self.session
    #             .query(UserHistory)
    #             .filter(UserHistory.tg_id == tg_id)
    #             .all()
    #         )
        
    def get_history(self, tg_id: int):
        hist = (
                self.session
                .query(UserHistory)
                .filter(UserHistory.tg_id == tg_id)
                .all()
            )
        history = {}
        for day in hist:
            history[day.date.strftime("%d.%m.%Y")] = (day.water_goal, day.calorie_goal,
                                                   day.logged_water, day.logged_calories, day.burned_calories)
        return history
    
    def get_recommendation(self, tg_id: int):
        activity_goal = 60
        waking = 7
        bedtime = 23
        
        hour = datetime.now().hour
        if hour < waking - 1 and hour > bedtime - 3:
            return "Время для сна, сейчас лучше воздержаться от употребления еды или упражнений."
        user = self.get_profile(tg_id)
        time_value = hour * 4 / (24 * 4)
        # print(time_value)
        cur_water_diff = int(user.water_goal * time_value + user.added_water) - int(user.logged_water)
        # water_diff = int(user.water_goal + user.added_water) - int(user.logged_water)
        cur_calorie_diff = int(user.calorie_goal * time_value + user.burned_calories) - int(user.logged_calories)
        activity_time_diff = activity_goal * time_value - user.burned_calories / 10
        
        # print(cur_water_diff, cur_calorie_diff, user.burned_calories / 10)
        text = []
        if 500 > cur_water_diff > 0:
            if activity_time_diff > 0:
                text.append(f"Немного физической активности не помешает ({activity_time_diff} минут активности).\n"
                            f"Не забудь взять бутылку воды ({cur_water_diff} мл)")
            else:
                text.append(f"Физическая активность пока что в норме\n"
                            f"Стоит выпить немного воды ({cur_water_diff} мл).")
        elif 1500 > cur_water_diff > 500:
            text.append(f'Пожалуйста, выпей воды. Это важно! ({cur_water_diff} мл)')
        elif cur_water_diff > 1500:
            text.append(f'😡 Критически низкий уровень воды (нужно еще {cur_water_diff} мл). СЕЙЧАС ЖЕ ИДИ ПИТЬ ВОДУ 😡')
        else:
            if activity_time_diff > 0:
                text.append(f"Немного физической активности не помешает ({activity_time_diff} минут активности).\n"
                            f"Не забудь взять бутылку воды ({cur_water_diff} мл)")
            else:
                text.append('Физическая активность пока что в норме\nУровень воды в порядке. Продолжай в том же духе!')
        if 300 > cur_calorie_diff > 0:
            product = find_closest_snack(cur_calorie_diff, low_cal_snacks)
            text.append(f"Калории в порядке, можно перекусить! Например: {product[0]} - {product[1]} ккал")
        elif cur_calorie_diff > 300:
            text.append(f"Нужно еще {cur_calorie_diff} калорий")
            if time_value < 0.3:
                text.append(f"Пора завтракать!")
            elif 0.3 < time_value < 0.7:
                text.append(f"Пора обедать!")
            else:
                text.append(f"Пора ужинать!")
        else:
            text.append(f"Калории выше нормы! Позанимайся спортом ({max(-cur_calorie_diff / 10, 5)} минут) и не забудь взять воду!")

        return '\n'.join(text)