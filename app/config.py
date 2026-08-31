import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

BOT_VERSION = "2.0"


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Environment variable {name} is required")
    return value


TOKEN = required_env("BOT_TOKEN")
ADMIN_ID = int(required_env("ADMIN_ID"))

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost").strip(),
    "port": int(os.getenv("DB_PORT", "3306").strip()),
    "user": required_env("DB_USER"),
    "password": required_env("DB_PASSWORD"),
    "db": required_env("DB_NAME"),
}
