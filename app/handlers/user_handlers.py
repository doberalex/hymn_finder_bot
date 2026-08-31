import time
from html import escape

import aiomysql

from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

from aiogram.filters import CommandStart, Command

from app.config import BOT_VERSION
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
from app.services.user_service import (
    LANGUAGES,
    ensure_user,
    get_settings,
    set_catalog_language,
    set_search_scope,
    is_favorite,
    toggle_favorite,
    get_favorites,
    toggle_quick_songbook,
    get_quick_songbooks,
)


def hymn_keyboard(hymn_id: int, favorite: bool = False) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text="★ Удалить из избранного" if favorite else "⭐ В избранное",
        callback_data=f"fav_{hymn_id}",
    )]])


async def result_keyboard(user_id: int, hymn_id: int) -> InlineKeyboardMarkup:
    favorite = await is_favorite(user_id, hymn_id)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Показать полностью", callback_data=f"full_{hymn_id}")],
        [InlineKeyboardButton(
            text="★ Удалить из избранного" if favorite else "⭐ В избранное",
            callback_data=f"fav_{hymn_id}",
        )],
    ])


# 🚀 /start
async def start_handler(message: Message):
    user_id = message.from_user.id
    await ensure_user(user_id)

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
        f"🚀 Версия: {BOT_VERSION}\n\n"
        f"🆕 <b>Новое в версии {BOT_VERSION}</b>\n"
        "🌐 Выбор языка: русский, украинский, английский и узбекский\n"
        "📚 Полный каталог: 22 сборника и 16 542 гимна\n"
        "⭐ Избранное с сохранением\n"
        "⚡ Быстрый доступ к любимым сборникам\n"
        "🔎 Поиск по названию, тексту или всему сразу\n\n"
        "💬 Есть идеи или что улучшить? Пиши — не стесняйся 😉",
        parse_mode="HTML",
        disable_web_page_preview=True
    )


# 📂 получить сборники
async def get_songbooks(language_code: str | None = None):
    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            sql = """SELECT s.id, s.title, s.language_code, COUNT(h.id) AS hymn_count
            FROM songbooks s LEFT JOIN hymns h ON h.songbook_id=s.id"""
            values = []
            if language_code:
                sql += " WHERE s.language_code=%s"
                values.append(language_code)
            sql += " GROUP BY s.id, s.title, s.language_code, s.display_order ORDER BY s.display_order, s.title"
            await cursor.execute(sql, values)
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
    settings = await get_settings(user_id)

    query = (message.text or "").strip()

    if not query:
        await message.answer("Отправьте номер или текст гимна.")
        return

    if len(query) > 300:
        await message.answer("Запрос слишком длинный. Используйте не более 300 символов.")
        return

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
        language_code=settings["catalog_language"],
        scope=settings["search_scope"],
        strict=True
    )

    exact_found = bool(results)

    # если нет — обычный
    if not results:
        results = await search_hymns(
            query,
            songbook_id=songbook_id,
            language_code=settings["catalog_language"],
            scope=settings["search_scope"],
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

        keyboard = await result_keyboard(user_id, row["id"])

        if row.get("tune"):
            tune_text = (
                f"\n🎼 Тональность: "
                f"{escape(row['tune'])}\n\n"
            )
        else:
            tune_text = "\n\n"

        await message.answer(
            f"📖 <b>{row['number']}. {escape(row['title'])}</b>\n"
            f"📂 {escape(row['songbook'] or 'Без сборника')}\n"
            f"🌐 {LANGUAGES.get(row.get('language_code'), row.get('language_code') or '—')}"
            f"{tune_text}"
            f"{escape(preview_text)}",
            parse_mode="HTML",
            reply_markup=keyboard
        )


# 🚀 основной обработчик сообщений
async def main_handler(message: Message):
    text = message.text
    user_id = message.from_user.id

    if text is None:
        await message.answer("Я ищу по тексту. Отправьте номер, название или строку гимна.")
        return

    # ⚙️ admin handlers
    handled = await admin_handler(
        message,
        user_mode,
        user_songbook
    )

    if handled:
        return

    if text == "🌐 Язык песен":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌍 Все языки", callback_data="lang_all")],
            *[[InlineKeyboardButton(text=name, callback_data=f"lang_{code}")] for code, name in LANGUAGES.items()],
        ])
        await message.answer("🌐 Выберите язык каталога:", reply_markup=keyboard)
        return

    if text == "⭐ Избранное":
        favorites = await get_favorites(user_id)
        if not favorites:
            await message.answer("⭐ В избранном пока ничего нет.")
            return
        await message.answer(f"⭐ Избранное: {len(favorites)}")
        for row in favorites:
            await message.answer(
                f"📖 <b>{row['number']}. {escape(row['title'])}</b>\n📂 {escape(row['songbook'])}",
                parse_mode="HTML",
                reply_markup=await result_keyboard(user_id, row["id"]),
            )
        return

    if text == "🔎 Область поиска":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔎 Название и текст", callback_data="scope_all")],
            [InlineKeyboardButton(text="📝 Только название", callback_data="scope_title")],
            [InlineKeyboardButton(text="📖 Только текст", callback_data="scope_text")],
        ])
        await message.answer("🔎 Где искать совпадения:", reply_markup=keyboard)
        return

    if text == "⚡ Быстрый доступ":
        books = await get_quick_songbooks(user_id)
        if not books:
            await message.answer("⚡ Быстрый доступ пуст. Закрепите сборник после его выбора.")
            return
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text=f"{LANGUAGES.get(book['language_code'], '🌐')} · {book['title']}",
                callback_data=f"sb_{book['id']}",
            )
        ] for book in books])
        await message.answer("⚡ Быстрый доступ:", reply_markup=keyboard)
        return

    # --- выбор режима ---
    if text == "📂 Искать по сборнику":
        user_mode[user_id] = "songbook"

        settings = await get_settings(user_id)
        songbooks = await get_songbooks(settings["catalog_language"])

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"{sb['title']} · {sb['hymn_count']}",
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
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="📌 Добавить/убрать быстрый доступ", callback_data=f"quick_{songbook_id}")
        ]]),
    )
    await callback.message.answer(
        "⬇️ Навигация:",
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
                    h.tune, h.words,
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
                f"{escape(row['tune'])}\n\n"
            )
        else:
            tune_text = "\n\n"

        words_text = f"✍️ {escape(row['words'])}\n" if row.get("words") else ""
        header = (
            f"📖 <b>{row['number']}. {escape(row['title'])}</b>\n"
            f"📂 {escape(row['songbook'] or 'Без сборника')}\n{words_text}{tune_text}"
        )
        content = row["content"]
        chunks = [content[i:i + 3500] for i in range(0, len(content), 3500)] or [""]
        favorite = await is_favorite(callback.from_user.id, int(hymn_id))
        await callback.message.answer(header, parse_mode="HTML")
        for chunk in chunks:
            await callback.message.answer(chunk)
        await callback.message.answer("Действия:", reply_markup=hymn_keyboard(int(hymn_id), favorite))

    else:
        await callback.message.answer(
            "Не удалось найти текст 😔"
        )

    await callback.answer()


async def choose_language(callback: CallbackQuery):
    value = callback.data.removeprefix("lang_")
    language = None if value == "all" else value
    if language is not None and language not in LANGUAGES:
        await callback.answer("Неизвестный язык", show_alert=True)
        return
    await set_catalog_language(callback.from_user.id, language)
    user_songbook.pop(callback.from_user.id, None)
    user_mode[callback.from_user.id] = "all"
    title = "Все языки" if language is None else LANGUAGES[language]
    await callback.message.answer(f"🌐 Язык каталога: {title}\nВведите номер, название или текст.")
    await callback.answer()


async def favorite_callback(callback: CallbackQuery):
    hymn_id = int(callback.data.removeprefix("fav_"))
    added = await toggle_favorite(callback.from_user.id, hymn_id)
    await callback.answer("Добавлено в избранное" if added else "Удалено из избранного")
    try:
        if callback.message.text == "Действия:":
            keyboard = hymn_keyboard(hymn_id, added)
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📖 Показать полностью", callback_data=f"full_{hymn_id}")],
                [InlineKeyboardButton(
                    text="★ Удалить из избранного" if added else "⭐ В избранное",
                    callback_data=f"fav_{hymn_id}",
                )],
            ])
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    except Exception:
        pass


async def quick_callback(callback: CallbackQuery):
    songbook_id = int(callback.data.removeprefix("quick_"))
    added = await toggle_quick_songbook(callback.from_user.id, songbook_id)
    await callback.answer("Сборник закреплён" if added else "Сборник откреплён", show_alert=True)


async def scope_callback(callback: CallbackQuery):
    scope = callback.data.removeprefix("scope_")
    titles = {"all": "название и текст", "title": "только название", "text": "только текст"}
    if scope not in titles:
        await callback.answer("Неизвестная область поиска", show_alert=True)
        return
    await set_search_scope(callback.from_user.id, scope)
    await callback.message.answer(f"🔎 Поиск: {titles[scope]}")
    await callback.answer()
