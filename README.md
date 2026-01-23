# RaceGuard SOCKS5 Proxy Server

SOCKS5 прокси сервер для Railway.app - **полностью бесплатно!**

## Возможности:

- ✅ SOCKS5 прокси для обхода блокировок
- ✅ Работает с браузерами, Telegram, Discord, Steam
- ✅ 100GB трафика в месяц бесплатно (на 1 аккаунт)
- ✅ Можно создать 9 аккаунтов = 900GB трафика
- ✅ HTTP API для управления пользователями

## Деплой на Railway:

1. Зайди на railway.app
2. Нажми "New Project" → "Deploy from GitHub repo"
3. Выбери репозиторий `TeamsNova/raceguardvpn`
4. Railway автоматически задеплоит проект
5. Получи домен в Settings → Networking

## API Endpoints:

### GET /health
Проверка работоспособности

**Response:**
```json
{
  "status": "ok",
  "type": "socks5"
}
```

### GET /server-info
Информация о сервере

**Response:**
```json
{
  "type": "socks5",
  "host": "raceguardvpn-production.up.railway.app",
  "port": 1080,
  "users": 0
}
```

### POST /add-user
Добавить пользователя

**Request:**
```json
{
  "username": "user123",
  "password": "pass123"
}
```

**Response:**
```json
{
  "username": "user123",
  "host": "raceguardvpn-production.up.railway.app",
  "port": 1080,
  "config": "socks5://user123:pass123@raceguardvpn-production.up.railway.app:1080"
}
```

## Использование:

### В браузере (Chrome/Edge):
1. Настройки → Прокси-сервер
2. SOCKS5: `raceguardvpn-production.up.railway.app:1080`

### В Telegram:
1. Настройки → Данные и память → Прокси
2. SOCKS5
3. Сервер: `raceguardvpn-production.up.railway.app`
4. Порт: `1080`

### В приложении:
```python
import socks
import socket

socks.set_default_proxy(socks.SOCKS5, "raceguardvpn-production.up.railway.app", 1080)
socket.socket = socks.socksocket
```

## Лимиты Railway (бесплатно):

- $5 кредитов в месяц
- 500 часов выполнения
- 100GB исходящего трафика

**Совет:** Создай 9 аккаунтов (6 Google + 3 GitHub) = 900GB трафика!
