import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from bot.config import API_TOKEN

from bot.handlers import router

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

dp.include_router(router)

async def main():
    # print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())