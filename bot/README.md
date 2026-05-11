# Бот закупки шпунта

Python + aiogram 3 бот, который автоматизирует полный цикл закупки б/у шпунта.

## Модули

| Файл                              | Модуль | Назначение |
|-----------------------------------|--------|------------|
| `src/modules/m1_parse_request.py` | M1     | Парсинг входящей заявки из канала через Claude |
| `src/modules/m2_publish_post.py`  | M2     | Генерация и публикация поста в группу продавцов |
| `src/modules/m3_collect_offers.py`| M3     | Сбор и парсинг ответов продавцов |
| `src/modules/m4_costing.py`       | M4     | Расчёт себестоимости (цена + OSRM логистика) |
| `src/modules/m5_negotiation.py`   | M5     | Торговый раунд с ТОП-N продавцами |
| `src/modules/m6_report.py`        | M6     | Итоговый отчёт менеджеру + кнопки выбора |

## Запуск

```bash
# через uv (рекомендуется)
uv venv
uv pip install -e ".[dev]"
cp .env.example .env  # заполнить значения
uv run python -m src.main

# или через pip
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m src.main
```

## Тесты

```bash
uv run pytest
```

## Архитектура

`src/main.py` запускает aiogram polling. Хендлеры в `src/handlers/`:

- `channel.py` — слушает канал заявок (M1).
- `group.py` — слушает группу продавцов (M3).
- `private.py` — личка с ботом (уточнения, ответы продавцов, кнопки менеджера).

Модули `src/modules/` — чистая бизнес-логика, без aiogram. Хендлеры их вызывают.

## Деплой

Railway / VPS, постоянно работающий процесс. Webhook не нужен — long polling.
