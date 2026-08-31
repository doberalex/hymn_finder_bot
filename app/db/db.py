import aiomysql

from app.config import DB_CONFIG
from app.db.schema import apply_schema

pool = None

async def connect_db():
    global pool
    pool = await aiomysql.create_pool(**DB_CONFIG, autocommit=True)
    await apply_schema(pool)
