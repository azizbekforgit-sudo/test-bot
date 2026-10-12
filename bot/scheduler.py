"""Test tugaganda adminlarga xabar beruvchi fon vazifasi."""

import asyncio
import logging

from aiogram import Bot

from . import keyboards as kb
from . import texts as t
from .config import config
from .db import Database
from .timeutils import FINISHED, status_of
from .utils import esc

CHECK_EVERY = 30  # soniya


async def watch_test_endings(bot: Bot, db: Database) -> None:
    while True:
        try:
            for test in await db.unnotified_tests():
                if status_of(test) != FINISHED:
                    continue
                await db.update_test(test.id, end_notified=1)
                count = len(await db.list_results(test.id))
                for admin_id in config.admin_ids:
                    try:
                        await bot.send_message(
                            admin_id,
                            t.TEST_ENDED_NOTIFY.format(code=esc(test.code), count=count),
                            reply_markup=kb.open_test_kb(test.id),
                        )
                    except Exception:
                        logging.exception("Adminga xabar yuborib bo'lmadi")
        except Exception:
            logging.exception("watch_test_endings xatosi")
        await asyncio.sleep(CHECK_EVERY)
