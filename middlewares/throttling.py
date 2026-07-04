import time
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, slow_mode_delay: float = 0.5):
        self.cache = {}
        self.delay = slow_mode_delay
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id
        now = time.time()
        
        if user_id in self.cache:
            last_time = self.cache[user_id]
            if now - last_time < self.delay:
                if isinstance(event, CallbackQuery):
                    await event.answer("⚠️ Tezlikni kamaytiring! / Помедленнее!", show_alert=False)
                return
        
        self.cache[user_id] = now
        return await handler(event, data)
