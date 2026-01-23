FROM python:3.11-slim

# Установка зависимостей
RUN pip install --no-cache-dir aiohttp pysocks

# Копируем файлы
COPY proxy_server.py /app/proxy_server.py
COPY api.py /app/api.py

WORKDIR /app

# Порт для API и SOCKS5
EXPOSE 8080

CMD ["python", "proxy_server.py"]
