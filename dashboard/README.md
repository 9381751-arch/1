# Дашборд закупки шпунта

Next.js 14 (App Router) + TypeScript + Tailwind + Supabase.

## Страницы

| Роут                       | Назначение                                      |
|----------------------------|-------------------------------------------------|
| `/login`                   | Вход (Supabase Auth, email + пароль)            |
| `/`                        | Список заявок с фильтрами                       |
| `/requests/[id]`           | Карточка заявки (предложения, торг, действия)   |
| `/requests/new`            | Ручной ввод заявки                              |
| `/settings`                | Управление константами (тарифы, дедлайны, ID)   |

## Запуск

```bash
pnpm install   # или npm install / yarn
cp .env.example .env.local
pnpm dev
```

## Структура

```
app/                    Роуты App Router
  layout.tsx            Корневой layout, навигация
  globals.css           Tailwind + переменные темы
  login/page.tsx
  page.tsx              Список заявок
  requests/
    new/page.tsx
    [id]/page.tsx
  settings/page.tsx
components/ui/          shadcn/ui-подобные примитивы
lib/
  supabase/
    client.ts           Клиент для браузерных компонентов
    server.ts           Клиент для серверных компонентов / Server Actions
  utils.ts              cn() и т.п.
```

## Деплой

Vercel: подключить репозиторий, задать корневой каталог `dashboard`, прописать
переменные из `.env.example`.

## Авторизация

В MVP — Supabase Auth, email + пароль, single-user (менеджер). Без RLS,
дашборд использует service role key из серверных компонентов.
