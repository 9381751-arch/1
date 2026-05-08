"""M4 — расчёт себестоимости и ранжирование.

    Себес/т = Цена_продавца/т + max(Тариф_руб/т·км × Расстояние_км, Мин. ставка/т)
"""

from __future__ import annotations

from typing import Any

from .. import db, osrm


async def compute_cost_for_offer(offer: dict[str, Any], region: str) -> dict[str, Any]:
    """Возвращает обновлённые поля для offer: distance_km, logistics_per_t,
    total_cost_per_t. Не сохраняет в БД — это делает вызывающий."""
    rate = db.get_setting_float("logistics_rate_per_t_km", 12.0)
    floor = db.get_setting_float("logistics_min_per_t", 500.0)

    distance = await osrm.distance_km(offer["location"], region) if offer.get("location") else None
    price = float(offer.get("price_per_t") or 0)

    if distance is None:
        # без расстояния не можем посчитать корректно, ставим только пол
        logistics = floor
        total = price + logistics
        return {
            "distance_km": None,
            "logistics_per_t": logistics,
            "total_cost_per_t": total,
        }

    logistics = max(rate * distance, floor)
    total = price + logistics
    return {
        "distance_km": round(distance, 1),
        "logistics_per_t": round(logistics, 2),
        "total_cost_per_t": round(total, 2),
    }


async def recalculate_request(request_id: str) -> list[dict[str, Any]]:
    """Пересчитывает себес для всех предложений по заявке и проставляет rank."""
    request = db.get_request(request_id)
    if not request or not request.get("region"):
        return []

    offers = db.list_offers(request_id)
    enriched: list[dict[str, Any]] = []

    for offer in offers:
        if not offer.get("price_per_t"):
            continue
        update = await compute_cost_for_offer(offer, request["region"])
        db.update_offer(offer["id"], update)
        enriched.append({**offer, **update})

    enriched.sort(key=lambda o: o["total_cost_per_t"])
    for idx, offer in enumerate(enriched, start=1):
        db.update_offer(offer["id"], {"rank": idx})
        offer["rank"] = idx

    return enriched
