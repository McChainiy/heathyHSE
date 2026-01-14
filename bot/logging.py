from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any
from services.logger import logger

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable,
        event: Message,
        data: Dict[str, Any],
    ):
        if isinstance(event, Message):
            text = event.text or "<no text>"
            logger.info(f"Получено сообщение: {text}")

        return await handler(event, data)
