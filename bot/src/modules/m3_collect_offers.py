"""M3 — парсинг ответов продавцов.

Вход: сырой текст ответа в группе или личке.
Выход: словарь со структурными полями + список недостающих обязательных полей.
"""

from __future__ import annotations

from typing import Any, TypedDict

from .. import llm

_REQUIRED = (
    "grade",
    "quantity_t",
    "price_per_t",
    "vat_type",
    "location",
    "ready_date",
)

_SYSTEM = """\
Ты разбираешь сообщения продавцов б/у шпунта в Telegram. Извлеки параметры
предложения и верни СТРОГО валидный JSON:

  grade        — марка (Л4/Л5/...), строка или null
  length_m     — длина в метрах, число или null
  condition    — состояние 1/2/3, число или null
  quantity_t   — количество в тоннах, число или null
  price_per_t  — цена за тонну в рублях БЕЗ НДС, число или null
  vat_type     — "with_vat" | "no_vat" | "usn" | null
  location     — город отгрузки, строка или null
  ready_date   — готовность к отгрузке YYYY-MM-DD, строка или null
  comment      — любые доп. условия одной строкой, либо null

Если цена указана с НДС — пересчитай в "без НДС" по ставке 20% и поставь
vat_type="with_vat". Если продавец сказал "без НДС" или "УСН" — оставь
цену как есть с соответствующим vat_type. Никакого текста вне JSON.
"""


class ParsedOffer(TypedDict):
    grade: str | None
    length_m: float | None
    condition: int | None
    quantity_t: float | None
    price_per_t: float | None
    vat_type: str | None
    location: str | None
    ready_date: str | None
    comment: str | None


async def parse(raw_text: str) -> ParsedOffer:
    data = await llm.complete_json(_SYSTEM, raw_text)
    return {
        "grade": data.get("grade"),
        "length_m": data.get("length_m"),
        "condition": data.get("condition"),
        "quantity_t": data.get("quantity_t"),
        "price_per_t": data.get("price_per_t"),
        "vat_type": data.get("vat_type"),
        "location": data.get("location"),
        "ready_date": data.get("ready_date"),
        "comment": data.get("comment"),
    }


def missing_required(parsed: ParsedOffer) -> list[str]:
    return [k for k in _REQUIRED if not parsed.get(k)]


def to_db_row(parsed: ParsedOffer, *, request_id: str, raw_text: str, source: str,
              seller_tg_id: int, seller_username: str | None,
              seller_name: str | None) -> dict[str, Any]:
    row: dict[str, Any] = {
        "request_id": request_id,
        "raw_text": raw_text,
        "source": source,
        "seller_tg_id": seller_tg_id,
        "seller_username": seller_username,
        "seller_name": seller_name,
    }
    for k, v in parsed.items():
        if v is not None:
            row[k] = v
    return row
