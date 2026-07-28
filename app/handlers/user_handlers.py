import time

import aiomysql

from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

from aiogram.filters import CommandStart, Command

from app.db import db

from app.storage import (
    user_mode,
    user_songbook
)

from app.keyboards.main_keyboard import get_main_keyboard

from app.handlers.admin_handlers import admin_handler

from app.services.search_service import (
    search_hymns,
    highlight_text,
    build_preview
)

from app.services.log_service import log_search


# 🚀 /start
async def start_handler(message: Message):
    user_id = message.from_user.id

    user_mode.pop(user_id, None)
    user_songbook.pop(user_id, None)

    await message.answer(
        "👋 Привет!\n\n"
        "🔥 <b>Что я умею:</b>\n\n"
        "🔎 Найду песню по номеру за секунду\n"
        "📝 Пойму даже по кусочку текста\n"
        "📚 Работаю с разными сборниками\n"
        "⚡ Отдаю результат сразу, без ожиданий\n\n"
        "Выбери режим поиска 👇",
        parse_mode="HTML",
        reply_markup=get_main_keyboard(
            user_id,
            user_mode,
            user_songbook
        )
    )


# 📖 /help
async def help_handler(message: Message):
    await message.answer(
        "📖 <b>Как пользоваться:</b>\n\n"
        "1. Выбери режим\n"
        "2. Введи текст или номер песни",
        parse_mode="HTML"
    )


# ℹ️ /about
async def about_handler(message: Message):
    await message.answer(
        "ℹ️ <b>О боте</b>\n\n"
        "HymnFinderBot — твой помощник в поиске песен 📖🎶\n\n"
        "👨‍💻 Сделал: <a href='https://t.me/doberalex'>Александр</a>\n"
        "🚀 Версия: 1.0\n\n"
        "💬 Есть идеи или что улучшить? Пиши — не стесняйся 😉",
        parse_mode="HTML",
        disable_web_page_preview=True
    )


# 📂 получить сборники
async def get_songbooks():
    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT id, title FROM songbooks ORDER BY title"
            )
            return await cursor.fetchall()


# 🌟 Показываем текущий режим
async def get_mode_text(user_id):
    mode = user_mode.get(user_id, "all")

    if mode == "songbook":
        songbook_id = user_songbook.get(user_id)

        if not songbook_id:
            return "📌 Режим: сборник (не выбран)"

        async with db.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(
                    "SELECT title FROM songbooks WHERE id=%s",
                    (songbook_id,)
                )
                row = await cursor.fetchone()

        if row:
            return f"📌 Режим: {row['title']}"

        return "📌 Режим: сборник"

    return "📌 Режим: вся база"


# 🔍 поиск
async def handle_search(message: Message):
    user_id = message.from_user.id

    mode = user_mode.get(user_id, "all")

    query = message.text

    songbook_id = (
        user_songbook.get(user_id)
        if mode == "songbook"
        else None
    )

    log_mode = "songbook" if songbook_id else "all"

    if mode == "songbook" and not songbook_id:
        await message.answer("Сначала выбери сборник 📂")
        return

    start_time = time.time()

    # 🔥 сначала точный поиск
    results = await search_hymns(
        query,
        songbook_id=songbook_id,
        strict=True
    )

    exact_found = bool(results)

    # если нет — обычный
    if not results:
        results = await search_hymns(
            query,
            songbook_id=songbook_id
        )

    response_time = round(time.time() - start_time, 2)

    # логирование
    await log_search(
        message.from_user,
        query,
        songbook_id,
        len(results),
        log_mode,
        response_time
    )

    if not results:
        await message.answer("Ничего не найдено 😔")
        return

    # 💬 сообщение пользователю
    if exact_found:
        await message.answer(
            "🔎 Найдено точное совпадение:"
        )
    else:
        await message.answer(
            "🔎 Точных совпадений нет, показываю похожие:"
        )

    # 🔥 вывод результатов
    for row in results:
        preview_text = build_preview(
            row['content'],
            query
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📖 Показать полностью",
                        callback_data=f"full_{row['id']}"
                    )
                ]
            ]
        )

        if row.get("tune"):
            tune_text = (
                f"\n🎼 Тональность: "
                f"{row['tune']}\n\n"
            )
        else:
            tune_text = "\n\n"

        await message.answer(
            f"📖 <b>{row['number']}. "
            f"{row['title']}</b>\n"
            f"📂 {row['songbook'] or 'Без сборника'}"
            f"{tune_text}"
            f"{preview_text}",
            parse_mode="HTML",
            reply_markup=keyboard
        )


# 🚀 основной обработчик сообщений
async def main_handler(message: Message):
    text = message.text
    user_id = message.from_user.id

    # ⚙️ admin handlers
    handled = await admin_handler(
        message,
        user_mode,
        user_songbook
    )

    if handled:
        return

    # --- выбор режима ---
    if text == "📂 Искать по сборнику":
        user_mode[user_id] = "songbook"

        songbooks = await get_songbooks()

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=sb["title"],
                        callback_data=f"sb_{sb['id']}"
                    )
                ]
                for sb in songbooks
            ]
        )

        await message.answer(
            "📂 Выбери сборник:",
            reply_markup=keyboard
        )

        await message.answer(
            "⬇️ Навигация:",
            reply_markup=get_main_keyboard(
                user_id,
                user_mode,
                user_songbook
            )
        )

        return

    # 🌍 вся база
    if text == "🌍 Искать по всей базе":
        user_mode[user_id] = "all"
        user_songbook.pop(user_id, None)

        await message.answer(
            "🌍 Режим: поиск по всей базе\nВведи текст 🔍",
            reply_markup=get_main_keyboard(
                user_id,
                user_mode,
                user_songbook
            )
        )

        return

    # ❌ сброс
    if text == "❌ Сбросить сборник":
        user_songbook.pop(user_id, None)
        user_mode[user_id] = "all"

        await message.answer(
            "🌍 Сборник сброшен",
            reply_markup=get_main_keyboard(
                user_id,
                user_mode,
                user_songbook
            )
        )

        return

    # ⬅️ назад
    if text == "⬅️ Назад":
        user_mode.pop(user_id, None)
        user_songbook.pop(user_id, None)

        await start_handler(message)
        return

    # --- дефолт режим ---
    if user_id not in user_mode:
        user_mode[user_id] = "all"

    # --- поиск ---
    await handle_search(message)


# 📂 выбор сборника
async def choose_songbook(callback: CallbackQuery):
    songbook_id = int(
        callback.data.replace("sb_", "")
    )

    user_id = callback.from_user.id

    user_songbook[user_id] = songbook_id
    user_mode[user_id] = "songbook"

    await callback.message.answer(
        "📂 Сборник выбран!\nВведи текст 🔍",
        reply_markup=get_main_keyboard(
            user_id,
            user_mode,
            user_songbook
        )
    )

    await callback.answer()


# 📖 полный текст
async def show_full_text(callback: CallbackQuery):
    hymn_id = callback.data.replace(
        "full_",
        ""
    )

    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                """
                SELECT
                    h.title,
                    h.content,
                    h.number,
                    h.tune,
                    s.title AS songbook
                FROM hymns h
                LEFT JOIN songbooks s
                    ON h.songbook_id = s.id
                WHERE h.id=%s
                """,
                (hymn_id,)
            )

            row = await cursor.fetchone()

    if row:
        if row.get("tune"):
            tune_text = (
                f"\n🎼 Тональность: "
                f"{row['tune']}\n\n"
            )
        else:
            tune_text = "\n\n"

        await callback.message.answer(
            f"📖 <b>{row['number']}. "
            f"{row['title']}</b>\n"
            f"📂 {row['songbook'] or 'Без сборника'}"
            f"{tune_text}"
            f"{row['content']}",
            parse_mode="HTML"
        )

    else:
        await callback.message.answer(
            "Не удалось найти текст 😔"
        )

    await callback.answer()