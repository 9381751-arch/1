"""Шедулер для замыкания цикла:

  publish_new          — берёт заявки status=new из ручного ввода и публикует в группу;
  close_collection     — закрывает сбор предложений по истечении дедлайна,
                         считает себес (M4) и запускает торг (M5);
  finalize_negotiation — закрывает торговый раунд по истечении дедлайна,
                         проставляет timeout не ответившим, шлёт отчёт менеджеру (M6).

Все три джобы запускаются раз в минуту, идемпотентны (status проверяется),
выполняются в одном процессе с aiogram polling.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from . import db
from .modules import m2_publish_post, m4_costing, m5_negotiation, m6_report

log = logging.getLogger("azimut.scheduler")

POLL_INTERVAL_SECONDS = 60


# ---------- 1. публикация заявок из ручного ввода ----------

async def publish_new_requests(bot: Bot) -> None:
    res = (
        db.get_client()
        .table("requests")
        .select("*")
        .eq("status", "new")
        .eq("source", "manual")
        .execute()
    )
    for req in res.data or []:
        # пропускаем, если не хватает обязательных
        if not (req.get("grade") and req.get("quantity_t")
                and req.get("region") and req.get("deadline")):
            db.update_request(req["id"], {"status": "clarifying"})
            continue
        try:
            post_text = await m2_publish_post.generate_post(req)
            msg_id = await m2_publish_post.publish(bot, post_text)
            db.update_request(
                req["id"],
                {
                    "claude_post_text": post_text,
                    "published_msg_id": msg_id,
                    "published_at": "now()",
                    "status": "collecting",
                },
            )
            db.log_event(
                "request_published",
                request_id=req["id"],
                payload={"msg_id": msg_id, "trigger": "scheduler"},
            )
            log.info("published manual request %s as msg %s", req["id"], msg_id)
        except Exception:  # noqa: BLE001
            log.exception("failed to publish request %s", req["id"])


# ---------- 2. закрытие сбора → торг ----------

async def close_collection_deadlines(bot: Bot) -> None:
    deadline_hours = db.get_setting_float("collect_deadline_hours", 4.0)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=deadline_hours)

    res = (
        db.get_client()
        .table("requests")
        .select("*")
        .eq("status", "collecting")
        .lt("published_at", cutoff.isoformat())
        .execute()
    )
    for req in res.data or []:
        try:
            await m4_costing.recalculate_request(req["id"])
            invited = await m5_negotiation.run(bot, req["id"])
            db.log_event(
                "negotiation_started",
                request_id=req["id"],
                payload={"top_count": len(invited), "trigger": "scheduler"},
            )
            log.info(
                "request %s: collection closed, invited %d sellers",
                req["id"],
                len(invited),
            )
        except Exception:  # noqa: BLE001
            log.exception("failed to close collection for %s", req["id"])


# ---------- 3. закрытие торга → отчёт менеджеру ----------

async def finalize_negotiation_deadlines(bot: Bot) -> None:
    deadline_hours = db.get_setting_float("negotiation_deadline_hours", 2.0)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=deadline_hours)

    res = (
        db.get_client()
        .table("requests")
        .select("*")
        .eq("status", "negotiating")
        .lt("negotiation_started_at", cutoff.isoformat())
        .execute()
    )
    for req in res.data or []:
        try:
            # проставляем timeout всем приглашённым, кто не ответил
            offers = (
                db.get_client()
                .table("offers")
                .select("id")
                .eq("request_id", req["id"])
                .eq("negotiation_status", "invited")
                .execute()
            )
            for offer in offers.data or []:
                db.update_offer(offer["id"], {"negotiation_status": "timeout"})

            await m6_report.send(bot, req["id"])
            db.log_event(
                "report_sent",
                request_id=req["id"],
                payload={"trigger": "scheduler"},
            )
            log.info("request %s: negotiation closed, report sent", req["id"])
        except Exception:  # noqa: BLE001
            log.exception("failed to finalize negotiation for %s", req["id"])


# ---------- setup ----------

def setup(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        publish_new_requests,
        "interval",
        seconds=POLL_INTERVAL_SECONDS,
        kwargs={"bot": bot},
        id="publish_new",
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        close_collection_deadlines,
        "interval",
        seconds=POLL_INTERVAL_SECONDS,
        kwargs={"bot": bot},
        id="close_collection",
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        finalize_negotiation_deadlines,
        "interval",
        seconds=POLL_INTERVAL_SECONDS,
        kwargs={"bot": bot},
        id="finalize_negotiation",
        max_instances=1,
        coalesce=True,
    )
    return scheduler
