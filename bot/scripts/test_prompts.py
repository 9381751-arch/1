"""Прогон M1/M2/M3/M5 на реальном Claude API без БД и Telegram.

Используется для калибровки промптов на примерах из реальной переписки.

    ANTHROPIC_API_KEY=... python scripts/test_prompts.py
"""

from __future__ import annotations

import asyncio
import os
import sys

# заглушки для pydantic-settings, чтобы импорт config не падал
os.environ.setdefault("SUPABASE_URL", "https://stub.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "stub")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "stub")
os.environ.setdefault("TG_CHANNEL_REQUESTS_ID", "1")
os.environ.setdefault("TG_GROUP_SELLERS_ID", "2")
os.environ.setdefault("TG_MANAGER_ID", "3")

if not os.getenv("ANTHROPIC_API_KEY"):
    print("ERROR: ANTHROPIC_API_KEY не задан", file=sys.stderr)
    sys.exit(1)

SAMPLE_REQUEST = (
    "Ребят, нужен шпунт Л4, длина от 10м, около 500 тонн, состояние 2-3. "
    "СПб или ЛО, нужно до 15 июня."
)

SAMPLE_OFFER = (
    "Привет! Есть Л4, длина 12м, 2 состояние, 300т, цена 18500 за тонну с НДС. "
    "Отгрузка из Колпино, готов через 3 дня."
)


def section(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


async def main() -> None:
    from src.modules import (
        m1_parse_request,
        m2_publish_post,
        m3_collect_offers,
        m5_negotiation,
    )

    section("M1: парсинг заявки")
    print(f"Вход: {SAMPLE_REQUEST}\n")
    parsed = await m1_parse_request.parse(SAMPLE_REQUEST)
    for k, v in parsed.items():
        print(f"  {k}: {v}")
    miss = m1_parse_request.missing_required(parsed)
    print(f"\nНе хватает обязательных: {miss or 'всё ок'}")

    section("M2: пост в группу продавцов")
    post = await m2_publish_post.generate_post(parsed)
    print(post)

    section("M3: парсинг ответа продавца")
    print(f"Вход: {SAMPLE_OFFER}\n")
    parsed_offer = await m3_collect_offers.parse(SAMPLE_OFFER)
    for k, v in parsed_offer.items():
        print(f"  {k}: {v}")

    section("M5: контрпредложение")
    fake_offer = {
        "seller_name": "Иван",
        "price_per_t": 18500,
        "quantity_t": 300,
        "location": "Колпино",
    }
    msg = await m5_negotiation._generate_message(fake_offer, target=17200)
    print(msg)


if __name__ == "__main__":
    asyncio.run(main())
