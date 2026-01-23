# RaceGuard VPN Server

WireGuard VPN сервер для Railway.app

## Деплой на Railway:

1. Создай новый репозиторий на GitHub
2. Загрузи эти файлы в репозиторий
3. Зайди на railway.app
4. Нажми "New Project" → "Deploy from GitHub repo"
5. Выбери свой репозиторий
6. Railway автоматически задеплоит проект

## API Endpoints:

### GET /health
Проверка работоспособности сервера

### GET /server-info
Получить информацию о сервере (публичный ключ, endpoint)

### POST /add-client
Добавить нового клиента

**Request:**
```json
{
  "name": "client1"
}
```

**Response:**
```json
{
  "config": "...",
  "client_ip": "10.13.13.2",
  "private_key": "...",
  "public_key": "..."
}
```

## Использование:

1. После деплоя получи URL проекта на Railway
2. Вызови `/add-client` для создания конфига клиента
3. Используй полученный конфиг в WireGuard клиенте

## Порты:

- 51820/udp - WireGuard
- 8080/tcp - API сервер

## Переменные окружения:

Railway автоматически устанавливает:
- `RAILWAY_PUBLIC_DOMAIN` - домен проекта
