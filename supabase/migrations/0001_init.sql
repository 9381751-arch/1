-- ============================================================
-- АЗИМУТ — автоматизация закупки б/у шпунта
-- Миграция 0001: базовая схема (requests, offers, settings, logs)
-- ============================================================

create extension if not exists "uuid-ossp";

-- ---------- requests ----------
-- Заявки клиентов: исходный текст из канала + структурированные поля.
create table if not exists public.requests (
    id                  uuid primary key default uuid_generate_v4(),
    created_at          timestamptz not null default now(),
    updated_at          timestamptz not null default now(),

    source              text not null default 'tg_channel',  -- tg_channel | manual
    source_msg_id       bigint,
    source_user_id      bigint,
    raw_text            text,

    grade               text,                  -- марка шпунта (Л4, Л5, и т.д.)
    length_m            numeric,
    quantity_t          numeric,
    region              text,
    deadline            date,
    condition           int,                   -- 1/2/3
    extra_conditions    text,

    status              text not null default 'new',
    -- new | clarifying | published | collecting | negotiating
    -- | awaiting_decision | closed | cancelled

    claude_post_text    text,                  -- сгенерированный пост для группы
    published_msg_id    bigint,                -- id поста в группе продавцов
    published_at        timestamptz,

    closed_at           timestamptz,
    winner_offer_id     uuid                   -- заполняется после выбора менеджера
);

create index if not exists requests_status_idx on public.requests (status);
create index if not exists requests_created_at_idx on public.requests (created_at desc);

-- ---------- offers ----------
-- Предложения от продавцов.
create table if not exists public.offers (
    id                  uuid primary key default uuid_generate_v4(),
    request_id          uuid not null references public.requests(id) on delete cascade,
    created_at          timestamptz not null default now(),
    updated_at          timestamptz not null default now(),

    source              text not null,         -- tg_group | tg_private
    source_msg_id       bigint,
    seller_tg_id        bigint not null,
    seller_username     text,
    seller_name         text,                  -- имя/компания

    raw_text            text,

    grade               text,
    length_m            numeric,
    condition           int,
    quantity_t          numeric,
    price_per_t         numeric,
    vat_type            text,                  -- with_vat | no_vat | usn
    location            text,
    ready_date          date,
    comment             text,

    -- расчётные поля (M4)
    distance_km         numeric,
    logistics_per_t     numeric,
    total_cost_per_t    numeric,
    rank                int,                   -- место по себесу (1 — лучший)

    -- торг (M5)
    negotiation_status  text default 'pending',
    -- pending | invited | accepted | rejected | timeout
    counter_price       numeric,
    final_price         numeric,
    negotiated_at       timestamptz
);

create index if not exists offers_request_idx on public.offers (request_id);
create index if not exists offers_seller_idx on public.offers (seller_tg_id);
create index if not exists offers_total_cost_idx on public.offers (request_id, total_cost_per_t);

alter table public.requests
    add constraint requests_winner_offer_fk
    foreign key (winner_offer_id) references public.offers(id) on delete set null;

-- ---------- settings ----------
-- Все управляемые из дашборда параметры в формате key/value.
create table if not exists public.settings (
    key             text primary key,
    value           text,
    description     text,
    updated_at      timestamptz not null default now()
);

-- ---------- logs ----------
-- Лента событий: вход. сообщения, парсинг, отправка, торг.
create table if not exists public.logs (
    id              uuid primary key default uuid_generate_v4(),
    created_at      timestamptz not null default now(),
    event_type      text not null,
    request_id      uuid references public.requests(id) on delete set null,
    offer_id        uuid references public.offers(id) on delete set null,
    payload         jsonb
);

create index if not exists logs_created_at_idx on public.logs (created_at desc);
create index if not exists logs_event_type_idx on public.logs (event_type);

-- ---------- триггер updated_at ----------
create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists requests_set_updated_at on public.requests;
create trigger requests_set_updated_at
    before update on public.requests
    for each row execute function public.set_updated_at();

drop trigger if exists offers_set_updated_at on public.offers;
create trigger offers_set_updated_at
    before update on public.offers
    for each row execute function public.set_updated_at();
