"""M1 — парсинг входящей заявки клиента из TG-канала закупок.

Вход: сырой текст сообщения.
Выход: словарь со структурными полями + список недостающих обязательных полей,
по которым бот должен задать уточняющие вопросы.
"""

from __future__ import annotations

from typing import Any, TypedDict

from .. import llm

_REQUIRED = ("grade", "quantity_t", "region", "deadline")
_OPTIONAL = ("length_m", "condition", "extra_conditions")

_SYSTEM = """\
Ты — помощник по закупке б/у шпунта в России. Извлекай из текста параметры заявки и
возвращай СТРОГО валидный JSON со следующими ключами:

  grade            — марка шпунта (например "Л4", "Л5"), строка или null
  length_m         — длина в метрах, число или null
  quantity_t       — количество в тоннах, число или null
  region           — регион/город доставки, строка или null
  deadline         — срок в формате YYYY-MM-DD, строка или null
  condition        — состояние 1, 2 или 3, число или null
  extra_conditions — доп. условия одной строкой, либо null

Никакого текста вне JSON. Если поле не названо в тексте — ставь null.
"""


class ParsedRequest(TypedDict):
    grade: str | None
    length_m: float | None
    quantity_t: float | None
    region: str | None
    deadline: str | None
    condition: int | None
    extra_conditions: str | None


async def parse(raw_text: str) -> ParsedRequest:
    data = await llm.complete_json(_SYSTEM, raw_text)
    return {
        "grade": data.get("grade"),
        "length_m": data.get("length_m"),
        "quantity_t": data.get("quantity_t"),
        "region": data.get("region"),
        "deadline": data.get("deadline"),
        "condition": data.get("condition"),
        "extra_conditions": data.get("extra_conditions"),
    }


def missing_required(parsed: ParsedRequest) -> list[str]:
    return [k for k in _REQUIRED if not parsed.get(k)]


def to_db_row(parsed: ParsedRequest, raw_text: str, **extra: Any) -> dict[str, Any]:
    row: dict[str, Any] = {"raw_text": raw_text, "status": "new"}
    for k in (*_REQUIRED, *_OPTIONAL):
        if parsed.get(k) is not None:
            row[k] = parsed[k]
    row.update(extra)
    if missing_required(parsed):
        row["status"] = "clarifying"
    return row
