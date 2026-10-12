import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    bot_token: str
    director_ids: frozenset[int]
    db_path: str


def load_config() -> Config:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN topilmadi. .env faylini to'ldiring.")

    raw_ids = os.getenv("DIRECTOR_IDS", "")
    director_ids = frozenset(int(x) for x in raw_ids.replace(" ", "").split(",") if x)
    if not director_ids:
        raise RuntimeError("DIRECTOR_IDS topilmadi. .env faylini to'ldiring.")

    return Config(
        bot_token=token,
        director_ids=director_ids,
        db_path=os.getenv("DB_PATH", "bot.db"),
    )


config = load_config()
