import aiomysql

from app.db import db
from app.utils.text import normalize


async def log_search(
    user,
    query: str,
    songbook_id: int,
    results_count: int,
    mode,
    response_time
):
    query_norm = normalize(query)

    async with db.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO search_logs (
                    user_id,
                    username,
                    first_name,
                    query,
                    normalized_query,
                    songbook_id,
                    results_count,
                    mode,
                    response_time_sec
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user.id,
                    user.username,
                    user.first_name,
                    query,
                    query_norm,
                    songbook_id,
                    results_count,
                    mode,
                    response_time
                )
            )