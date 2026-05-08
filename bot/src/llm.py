"""Обёртка над Claude API.

В MVP используются три типа вызовов:
    - parse_*  — структурирование текста в JSON (с tool use / response_format).
    - generate_post — живой пост в группу продавцов.
    - generate_counter_offer — персональный торг с продавцом.
"""

from __future__ import annotations

import json
from typing import Any

from anthropic import AsyncAnthropic

from .config import settings

_client: AsyncAnthropic | None = None


def get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


async def complete_json(
    system: str,
    user: str,
    *,
    max_tokens: int = 1024,
    temperature: float = 0.0,
) -> dict[str, Any]:
    """Запрашивает у Claude ответ строго в JSON и парсит его.

    Используется в M1/M3 для структурирования текста.
    """
    msg = await get_client().messages.create(
        model=settings.claude_model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(block.text for block in msg.content if block.type == "text")
    text = text.strip()
    if text.startswith("```"):
        # срезаем ```json ... ```
        text = text.split("\n", 1)[1] if "\n" in text else text
        if text.endswith("```"):
            text = text[: -3]
    return json.loads(text)


async def complete_text(
    system: str,
    user: str,
    *,
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> str:
    """Свободная генерация текста (M2 пост, M5 торг)."""
    msg = await get_client().messages.create(
        model=settings.claude_model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(block.text for block in msg.content if block.type == "text").strip()
