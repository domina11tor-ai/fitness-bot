
FROM python:3.10-slim

WORKDIR /app

# Сначала копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем абсолютно все файлы проекта в контейнер
COPY . .

# Явно указываем полный путь к python внутри контейнера
CMD ["/usr/local/bin/python", "bot.py"]
