from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from app.config import ADMIN_ID

# динамическая клавиатура
def get_main_keyboard(user_id: int, user_mode: dict, user_songbook: dict):
    mode = user_mode.get(user_id)
    songbook_id = user_songbook.get(user_id)

    keyboard = []

    # 👑 кнопка админа
    admin_button = []
    if user_id == ADMIN_ID:
        admin_button = [[KeyboardButton(text="⚙️ Админ")]]

    if not mode:
        keyboard = [
            [KeyboardButton(text="📂 Искать по сборнику"), KeyboardButton(text="🌍 Искать по всей базе")],
            [KeyboardButton(text="🌐 Язык песен"), KeyboardButton(text="⭐ Избранное")],
            [KeyboardButton(text="⚡ Быстрый доступ"), KeyboardButton(text="🔎 Область поиска")],
        ] + admin_button

    elif mode == "all":
        keyboard = [
            [KeyboardButton(text="📂 Искать по сборнику")],
            [KeyboardButton(text="🌐 Язык песен"), KeyboardButton(text="⭐ Избранное")],
            [KeyboardButton(text="⚡ Быстрый доступ"), KeyboardButton(text="🔎 Область поиска")],
            [KeyboardButton(text="⬅️ Назад")]
        ] + admin_button

    elif mode == "songbook":
        if songbook_id:
            keyboard = [
                [KeyboardButton(text="❌ Сбросить сборник")],
                [KeyboardButton(text="🌐 Язык песен"), KeyboardButton(text="⭐ Избранное")],
                [KeyboardButton(text="⚡ Быстрый доступ"), KeyboardButton(text="🔎 Область поиска")],
                [KeyboardButton(text="⬅️ Назад")]
            ] + admin_button
        else:
            keyboard = [
                [KeyboardButton(text="🌐 Язык песен"), KeyboardButton(text="⭐ Избранное")],
                [KeyboardButton(text="⚡ Быстрый доступ"), KeyboardButton(text="🔎 Область поиска")],
                [KeyboardButton(text="⬅️ Назад")]
            ] + admin_button

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )
