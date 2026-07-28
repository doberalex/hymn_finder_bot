import asyncio
import os
import json

from aiogram import Router
from aiogram.types import Message

from app.keyboards.main_keyboard import get_main_keyboard
from app.keyboards.admin_keyboard import get_admin_keyboard
from app.db import db
from app.services.stats_service import get_bot_stats
from app.storage import restart_data
from app.config import ADMIN_ID

router = Router()


@router.message()
async def admin_handler(message: Message, user_mode: dict, user_songbook: dict):
    text = message.text
    user_id = message.from_user.id

    # ⚙️ вход в админку
    if text == "⚙️ Админ":
        if user_id != ADMIN_ID:
            await message.answer("⛔ Нет доступа")
            return True

        user_mode[user_id] = "admin"

        await message.answer(
            "⚙️ Админ панель",
            reply_markup=get_admin_keyboard()
        )
        return True

    # ⬅️ выход
    if text == "⬅️ В основное меню":
        user_mode.pop(user_id, None)
        user_songbook.pop(user_id, None)

        await message.answer(
            "🏠 Главное меню",
            reply_markup=get_main_keyboard(
                user_id,
                user_mode,
                user_songbook
            )
        )
        return True

    # 🔄 рестарт
    if text == "🔄 Рестарт бота":
        if user_id != ADMIN_ID:
            await message.answer("⛔ Нет доступа")
            return True

        await message.answer("♻️ Перезапуск бота...")

        with open("restart.tmp", "w") as f:
            json.dump({
                "user_id": user_id
            }, f)

        try:
            db.pool.close()
        except:
            pass

        await asyncio.sleep(1)

        os.execl(os.sys.executable, os.sys.executable, *os.sys.argv)

    # 📊 статистика
    if text == "📊 Статистика":
        if user_id != ADMIN_ID:
            await message.answer("⛔ Нет доступа")
            return True

        stats = await get_bot_stats()

        top_text = ""

        for i, row in enumerate(stats["top_queries"], start=1):
            top_text += (
                f"{i}. {row['normalized_query']} — "
                f"{row['total']}\n"
            )

        mode_map = {
            "all": "🌍 Вся база",
            "songbook": "📂 Сборники",
            "inline": "📖 Inline"
        }

        mode_text = ""

        for row in stats["modes"]:
            mode_name = mode_map.get(
                row["mode"],
                row["mode"]
            )

            mode_text += (
                f"{mode_name} — "
                f"{row['total']}\n"
            )

        text_result = (
            "📊 <b>Статистика бота</b>\n\n"

            f"📚 <b>База гимнов</b>\n"
            f"• Сборников: {stats['songbooks']}\n"
            f"• Гимнов: {stats['hymns']}\n\n"

            f"👥 Пользователей: "
            f"{stats['users']}\n"

            f"🔍 Всего запросов: "
            f"{stats['searches']}\n"

            f"📅 Запросов сегодня: "
            f"{stats['today']}\n"

            f"⚡ Средний response: "
            f"{stats['avg_time']} сек\n\n"

            f"🔥 <b>ТОП запросов:</b>\n"
            f"{top_text}\n"

            f"📚 <b>Режимы:</b>\n"
            f"{mode_text}"
        )

        await message.answer(
            text_result,
            parse_mode="HTML"
        )

        return True

    return False