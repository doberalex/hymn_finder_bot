import aiomysql

from app.config import DB_CONFIG

pool = None

async def connect_db():
    global pool
    pool = await aiomysql.create_pool(**DB_CONFIG, autocommit=True)
