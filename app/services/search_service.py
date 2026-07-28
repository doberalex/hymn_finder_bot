import aiomysql
import re

from app.db import db
from app.utils.text import normalize


# 🔹 подсветка найденного текста
def highlight_text(text: str, query: str) -> str:
    if not text or not query:
        return text

    query_norm = normalize(query)

    if not query_norm:
        return text

    # разбиваем для подсветки
    words = query_norm.split()

    result = text

    for word in words:
        if len(word) < 2:
            continue

        pattern = re.compile(re.escape(word), re.IGNORECASE)

        result = pattern.sub(
            lambda m: f"<b><u>{m.group(0)}</u></b>",
            result
        )

    return result


# 🔹 умное превью (вырезает кусок вокруг совпадения)
def build_preview(text: str, query: str, radius: int = 100) -> str:
    if not text:
        return ""

    query_norm = normalize(query)

    if not query_norm:
        preview = text[:radius * 2]
        return preview + "..." if len(text) > radius * 2 else preview

    text_lower = text.lower()

    # ищем полную фразу
    index = text_lower.find(query_norm)

    # если точной фразы нет — пробуем первое слово
    if index == -1:
        first_word = query_norm.split()[0]

        if len(first_word) > 1:
            index = text_lower.find(first_word)

    # если ничего не нашли
    if index == -1:
        preview = text[:radius * 2]
        return preview + "..." if len(text) > radius * 2 else preview

    start = max(index - radius, 0)
    end = min(index + len(query_norm) + radius, len(text))

    preview = text[start:end]

    if start > 0:
        preview = "..." + preview

    if end < len(text):
        preview = preview + "..."

    return preview


# 🔍 основной поиск
async def search_hymns(
    query: str,
    offset: int = 0,
    songbook_id: int = None,
    limit: int = 20,
    strict: bool = True
):
    query_norm = normalize(query)

    base_sql = """
        SELECT
            h.id,
            h.number,
            h.title,
            h.content,
            h.tune,
            s.title AS songbook
        FROM hymns h
        LEFT JOIN songbooks s ON h.songbook_id = s.id
    """

    conditions = []
    values = []

    # 📂 фильтр по сборнику (если выбран)
    if songbook_id:
        conditions.append("h.songbook_id = %s")
        values.append(songbook_id)

    # 🔢 поиск по номеру
    if query_norm.isdigit():
        conditions.append("h.number = %s")
        values.append(int(query_norm))

        order_clause = "ORDER BY h.number ASC"

    # 🔍 поиск по фразе
    elif query_norm:
        conditions.append("""
            (
                h.title_normalized LIKE %s OR
                h.content_normalized LIKE %s
            )
        """)

        search_value = f"%{query_norm}%"

        values.extend([
            search_value,
            search_value
        ])

        order_clause = """
            ORDER BY
                CASE
                    WHEN h.title_normalized LIKE %s THEN 1
                    WHEN h.content_normalized LIKE %s THEN 2
                    ELSE 3
                END,
                h.number ASC
        """

        values.extend([
            search_value,
            search_value
        ])

    else:
        order_clause = "ORDER BY h.number ASC"

    # 🔹 WHERE
    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(f"({c})" for c in conditions)

    sql = f"""
        {base_sql}
        {where_clause}
        {order_clause}
        LIMIT %s OFFSET %s
    """

    values.append(limit)
    values.append(offset)

    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(sql, values)
            rows = await cursor.fetchall()

    return rows