from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_admin_keyboard():
    keyboard = [
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="🔄 Рестарт бота")],
        [KeyboardButton(text="⬅️ В основное меню")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )