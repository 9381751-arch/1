"""Тонкая обёртка над supabase-py для удобного доступа из модулей."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from supabase import Client, create_client

from .config import settings


@lru_cache(maxsize=1)
def get_client() -> Client:
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


# ---------- requests ----------

def insert_request(data: dict[str, Any]) -> dict[str, Any]:
    res = get_client().table("requests").insert(data).execute()
    return res.data[0]


def update_request(request_id: str, data: dict[str, Any]) -> dict[str, Any]:
    res = (
        get_client()
        .table("requests")
        .update(data)
        .eq("id", request_id)
        .execute()
    )
    return res.data[0] if res.data else {}


def get_request(request_id: str) -> dict[str, Any] | None:
    res = get_client().table("requests").select("*").eq("id", request_id).single().execute()
    return res.data


# ---------- offers ----------

def insert_offer(data: dict[str, Any]) -> dict[str, Any]:
    res = get_client().table("offers").insert(data).execute()
    return res.data[0]


def update_offer(offer_id: str, data: dict[str, Any]) -> dict[str, Any]:
    res = get_client().table("offers").update(data).eq("id", offer_id).execute()
    return res.data[0] if res.data else {}


def list_offers(request_id: str) -> list[dict[str, Any]]:
    res = (
        get_client()
        .table("offers")
        .select("*")
        .eq("request_id", request_id)
        .order("total_cost_per_t")
        .execute()
    )
    return res.data or []


# ---------- settings ----------

def get_setting(key: str, default: str | None = None) -> str | None:
    res = get_client().table("settings").select("value").eq("key", key).execute()
    if res.data:
        return res.data[0]["value"]
    return default


def get_setting_float(key: str, default: float) -> float:
    raw = get_setting(key)
    try:
        return float(raw) if raw is not None else default
    except (TypeError, ValueError):
        return default


def get_setting_int(key: str, default: int) -> int:
    raw = get_setting(key)
    try:
        return int(raw) if raw is not None else default
    except (TypeError, ValueError):
        return default


# ---------- logs ----------

def log_event(
    event_type: str,
    *,
    request_id: str | None = None,
    offer_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> None:
    get_client().table("logs").insert(
        {
            "event_type": event_type,
            "request_id": request_id,
            "offer_id": offer_id,
            "payload": payload or {},
        }
    ).execute()
