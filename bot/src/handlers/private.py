"""Личка с ботом:

  - кнопки выбора поставщика от менеджера (M6);
  - ответы продавцов на торг (M5);
  - предложения от продавцов, написавших в личку напрямую (M3).

В MVP — упрощённая маршрутизация по chat.id и состоянию ожидания.
"""

from __future__ import annotations

import logging

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from .. import db
from ..config import settings
from ..modules import m3_collect_offers

router = Router(name="private")
log = logging.getLogger("azimut.private")


@router.message(Command("start"), F.chat.type == "private")
async def cmd_start(message: Message) -> None:
    if message.from_user and message.from_user.id == settings.tg_manager_id:
        await message.answer("Привет, менеджер. Отчёты по заявкам будут приходить сюда.")
    else:
        await message.answer(
            "Здравствуйте! Если у вас есть предложение по шпунту — пришлите параметры "
            "(марка, длина, состояние, тоннаж, цена/т без НДС, город, готовность). "
            "Я передам по вашей теме."
        )


# ---------- Менеджер: выбор поставщика ----------

@router.callback_query(F.data.startswith("pick:"))
async def on_pick(call: CallbackQuery) -> None:
    if not call.data:
        return
    _, request_id, offer_id = call.data.split(":", 2)
    db.update_request(
        request_id,
        {"status": "closed", "winner_offer_id": offer_id, "closed_at": "now()"},
    )
    db.log_event("winner_picked", request_id=request_id, offer_id=offer_id)
    await call.answer("Поставщик выбран")
    if call.message:
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer(f"✓ Заявка закрыта, выбран оффер {offer_id[:8]}.")


@router.callback_query(F.data.startswith("close:"))
async def on_close(call: CallbackQuery) -> None:
    if not call.data:
        return
    _, request_id = call.data.split(":", 1)
    db.update_request(request_id, {"status": "cancelled", "closed_at": "now()"})
    db.log_event("request_cancelled", request_id=request_id)
    await call.answer("Закрыто без выбора")
    if call.message:
        await call.message.edit_reply_markup(reply_markup=None)


# ---------- Продавец: ответ на торг или прямое предложение ----------

def _find_invited_offer(seller_tg_id: int) -> dict | None:
    res = (
        db.get_client()
        .table("offers")
        .select("*")
        .eq("seller_tg_id", seller_tg_id)
        .eq("negotiation_status", "invited")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    return res.data[0] if res.data else None


@router.message(F.chat.type == "private", F.text)
async def on_private_message(message: Message, bot: Bot) -> None:
    if not message.from_user:
        return
    user_id = message.from_user.id

    # менеджер пишет в личку — не торг и не оффер
    if user_id == settings.tg_manager_id:
        return

    raw = message.text or ""
    invited = _find_invited_offer(user_id)
    if invited:
        # ответ на торг — простая эвристика "да/нет" + поиск числа
        lower = raw.lower()
        accepted = any(w in lower for w in ("да", "ок", "согласен", "беру", "договорились"))
        rejected = any(w in lower for w in ("нет", "не могу", "дороже", "не возьму", "отказ"))

        update: dict = {"final_price": invited.get("counter_price")}
        if accepted and not rejected:
            update["negotiation_status"] = "accepted"
        elif rejected:
            update["negotiation_status"] = "rejected"
        else:
            update["negotiation_status"] = "rejected"  # неоднозначно — фиксируем как отказ
        db.update_offer(invited["id"], update)
        db.log_event(
            "negotiation_response",
            request_id=invited["request_id"],
            offer_id=invited["id"],
            payload={"text": raw, "status": update["negotiation_status"]},
        )
        await message.answer("Спасибо, зафиксировал.")
        return

    # прямое предложение в личку — ищем активную заявку
    res = (
        db.get_client()
        .table("requests")
        .select("id")
        .eq("status", "collecting")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not res.data:
        await message.answer("Сейчас активных заявок нет. Спасибо!")
        return
    request_id = res.data[0]["id"]

    parsed = await m3_collect_offers.parse(raw)
    if not parsed.get("price_per_t"):
        await message.answer(
            "Не понял цену. Пришлите, пожалуйста: марка, длина, состояние, "
            "тоннаж, цена/т без НДС, город, готовность."
        )
        return

    row = m3_collect_offers.to_db_row(
        parsed,
        request_id=request_id,
        raw_text=raw,
        source="tg_private",
        seller_tg_id=user_id,
        seller_username=message.from_user.username,
        seller_name=message.from_user.full_name,
    )
    offer = db.insert_offer(row)
    db.log_event("offer_received", request_id=request_id, offer_id=offer["id"], payload=parsed)
    await message.answer("Предложение получено, спасибо!")
