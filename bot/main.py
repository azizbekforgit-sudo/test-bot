import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from .config import config
from .db import Database
from .handlers import get_routers
from .scheduler import watch_test_endings


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    db = Database(config.db_path)
    await db.connect()

    bot = Bot(config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    me = await bot.get_me()

    dp = Dispatcher(storage=MemoryStorage())
    dp["db"] = db
    dp["bot_username"] = me.username
    dp.include_routers(*get_routers())

    await bot.set_my_commands([
        BotCommand(command="start", description="Bosh menyu"),
        BotCommand(command="ism", description="Ism-familiyani o'zgartirish"),
        BotCommand(command="cancel", description="Bekor qilish"),
    ])

    logging.info("Bot ishga tushdi: @%s", me.username)
    watcher = asyncio.create_task(watch_test_endings(bot, db))
    try:
        await dp.start_polling(bot)
    finally:
        watcher.cancel()
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
