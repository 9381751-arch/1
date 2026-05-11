"""Smoke-тесты: проверяем, что модули импортируются и чистая логика работает."""

from __future__ import annotations

import os

# заглушки env, чтобы pydantic-settings не падал
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "stub")
os.environ.setdefault("ANTHROPIC_API_KEY", "stub")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "stub")
os.environ.setdefault("TG_CHANNEL_REQUESTS_ID", "1")
os.environ.setdefault("TG_GROUP_SELLERS_ID", "2")
os.environ.setdefault("TG_MANAGER_ID", "3")


def test_imports() -> None:
    from src import config, db, llm, osrm, scheduler  # noqa: F401
    from src.handlers import channel, group, private  # noqa: F401
    from src.modules import (  # noqa: F401
        m1_parse_request,
        m2_publish_post,
        m3_collect_offers,
        m4_costing,
        m5_negotiation,
        m6_report,
    )


def test_scheduler_setup() -> None:
    """Шедулер должен собираться с тремя джобами и не падать на старте."""
    from unittest.mock import MagicMock

    from src.scheduler import setup

    bot = MagicMock()
    scheduler = setup(bot)
    job_ids = {j.id for j in scheduler.get_jobs()}
    assert job_ids == {"publish_new", "close_collection", "finalize_negotiation"}


def test_m1_missing_required() -> None:
    from src.modules.m1_parse_request import missing_required

    assert set(missing_required({  # type: ignore[arg-type]
        "grade": None,
        "length_m": 12,
        "quantity_t": 500,
        "region": None,
        "deadline": None,
        "condition": None,
        "extra_conditions": None,
    })) == {"grade", "region", "deadline"}


def test_m3_missing_required() -> None:
    from src.modules.m3_collect_offers import missing_required

    miss = missing_required({  # type: ignore[arg-type]
        "grade": "Л4",
        "length_m": 12,
        "condition": 2,
        "quantity_t": 300,
        "price_per_t": None,
        "vat_type": None,
        "location": "СПб",
        "ready_date": None,
        "comment": None,
    })
    assert set(miss) == {"price_per_t", "vat_type", "ready_date"}
