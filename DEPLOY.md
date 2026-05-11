# Развёртывание

Полная инструкция для запуска системы с нуля. Время — ~30 минут.

## 1. Supabase (БД)

1. Зарегистрироваться: https://supabase.com → New project.
2. Регион: `Frankfurt (eu-central-1)` для близости к РФ.
3. Подождать ~2 минуты, пока провизионируется.
4. SQL Editor → New query → последовательно выполнить:
   - `supabase/migrations/0001_init.sql`
   - `supabase/migrations/0002_scheduler.sql`
   - `supabase/migrations/0003_rls.sql`
   - `supabase/seed.sql`
5. Создать пользователя дашборда:
   - Authentication → Users → Add user → Email + Password (запомнить пароль).
   - Email confirmation отключить: Authentication → Providers → Email → выключить "Confirm email".
6. Записать из Project Settings → API:
   - `Project URL` → `SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_URL`
   - `anon public` → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `service_role` (секрет!) → `SUPABASE_SERVICE_ROLE_KEY`

## 2. Telegram

1. @BotFather → `/newbot` → имя → username → получить **bot token**.
2. Добавить бота в группу продавцов и канал заявок **как администратора**:
   - в группе: дать право читать все сообщения (Privacy off через `/setprivacy`).
   - в канале: дать право публиковать.
3. Узнать `chat_id`:
   - бот @userinfobot или @getmyid_bot — для личного ID менеджера;
   - переслать любое сообщение из группы/канала в @userinfobot — получите ID канала и группы (с минусом для групп).

## 3. Claude API

1. https://console.anthropic.com → Settings → API Keys → Create Key.
2. Записать ключ → `ANTHROPIC_API_KEY`.
3. Минимальный план: Build (платный, $5 на старт хватит на тысячи запросов).

## 4. Дашборд на Vercel

1. https://vercel.com → New Project → Import репозиторий.
2. Root Directory: `dashboard`.
3. Environment Variables:
   ```
   NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=...
   SUPABASE_SERVICE_ROLE_KEY=...
   ```
4. Deploy.
5. Domains → Add → `admin.azimut-stroy.pro` → настроить DNS CNAME на `cname.vercel-dns.com`.
6. Открыть → войти под пользователем из п.1.5.

## 5. Бот на Railway

1. https://railway.app → New Project → Deploy from GitHub.
2. Root Directory: `bot`.
3. Build: Dockerfile (определится автоматически).
4. Variables:
   ```
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=...
   ANTHROPIC_API_KEY=...
   TELEGRAM_BOT_TOKEN=...
   TG_CHANNEL_REQUESTS_ID=-100...
   TG_GROUP_SELLERS_ID=-100...
   TG_MANAGER_ID=...
   OSRM_BASE_URL=https://router.project-osrm.org
   CLAUDE_MODEL=claude-sonnet-4-6
   LOG_LEVEL=INFO
   ```
5. Deploy → проверить логи: должна быть строка `bot starting (model=claude-sonnet-4-6)`
   и `scheduler started (3 jobs, interval 60s)`.

## 6. Проверка end-to-end

1. Открыть дашборд, авторизоваться.
2. Создать тестовую заявку через **Новая заявка**.
3. Через минуту бот должен опубликовать пост в группе продавцов.
4. Ответить в группе от тестового аккаунта (с ценой/городом).
5. В карточке заявки появится оффер.
6. Подождать `collect_deadline_hours` (по умолчанию 4ч — на тест можно временно
   уменьшить через **Настройки** до 0.05 ≈ 3 минуты).
7. Бот напишет торг в личку «продавцу», после ответа — отправит отчёт менеджеру.

## Замечания по эксплуатации

- **Стоимость**: Supabase free tier (500 МБ), Vercel hobby (бесплатно), Railway
  $5 кредитов/мес, Claude API — pay-as-you-go.
- **OSRM**: публичный демо-сервер ограничен по rate limit. На прод-нагрузке
  поднять свой инстанс или взять Yandex / 2GIS API.
- **Логи**: bot пишет в stdout (Railway → Logs), плюс события в Supabase
  таблицу `logs`.
- **Бэкапы**: Supabase делает daily snapshot автоматически (free tier — 7 дней).
