import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)

aiohttp_logger = logging.getLogger("aiohttp")
aiohttp_logger.setLevel(logging.DEBUG)

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
OPENWEATHER_API = os.getenv("OPENWEATHER_API")


if not API_TOKEN:
    raise NameError