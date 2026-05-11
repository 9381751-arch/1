FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Зависимости отдельным слоем — кешируется между сборками
COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install .

COPY src ./src

# Бот работает как long-poll процесс, без портов.
CMD ["python", "-m", "src.main"]
