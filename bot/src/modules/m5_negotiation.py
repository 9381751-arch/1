"""M5 — торговый раунд с ТОП-N продавцами.

Логика:
  1. Берём N лучших предложений по total_cost_per_t (N из настроек).
  2. Для каждого считаем target_price = best_price * (1 - discount_pct/100).
  3. Claude генерирует персональное сообщение с этой ценой.
  4. Бот пишет каждому в личку (ставит negotiation_status='invited').
  5. Ответы продавцов разбираются хендлером личного чата (см. handlers/private.py).
"""

from __future__ import annotations

from typing import Any

from aiogram import Bot

from .. import db, llm

_SYSTEM = """\
Ты — снабженец, который ведёт торг с продавцом б/у шпунта в Telegram-личке.
Сгенерируй короткое (2–4 строки), вежливое и конкретное сообщение:
  - обратись к продавцу по имени (если есть),
  - сошлись на его предложение, скажи что объём подходит,
  - предложи цену TARGET_PRICE за тонну,
  - попроси короткий ответ "да/нет" или встречную цену,
  - без markdown, без упоминания бота и автоматики.
"""


async def select_top(request_id: str) -> list[dict[str, Any]]:
    n = db.get_setting_int("negotiation_top_n", 3)
    offers = [o for o in db.list_offers(request_id) if o.get("total_cost_per_t")]
    return offers[:n]


def target_price(best_price: float) -> float:
    pct = db.get_setting_float("negotiation_discount_pct", 5.0)
    return round(best_price * (1 - pct / 100), 2)


async def _generate_message(offer: dict[str, Any], target: float) -> str:
    user = (
        f"имя: {offer.get('seller_name') or offer.get('seller_username') or 'коллега'}\n"
        f"их цена за тонну: {offer.get('price_per_t')}\n"
        f"их количество: {offer.get('quantity_t')} т\n"
        f"их город: {offer.get('location')}\n"
        f"TARGET_PRICE: {target}"
    )
    return await llm.complete_text(_SYSTEM, user, temperature=0.7)


async def run(bot: Bot, request_id: str) -> list[dict[str, Any]]:
    """Запускает торговый раунд. Возвращает список приглашённых офферов."""
    top = await select_top(request_id)
    if not top:
        return []

    best_price = float(top[0]["price_per_t"])
    target = target_price(best_price)

    invited: list[dict[str, Any]] = []
    for offer in top:
        text = await _generate_message(offer, target)
        await bot.send_message(offer["seller_tg_id"], text)
        db.update_offer(
            offer["id"],
            {
                "negotiation_status": "invited",
                "counter_price": target,
            },
        )
        db.log_event(
            "negotiation_invited",
            request_id=request_id,
            offer_id=offer["id"],
            payload={"target_price": target, "message": text},
        )
        invited.append(offer)

    db.update_request(request_id, {"status": "negotiating"})
    return invited
