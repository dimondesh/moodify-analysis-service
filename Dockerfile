# --- Базовый образ ---
    FROM python:3.9-slim

    # --- Установка системных зависимостей ---
    # Essentia требует некоторые системные библиотеки для работы с аудио
    RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        libavformat-dev \
        libavcodec-dev \
        libavutil-dev \
        libswresample-dev \
        # libavresample-dev удален, так как он устарел
        && rm -rf /var/lib/apt/lists/*
    
    # --- Настройка рабочей директории ---
    WORKDIR /app
    
    # --- Копирование и установка Python-зависимостей ---
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    
    # --- Копирование кода приложения ---
    COPY . .
    
    # --- Запуск приложения ---
    # Используем gunicorn - это продакшн-сервер.
    CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]