import time
from collections import defaultdict, deque
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, InlineQuery, Message, TelegramObject

from app.config import ADMIN_ID


class RateLimitMiddleware(BaseMiddleware):
    """Ограничивает частоту запросов и не даёт памяти расти бесконечно."""

    def __init__(self, limit: int, period: float, block_for: float = 15.0) -> None:
        self.limit = limit
        self.period = period
        self.block_for = block_for
        self.requests: dict[int, deque[float]] = defaultdict(deque)
        self.blocked_until: dict[int, float] = {}
        self.last_cleanup = time.monotonic()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None or user.id == ADMIN_ID:
            return await handler(event, data)

        now = time.monotonic()
        self._cleanup(now)

        if self.blocked_until.get(user.id, 0) > now:
            await self._notify(event)
            return None

        queue = self.requests[user.id]
        while queue and queue[0] <= now - self.period:
            queue.popleft()

        if len(queue) >= self.limit:
            self.blocked_until[user.id] = now + self.block_for
            await self._notify(event)
            return None

        queue.append(now)
        return await handler(event, data)

    def _cleanup(self, now: float) -> None:
        if now - self.last_cleanup < 300:
            return

        stale_before = now - max(self.period, self.block_for) - 300
        for user_id, queue in list(self.requests.items()):
            if not queue or queue[-1] < stale_before:
                self.requests.pop(user_id, None)
                self.blocked_until.pop(user_id, None)
        self.last_cleanup = now

    @staticmethod
    async def _notify(event: TelegramObject) -> None:
        if isinstance(event, Message):
            await event.answer("Слишком много запросов. Попробуйте снова через несколько секунд.")
        elif isinstance(event, CallbackQuery):
            await event.answer("Слишком много запросов", show_alert=False)
        elif isinstance(event, InlineQuery):
            await event.answer([], cache_time=5, is_personal=True)
