import aiomysql

from app.db import db


async def get_bot_stats():
    async with db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:

            # 👥 пользователи
            await cursor.execute("""
                SELECT COUNT(DISTINCT user_id) AS total
                FROM search_logs
            """)
            users = await cursor.fetchone()

            # 🔍 всего запросов
            await cursor.execute("""
                SELECT COUNT(*) AS total
                FROM search_logs
            """)
            searches = await cursor.fetchone()

            # 📅 сегодня
            await cursor.execute("""
                SELECT COUNT(*) AS total
                FROM search_logs
                WHERE DATE(created_at) = CURDATE()
            """)
            today = await cursor.fetchone()

            # ⚡ средний response
            await cursor.execute("""
                SELECT ROUND(AVG(response_time_sec), 2) AS avg_time
                FROM search_logs
            """)
            avg_time = await cursor.fetchone()

            # 🔥 топ запросов
            await cursor.execute("""
                SELECT
                    normalized_query,
                    COUNT(*) AS total
                FROM search_logs
                WHERE normalized_query != ''
                GROUP BY normalized_query
                ORDER BY total DESC
                LIMIT 5
            """)
            top_queries = await cursor.fetchall()

            # 📚 режимы
            await cursor.execute("""
                SELECT
                    mode,
                    COUNT(*) AS total
                FROM search_logs
                GROUP BY mode
            """)
            modes = await cursor.fetchall()

            # 📚 база гимнов
            await cursor.execute("""
                SELECT COUNT(*) AS total
                FROM hymns
            """)
            hymns = await cursor.fetchone()

            await cursor.execute("""
                SELECT COUNT(*) AS total
                FROM songbooks
            """)
            songbooks = await cursor.fetchone()

    return {
        "users": users["total"],
        "searches": searches["total"],
        "today": today["total"],
        "avg_time": avg_time["avg_time"] or 0,
        "top_queries": top_queries,
        "modes": modes,

        "hymns": hymns["total"],
        "songbooks": songbooks["total"]
    }