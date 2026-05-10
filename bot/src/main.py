"""Точка входа бота. Поднимает aiogram polling и регистрирует хендлеры."""

from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from .config import settings
from .handlers import channel, group, private
from .scheduler import setup as setup_scheduler


def setup_logging() -> None:
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    )


async def main() -> None:
    setup_logging()
    log = logging.getLogger("azimut.bot")

    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    dp.include_router(channel.router)
    dp.include_router(group.router)
    dp.include_router(private.router)

    scheduler = setup_scheduler(bot)
    scheduler.start()
    log.info("scheduler started (3 jobs, interval 60s)")

    log.info("bot starting (model=%s)", settings.claude_model)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    asyncio.run(main())
