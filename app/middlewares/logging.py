from __future__ import annotations
import time
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from ..services import analytics

class EventLogger(BaseMiddleware):
    async def __call__(self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject, data: Dict[str, Any]
    ) -> Any:
        try:
            if isinstance(event, Message):
                uid = event.from_user.id if event.from_user else 0
                await analytics.log_event(uid, "message", (event.text or "")[:200])
            elif isinstance(event, CallbackQuery):
                uid = event.from_user.id if event.from_user else 0
                await analytics.log_event(uid, "callback", (event.data or "")[:200])
        except Exception:
            pass
        return await handler(event, data)

class RateLimit(BaseMiddleware):
    def __init__(self, limit: int = 6, interval: int = 5):
        self.limit = limit
        self.interval = interval
        self.bucket: Dict[int, list[float]] = {}

    async def __call__(self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject, data: Dict[str, Any]
    ) -> Any:
        uid = None
        if isinstance(event, Message) and event.from_user:
            uid = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            uid = event.from_user.id

        if uid:
            now = time.monotonic()
            arr = [t for t in self.bucket.get(uid, []) if now - t < self.interval]
            if len(arr) >= self.limit:
                if isinstance(event, Message):
                    await event.answer("Слишком часто. Подожди пару секунд.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("Слишком часто", show_alert=False)
                self.bucket[uid] = arr
                return
            arr.append(now)
            self.bucket[uid] = arr

        return await handler(event, data)
