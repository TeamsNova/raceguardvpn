FROM python:3.11-slim

# Копируем файлы
COPY proxy_server.py /app/proxy_server.py

WORKDIR /app

# Порт для API и SOCKS5
EXPOSE 8080

CMD ["python", "proxy_server.py"]
