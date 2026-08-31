import aiomysql

from app.db import db


LANGUAGES = {"ru": "Русский", "uk": "Українська", "en": "English", "uz": "O‘zbekcha"}


async def ensure_user(user_id: int) -> None:
    async with db.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("INSERT IGNORE INTO bot_users (user_id) VALUES (%s)", (user_id,))
            if cursor.rowcount:
                await cursor.execute(
                    """INSERT IGNORE INTO user_quick_songbooks (user_id, songbook_id, position)
                    SELECT %s, id, CASE source_slug WHEN 'pesenik' THEN 0 ELSE 1 END
                    FROM songbooks WHERE language_code='ru' AND source_slug IN ('pesenik', 'molodejniy_sbornik')""",
                    (user_id,),
                )


async def get_settings(user_id: int) -> dict:
    await ensure_user(user_id)
    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT interface_language, catalog_language, search_scope FROM bot_users WHERE user_id=%s",
                (user_id,),
            )
            return await cursor.fetchone()


async def set_catalog_language(user_id: int, language: str | None) -> None:
    await ensure_user(user_id)
    async with db.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "UPDATE bot_users SET catalog_language=%s WHERE user_id=%s",
                (language, user_id),
            )


async def set_search_scope(user_id: int, scope: str) -> None:
    if scope not in {"all", "title", "text"}:
        raise ValueError("Unsupported search scope")
    await ensure_user(user_id)
    async with db.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "UPDATE bot_users SET search_scope=%s WHERE user_id=%s",
                (scope, user_id),
            )


async def is_favorite(user_id: int, hymn_id: int) -> bool:
    async with db.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT 1 FROM user_favorites WHERE user_id=%s AND hymn_id=%s",
                (user_id, hymn_id),
            )
            return await cursor.fetchone() is not None


async def toggle_favorite(user_id: int, hymn_id: int) -> bool:
    await ensure_user(user_id)
    async with db.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM user_favorites WHERE user_id=%s AND hymn_id=%s",
                (user_id, hymn_id),
            )
            if cursor.rowcount:
                return False
            await cursor.execute(
                "INSERT IGNORE INTO user_favorites (user_id, hymn_id) VALUES (%s, %s)",
                (user_id, hymn_id),
            )
            return True


async def get_favorites(user_id: int, limit: int = 50) -> list[dict]:
    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                """SELECT h.id, h.number, h.title, h.content, h.tune, h.words,
                s.title AS songbook, s.language_code
                FROM user_favorites f JOIN hymns h ON h.id=f.hymn_id
                JOIN songbooks s ON s.id=h.songbook_id
                WHERE f.user_id=%s ORDER BY f.created_at DESC LIMIT %s""",
                (user_id, limit),
            )
            return await cursor.fetchall()


async def toggle_quick_songbook(user_id: int, songbook_id: int) -> bool:
    await ensure_user(user_id)
    async with db.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM user_quick_songbooks WHERE user_id=%s AND songbook_id=%s",
                (user_id, songbook_id),
            )
            if cursor.rowcount:
                return False
            await cursor.execute(
                "SELECT COALESCE(MAX(position), -1)+1 FROM user_quick_songbooks WHERE user_id=%s",
                (user_id,),
            )
            position = (await cursor.fetchone())[0]
            await cursor.execute(
                "INSERT INTO user_quick_songbooks (user_id, songbook_id, position) VALUES (%s, %s, %s)",
                (user_id, songbook_id, position),
            )
            return True


async def get_quick_songbooks(user_id: int) -> list[dict]:
    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                """SELECT s.id, s.title, s.language_code, COUNT(h.id) AS hymn_count
                FROM user_quick_songbooks q JOIN songbooks s ON s.id=q.songbook_id
                LEFT JOIN hymns h ON h.songbook_id=s.id
                WHERE q.user_id=%s GROUP BY s.id, s.title, s.language_code, q.position
                ORDER BY q.position""",
                (user_id,),
            )
            return await cursor.fetchall()
