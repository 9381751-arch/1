"""Хендлер канала заявок клиентов (M1 → M2)."""

from __future__ import annotations

import logging

from aiogram import Bot, F, Router
from aiogram.types import Message

from .. import db
from ..config import settings
from ..modules import m1_parse_request, m2_publish_post

router = Router(name="channel")
log = logging.getLogger("azimut.channel")


@router.channel_post(F.chat.id == settings.tg_channel_requests_id, F.text)
async def on_channel_post(message: Message, bot: Bot) -> None:
    raw = message.text or ""
    log.info("channel post: %s", raw[:200])

    parsed = await m1_parse_request.parse(raw)
    row = m1_parse_request.to_db_row(
        parsed,
        raw_text=raw,
        source="tg_channel",
        source_msg_id=message.message_id,
        source_user_id=message.from_user.id if message.from_user else None,
    )

    if missing := m1_parse_request.missing_required(parsed):
        request = db.insert_request(row)
        db.log_event(
            "request_clarifying",
            request_id=request["id"],
            payload={"missing": missing},
        )
        log.info("request %s waiting for clarification: %s", request["id"], missing)
        return

    request = db.insert_request(row)
    db.log_event("request_parsed", request_id=request["id"], payload=parsed)

    # M2: публикуем в группу продавцов
    post_text = await m2_publish_post.generate_post(request)
    msg_id = await m2_publish_post.publish(bot, post_text)
    db.update_request(
        request["id"],
        {
            "claude_post_text": post_text,
            "published_msg_id": msg_id,
            "status": "collecting",
            "published_at": "now()",
        },
    )
    db.log_event("request_published", request_id=request["id"], payload={"msg_id": msg_id})
    log.info("request %s published as msg %s", request["id"], msg_id)
