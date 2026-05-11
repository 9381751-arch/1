"""M2 — генерация и публикация поста в группу продавцов.

Текст генерируется Claude каждый раз заново, без шаблонов.
В тексте НЕ должно упоминаться: бот, автоматика, компания-покупатель.
"""

from __future__ import annotations

from typing import Any

from aiogram import Bot

from .. import llm
from ..config import settings

_SYSTEM = """\
Ты — снабженец, который ищет б/у шпунт у поставщиков в России через Telegram-чат.
По параметрам заявки сгенерируй короткий живой пост в группу продавцов (3–6 строк):
  - в разговорном стиле, как пишут в чатах,
  - укажи марку, длину, количество, состояние, регион, срок,
  - попроси писать в личку,
  - НЕ упоминай ни бота, ни автоматику, ни название компании-покупателя,
  - не используй markdown, эмодзи допустимы умеренно.

Каждый пост должен быть уникальным — варьируй формулировки.
"""


def _format_input(req: dict[str, Any]) -> str:
    parts = []
    if req.get("grade"):
        parts.append(f"марка: {req['grade']}")
    if req.get("length_m"):
        parts.append(f"длина: {req['length_m']} м")
    if req.get("quantity_t"):
        parts.append(f"количество: {req['quantity_t']} т")
    if req.get("condition"):
        parts.append(f"состояние: {req['condition']}")
    if req.get("region"):
        parts.append(f"регион: {req['region']}")
    if req.get("deadline"):
        parts.append(f"срок: {req['deadline']}")
    if req.get("extra_conditions"):
        parts.append(f"доп: {req['extra_conditions']}")
    return "\n".join(parts)


async def generate_post(req: dict[str, Any]) -> str:
    return await llm.complete_text(_SYSTEM, _format_input(req), temperature=0.9)


async def publish(bot: Bot, text: str) -> int:
    msg = await bot.send_message(settings.tg_group_sellers_id, text)
    return msg.message_id
