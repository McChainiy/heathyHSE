import aiohttp
from bot.config import OPENWEATHER_API
import requests


class WeatherService:
    url = "https://api.openweathermap.org/data/2.5/weather"
    async def check_weather(self, city_to_check: str) -> int:
        params = {
            "q": city_to_check,
            "appid": OPENWEATHER_API,
            "units": "metric",
            "lang": "ru"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, params=params) as response:
                if response.status != 200:
                    return None
                response = await response.json()
                temp = response['main']['temp']
                return temp
            
    def check_weather_sync(self, city_to_check: str) -> int:
        params = {
            "q": city_to_check,
            "appid": OPENWEATHER_API,
            "units": "metric",
            "lang": "ru"
        }
        try:
            response = requests.get(self.url, params=params)
            if response.status != 200:
                return None
            response = response.json()
            temp = response['main']['temp']
        except:
            temp = None
        return temp