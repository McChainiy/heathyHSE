import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from bot.config import API_TOKEN

from bot.handlers import router

from bot.logging import LoggingMiddleware
from services.logger import logger

import logging

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

dp.include_router(router)

logging.getLogger("aiogram.event").setLevel(logging.WARNING)
logging.getLogger("aiogram.dispatcher").setLevel(logging.WARNING)

async def main():
    # print("Бот запущен!")
    dp.message.middleware(LoggingMiddleware())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())