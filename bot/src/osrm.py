"""Расчёт расстояний через OSRM.

В MVP — простой geocoding через Nominatim + /route/v1/driving у OSRM.
Для прода стоит закешировать координаты часто встречающихся городов в БД,
а лучше поднять свой OSRM-инстанс.
"""

from __future__ import annotations

import httpx

from .config import settings

_NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
_USER_AGENT = "azimut-bot/0.1 (+https://azimut-stroy.pro)"


async def geocode(city: str) -> tuple[float, float] | None:
    """Возвращает (lon, lat) для города или None."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            _NOMINATIM_URL,
            params={"q": city, "format": "json", "limit": 1, "countrycodes": "ru"},
            headers={"User-Agent": _USER_AGENT},
        )
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        return float(data[0]["lon"]), float(data[0]["lat"])


async def distance_km(from_city: str, to_city: str) -> float | None:
    """Возвращает расстояние по дорогам в км, либо None если не удалось посчитать."""
    a = await geocode(from_city)
    b = await geocode(to_city)
    if a is None or b is None:
        return None

    url = f"{settings.osrm_base_url.rstrip('/')}/route/v1/driving/{a[0]},{a[1]};{b[0]},{b[1]}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(url, params={"overview": "false"})
        r.raise_for_status()
        data = r.json()

    if data.get("code") != "Ok" or not data.get("routes"):
        return None
    return data["routes"][0]["distance"] / 1000.0
