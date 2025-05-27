# Базовый образ Python
FROM python:3.11

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости для PostgreSQL (если нужно)
RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Копируем файлы проекта
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости (без создания виртуального окружения)
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Копируем всё приложение
COPY . .

# Открываем порт
EXPOSE 8000

# Команда запуска
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
