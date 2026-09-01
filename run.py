import asyncio
import os
import json
import socket
import sys
import time
import traceback

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import CommandStart, Command
from aiohttp.resolver import DefaultResolver
from app.db.db import connect_db
from app.handlers.inline_handlers import inline_search
from app.handlers.user_handlers import (
    start_handler,
    help_handler,
    about_handler,
    main_handler,
    choose_songbook,
    show_full_text,
    choose_language,
    favorite_callback,
    quick_callback,
    scope_callback,
)
from app.storage import restart_data
from app.keyboards.admin_keyboard import get_admin_keyboard
from app.config import TELEGRAM_PROXY_URL, TOKEN
from app.security import RateLimitMiddleware


TELEGRAM_API_IP = "149.154.167.220"


class TelegramIPv4Resolver:
    def __init__(self) -> None:
        self._default = DefaultResolver()

    async def resolve(
        self,
        host: str,
        port: int = 0,
        family: socket.AddressFamily = socket.AF_INET,
    ) -> list[dict]:
        if host == "api.telegram.org":
            return [
                {
                    "hostname": host,
                    "host": TELEGRAM_API_IP,
                    "port": port,
                    "family": socket.AF_INET,
                    "proto": socket.IPPROTO_TCP,
                    "flags": 0,
                }
            ]

        return await self._default.resolve(host, port, family)

    async def close(self) -> None:
        await self._default.close()


def create_bot() -> Bot:
    session = AiohttpSession(proxy=TELEGRAM_PROXY_URL or None)
    session._connector_init["family"] = socket.AF_INET

    if not TELEGRAM_PROXY_URL:
        session._connector_init["resolver"] = TelegramIPv4Resolver()

    return Bot(token=TOKEN, session=session)


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.message.outer_middleware(RateLimitMiddleware(limit=8, period=10))
    dp.callback_query.outer_middleware(RateLimitMiddleware(limit=15, period=10))
    dp.inline_query.outer_middleware(RateLimitMiddleware(limit=20, period=10))
    dp.inline_query.register(inline_search)

    # 🚀 handlers
    dp.message.register(
        start_handler,
        CommandStart()
    )

    dp.message.register(
        help_handler,
        Command("help")
    )

    dp.message.register(
        about_handler,
        Command("about")
    )

    dp.message.register(main_handler)

    dp.callback_query.register(
        choose_songbook,
        lambda c: c.data.startswith("sb_")
    )

    dp.callback_query.register(
        show_full_text,
        lambda c: c.data.startswith("full_")
    )
    dp.callback_query.register(
        choose_language,
        lambda c: c.data.startswith("lang_")
    )
    dp.callback_query.register(
        favorite_callback,
        lambda c: c.data.startswith("fav_")
    )
    dp.callback_query.register(
        quick_callback,
        lambda c: c.data.startswith("quick_")
    )
    dp.callback_query.register(
        scope_callback,
        lambda c: c.data.startswith("scope_")
    )
    return dp


# 🚀 запуск
async def main():
    bot = create_bot()
    dp = create_dispatcher()
    await connect_db()

    # 🔄 post restart notify
    if os.path.exists("restart.tmp"):

        try:
            with open("restart.tmp", "r") as f:
                data = json.load(f)

            user_id = data.get("user_id")

            if user_id:
                await bot.send_message(
                    user_id,
                    "✅ Бот успешно перезапущен",
                    reply_markup=get_admin_keyboard()
                )

            os.remove("restart.tmp")

        except Exception as e:
            print("Restart notify error:", e)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
            break
        except KeyboardInterrupt:
            raise
        except Exception:
            traceback.print_exc()
            print("Bot stopped after an error. Restarting process in 30 seconds...", flush=True)
            time.sleep(30)
            os.execv(sys.executable, [sys.executable, *sys.argv])
