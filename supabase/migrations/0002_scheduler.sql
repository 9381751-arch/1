-- ============================================================
-- Миграция 0002: дедлайны и шедулер
--   negotiation_started_at — для отсчёта дедлайна торгового раунда
-- ============================================================

alter table public.requests
    add column if not exists negotiation_started_at timestamptz;

create index if not exists requests_status_published_at_idx
    on public.requests (status, published_at);

create index if not exists requests_status_negotiation_started_idx
    on public.requests (status, negotiation_started_at);
