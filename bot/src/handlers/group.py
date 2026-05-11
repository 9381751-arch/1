"""Хендлер группы продавцов — приём ответов на пост.

Логика MVP:
  - если сообщение является ответом (reply) на пост заявки — привязываем к этой заявке;
  - иначе берём самую свежую заявку в статусе collecting (упрощение для MVP).
"""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.types import Message

from .. import db
from ..config import settings
from ..modules import m3_collect_offers

router = Router(name="group")
log = logging.getLogger("azimut.group")


def _find_request_id(message: Message) -> str | None:
    client = db.get_client()

    if message.reply_to_message:
        res = (
            client.table("requests")
            .select("id")
            .eq("published_msg_id", message.reply_to_message.message_id)
            .limit(1)
            .execute()
        )
        if res.data:
            return res.data[0]["id"]

    res = (
        client.table("requests")
        .select("id")
        .eq("status", "collecting")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    return res.data[0]["id"] if res.data else None


@router.message(F.chat.id == settings.tg_group_sellers_id, F.text)
async def on_group_message(message: Message) -> None:
    raw = message.text or ""
    log.info("group message: %s", raw[:200])

    request_id = _find_request_id(message)
    if not request_id:
        log.warning("no active request, skipping group message")
        return

    parsed = await m3_collect_offers.parse(raw)
    if not parsed.get("price_per_t"):
        # без цены не считаем за оффер
        return

    user = message.from_user
    row = m3_collect_offers.to_db_row(
        parsed,
        request_id=request_id,
        raw_text=raw,
        source="tg_group",
        seller_tg_id=user.id if user else 0,
        seller_username=user.username if user else None,
        seller_name=user.full_name if user else None,
    )
    row["source_msg_id"] = message.message_id
    offer = db.insert_offer(row)
    db.log_event("offer_received", request_id=request_id, offer_id=offer["id"], payload=parsed)
