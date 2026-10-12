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
    database_url: str | None
    tz: ZoneInfo
    # Webhook rejimi (serverda): bot shu manzilda Telegramdan xabar qabul qiladi
    webhook_base: str | None
    webhook_secret: str
    port: int


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
        database_url=os.getenv("DATABASE_URL") or None,
        tz=ZoneInfo(os.getenv("TIMEZONE", "Asia/Tashkent")),
        # Render o'zi RENDER_EXTERNAL_URL ni beradi; boshqa hostingda WEBHOOK_URL yoziladi
        webhook_base=(os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL") or "").rstrip("/") or None,
        webhook_secret=os.getenv("WEBHOOK_SECRET") or token.split(":")[-1][-20:],
        port=int(os.getenv("PORT", "8080")),
    )


config = load_config()
