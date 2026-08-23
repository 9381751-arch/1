#!/usr/bin/env bash
# Обновление калькулятора «Каркас·КМ» на сервере: тянет index.html из репозитория
# и кладёт в веб-корень. Никаких ключей и доступа извне — сервер ходит сам.
#
#   SRC  — откуда брать (по умолчанию main публичного репозитория)
#   DEST — куда положить (по умолчанию /var/www/karkas/index.html)
#
# Ручной запуск:  sudo karkas-update
# Автообновление: systemd-таймер karkas-update.timer (см. соседние файлы)
set -euo pipefail

SRC="${SRC:-https://raw.githubusercontent.com/9381751-arch/1/main/index.html}"
DEST="${DEST:-/var/www/karkas/index.html}"
ETAG="${DEST}.etag"
MIN_SIZE="${MIN_SIZE:-20000}"     # страховка от обрезанной закачки, байт

install -d -m 0755 "$(dirname "$DEST")"
tmp="$(mktemp "${DEST}.XXXXXX")"
trap 'rm -f "$tmp"' EXIT

# --etag-compare шлёт If-None-Match: если на сервере то же самое, придёт 304
# и curl оставит файл пустым — значит обновлять нечего
curl -fsSL --max-time 60 \
     --etag-compare "$ETAG" --etag-save "$ETAG" \
     -o "$tmp" "$SRC"

if [ ! -s "$tmp" ]; then
  echo "без изменений: $(basename "$DEST") уже актуален"
  exit 0
fi

size=$(wc -c < "$tmp")
if [ "$size" -lt "$MIN_SIZE" ] || ! grep -q 'Каркас' "$tmp"; then
  echo "отказ: закачка не похожа на страницу калькулятора (${size} байт)" >&2
  rm -f "$ETAG"                    # чтобы следующий запуск не считал файл свежим
  exit 1
fi

chmod 0644 "$tmp"
mv -f "$tmp" "$DEST"               # подмена одним движением, без «полупустой» страницы
trap - EXIT
echo "обновлено: $DEST (${size} байт)"
