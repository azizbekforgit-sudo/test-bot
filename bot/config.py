import os
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    bot_token: str
    admin_ids: frozenset[int]
    db_path: str
    tz: ZoneInfo


def load_config() -> Config:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN topilmadi. .env faylini to'ldiring.")

    raw_ids = os.getenv("ADMIN_IDS") or os.getenv("DIRECTOR_IDS", "")
    admin_ids = frozenset(int(x) for x in raw_ids.replace(" ", "").split(",") if x)
    if not admin_ids:
        raise RuntimeError("ADMIN_IDS topilmadi. .env faylini to'ldiring.")

    return Config(
        bot_token=token,
        admin_ids=admin_ids,
        db_path=os.getenv("DB_PATH", "bot.db"),
        tz=ZoneInfo(os.getenv("TIMEZONE", "Asia/Tashkent")),
    )


config = load_config()
