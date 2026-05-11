"""M6 — итоговый отчёт менеджеру.

Формирует таблицу со всеми предложениями (после расчёта себеса и торга)
и inline-кнопки для выбора поставщика.
"""

from __future__ import annotations

from typing import Any

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .. import db
from ..config import settings

_STATUS_RU = {
    "pending": "—",
    "invited": "ожидаем",
    "accepted": "согласен",
    "rejected": "отказал",
    "timeout": "не ответил",
}


def _format_table(request: dict[str, Any], offers: list[dict[str, Any]]) -> str:
    head = (
        f"<b>Заявка #{str(request['id'])[:8]}</b> — "
        f"{request.get('grade') or '?'}, "
        f"{request.get('quantity_t') or '?'}т, "
        f"{request.get('region') or '?'}\n"
        f"Получено предложений: {len(offers)}\n\n"
    )

    if not offers:
        return head + "Предложений нет."

    rows = ["<pre>", "#  Продавец            Цена/т  Лог./т  Себес/т  Кол-во  Торг"]
    for o in offers[:10]:
        rows.append(
            f"{o.get('rank') or '-':<2} "
            f"{(o.get('seller_name') or o.get('seller_username') or 'без имени')[:18]:<18} "
            f"{o.get('price_per_t') or '-':>7} "
            f"{o.get('logistics_per_t') or '-':>7} "
            f"{o.get('total_cost_per_t') or '-':>8} "
            f"{o.get('quantity_t') or '-':>6} "
            f"{_STATUS_RU.get(o.get('negotiation_status') or 'pending', '—')}"
        )
    rows.append("</pre>")
    return head + "\n".join(rows)


def _keyboard(request_id: str, offers: list[dict[str, Any]]) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for o in offers[:5]:
        rank = o.get("rank")
        if not rank:
            continue
        row.append(
            InlineKeyboardButton(
                text=f"Выбрать #{rank}",
                callback_data=f"pick:{request_id}:{o['id']}",
            )
        )
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append(
        [
            InlineKeyboardButton(
                text="Закрыть без выбора", callback_data=f"close:{request_id}"
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def send(bot: Bot, request_id: str) -> int:
    request = db.get_request(request_id)
    offers = db.list_offers(request_id)
    text = _format_table(request or {}, offers)
    kb = _keyboard(request_id, offers)
    msg = await bot.send_message(settings.tg_manager_id, text, reply_markup=kb)
    db.update_request(request_id, {"status": "awaiting_decision"})
    return msg.message_id
