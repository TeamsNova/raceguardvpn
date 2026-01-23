# RaceGuard HTTP Proxy Server

HTTP/HTTPS прокси сервер для Railway.app - **полностью бесплатно!**

## Возможности:

- ✅ HTTP/HTTPS прокси для обхода блокировок
- ✅ Работает с браузерами, приложениями
- ✅ 100GB трафика в месяц бесплатно (на 1 аккаунт)
- ✅ Можно создать 9 аккаунтов = 900GB трафика
- ✅ HTTP API для управления пользователями

## Использование:

### В браузере (Chrome/Edge):
1. Настройки → Прокси-сервер
2. HTTP прокси: `raceguardvpn-production.up.railway.app:443`
3. HTTPS прокси: `raceguardvpn-production.up.railway.app:443`

### В Windows (системный прокси):
```
Настройки → Сеть и Интернет → Прокси
HTTP: raceguardvpn-production.up.railway.app:443
```

## API Endpoints:

### GET /health
```json
{"status": "ok", "type": "http_proxy"}
```

### GET /server-info
```json
{
  "type": "http_proxy",
  "host": "raceguardvpn-production.up.railway.app",
  "port": 443,
  "users": 0
}
```

### POST /add-user
**Request:**
```json
{"username": "user123", "password": "pass123"}
```

**Response:**
```json
{
  "username": "user123",
  "host": "raceguardvpn-production.up.railway.app",
  "port": 443,
  "type": "http",
  "config": "http://user123:pass123@raceguardvpn-production.up.railway.app:443"
}
```
