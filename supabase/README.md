# Supabase

## Структура

- `migrations/0001_init.sql` — базовая схема: `requests`, `offers`, `settings`, `logs`.
- `seed.sql` — дефолтные значения настроек.

## Применение

### Через Supabase Studio (быстро)

1. SQL Editor → вставить содержимое `migrations/0001_init.sql` → Run.
2. SQL Editor → вставить `seed.sql` → Run.

### Через CLI

```bash
supabase link --project-ref <ref>
supabase db push
psql "$DATABASE_URL" -f supabase/seed.sql
```

## Таблицы

| Таблица    | Назначение                                            |
|------------|-------------------------------------------------------|
| requests   | Заявки клиентов (исходный текст + структурные поля)   |
| offers     | Предложения продавцов + расчёт себеса + торг          |
| settings   | Настройки (тарифы, дедлайны, TG-ID) — управляются UI  |
| logs       | События (входящие сообщения, парсинг, отправки)       |

## Статусы заявки

`new → clarifying → published → collecting → negotiating → awaiting_decision → closed`

## RLS

В MVP не настраивается — дашборд использует service role key из серверных
компонентов. При выходе на прод добавить отдельную миграцию с политиками.
