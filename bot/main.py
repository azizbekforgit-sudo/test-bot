import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from .config import config
from .db import Database
from .handlers import get_routers
from .scheduler import watch_test_endings

WEBHOOK_PATH = "/telegram/webhook"


async def run_webhook(bot: Bot, dp: Dispatcher) -> None:
    """Serverda: Telegram xabarlarni HTTP orqali yuboradi (Render bepul tarifida ham ishlaydi)."""
    await bot.set_webhook(
        f"{config.webhook_base}{WEBHOOK_PATH}",
        secret_token=config.webhook_secret,
        allowed_updates=dp.resolve_used_update_types(),
    )

    app = web.Application()

    async def health(_: web.Request) -> web.Response:
        return web.Response(text="ok")

    app.router.add_get("/", health)
    SimpleRequestHandler(dp, bot, secret_token=config.webhook_secret).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", config.port).start()
    logging.info("Webhook rejimi: %s%s (port %s)", config.webhook_base, WEBHOOK_PATH, config.port)
    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    db = Database(config.db_path, config.database_url)
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
        if config.webhook_base:
            await run_webhook(bot, dp)
        else:
            # Kompyuterda: oddiy polling rejimi
            await bot.delete_webhook()
            await dp.start_polling(bot)
    finally:
        watcher.cancel()
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
