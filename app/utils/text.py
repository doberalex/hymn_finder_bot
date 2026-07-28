import re


# 🔹 нормализация текста
def normalize(text: str) -> str:
    if not text:
        return ""

    # нижний регистр
    text = text.lower()

    # удаляем всё кроме букв/цифр/пробелов
    text = re.sub(r"[^\w\s]", " ", text)

    # схлопываем множественные пробелы
    text = re.sub(r"\s+", " ", text)

    return text.strip()