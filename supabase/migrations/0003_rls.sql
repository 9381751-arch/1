-- ============================================================
-- Миграция 0003: RLS (Row Level Security)
--
-- Модель доступа в MVP:
--   - анонимный браузерный клиент (Supabase Auth с anon key) — НИЧЕГО не видит;
--   - авторизованные пользователи (через Supabase Auth) — читают всё;
--   - service role (бот + Server Actions дашборда) — полный доступ, RLS обходит.
--
-- На прод-этапе сюда добавить per-role (менеджер, наблюдатель) политики.
-- ============================================================

alter table public.requests enable row level security;
alter table public.offers   enable row level security;
alter table public.settings enable row level security;
alter table public.logs     enable row level security;

-- ---------- requests ----------
drop policy if exists "auth read requests"   on public.requests;
drop policy if exists "auth write requests"  on public.requests;
create policy "auth read requests"  on public.requests for select to authenticated using (true);
create policy "auth write requests" on public.requests for all    to authenticated using (true) with check (true);

-- ---------- offers ----------
drop policy if exists "auth read offers"   on public.offers;
drop policy if exists "auth write offers"  on public.offers;
create policy "auth read offers"  on public.offers for select to authenticated using (true);
create policy "auth write offers" on public.offers for all    to authenticated using (true) with check (true);

-- ---------- settings ----------
drop policy if exists "auth read settings"   on public.settings;
drop policy if exists "auth write settings"  on public.settings;
create policy "auth read settings"  on public.settings for select to authenticated using (true);
create policy "auth write settings" on public.settings for all    to authenticated using (true) with check (true);

-- ---------- logs (только чтение из UI) ----------
drop policy if exists "auth read logs" on public.logs;
create policy "auth read logs" on public.logs for select to authenticated using (true);
-- запись в logs — только service role (бот). Политик для authenticated нет.
