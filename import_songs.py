import json
import asyncio
import aiomysql

from app.config import DB_CONFIG
from app.utils.text import normalize


def generate_search_key(songbook_id: int, number: int, title: str) -> str:
    return f"{songbook_id}_{number}_{normalize(title)}"


async def get_or_create_songbook(cursor, title: str):
    normalized = normalize(title)
    search_key = normalized

    # ищем
    await cursor.execute(
        "SELECT id FROM songbooks WHERE search_key = %s",
        (search_key,)
    )
    row = await cursor.fetchone()

    if row:
        # обновим title + нормализованное поле
        await cursor.execute(
            """
            UPDATE songbooks
            SET title=%s, normalized_title=%s
            WHERE id=%s
            """,
            (title, normalized, row["id"])
        )
        return row["id"]

    # создаём
    await cursor.execute(
        """
        INSERT INTO songbooks (title, normalized_title, search_key)
        VALUES (%s, %s, %s)
        """,
        (title, normalized, search_key)
    )

    return cursor.lastrowid


async def import_songs():
    # --- читаем сборник ---
    with open("import/ru/zvuki_neba/songbook.json", "r", encoding="utf-8") as f:
        songbook = json.load(f)[0]

    # --- читаем песни ---
    with open("import/ru/zvuki_neba/songs.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        songs = data
    elif isinstance(data, dict):
        songs = data.get("Songs") or data.get("songs") or data.get("data") or []
    else:
        raise Exception("Непонятный формат JSON")

    print(f"Найдено песен: {len(songs)}")

    songbook_title = songbook.get("title", "")

    conn = await aiomysql.connect(**DB_CONFIG)
    cursor = await conn.cursor(aiomysql.DictCursor)

    # --- получаем ID сборника ---
    songbook_id = await get_or_create_songbook(cursor, songbook_title)

    inserted = 0
    updated = 0

    for song in songs:
        number = song.get("number") or 0
        title = song.get("title", "")
        content = song.get("song_text", "")
        tune = song.get("tune", "")

        # нормализация ЗДЕСЬ (внутри цикла!)
        title_normalized = normalize(title)
        content_normalized = normalize(content)[:5000]

        search_key = generate_search_key(songbook_id, number, title)

        # ищем песню
        await cursor.execute(
            "SELECT id FROM hymns WHERE search_key = %s",
            (search_key,)
        )
        existing = await cursor.fetchone()

        if existing:
            # UPDATE
            await cursor.execute(
                """
                UPDATE hymns
                SET
                    title=%s,
                    content=%s,
                    songbook_id=%s,
                    number=%s,
                    tune=%s,
                    title_normalized=%s,
                    content_normalized=%s
                WHERE search_key=%s
                """,
                (
                    title,
                    content,
                    songbook_id,
                    number,
                    tune,
                    title_normalized,
                    content_normalized,
                    search_key
                )
            )
            updated += 1
            print(f"🔄 Обновлено: {title}")

        else:
            # INSERT
            await cursor.execute(
                """
                INSERT INTO hymns (
                    title,
                    content,
                    songbook_id,
                    number,
                    tune,
                    search_key,
                    title_normalized,
                    content_normalized
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    title,
                    content,
                    songbook_id,
                    number,
                    tune,
                    search_key,
                    title_normalized,
                    content_normalized
                )
            )
            inserted += 1
            print(f"➕ Добавлено: {title}")

    await conn.commit()
    await cursor.close()
    conn.close()

    print("\n=== ИТОГ ===")
    print(f"Добавлено: {inserted}")
    print(f"Обновлено: {updated}")


if __name__ == "__main__":
    asyncio.run(import_songs())