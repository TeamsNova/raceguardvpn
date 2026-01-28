# RaceGuard HTTP Proxy Server

HTTP/HTTPS прокси сервер для Railway.app - **полностью бесплатно!**

## Возможности:

- ✅ HTTP/HTTPS прокси для обхода блокировок
- ✅ **Встроенная аутентификация пользователей (Basic Auth)**
- ✅ Работает с браузерами, приложениями
- ✅ 100GB трафика в месяц бесплатно (на 1 аккаунт)
- ✅ Можно создать 9 аккаунтов = 900GB трафика
- ✅ HTTP API для управления пользователями
- ✅ Оптимизированная обработка CONNECT-запросов

## Использование:

### Шаг 1: Создать пользователя
```bash
curl -X POST https://raceguardvpn-production.up.railway.app/add-user \
  -H "Content-Type: application/json" \
  -d '{"username": "myuser", "password": "mypass"}'
```

### Шаг 2: Настроить прокси с аутентификацией

#### В браузере (Chrome/Edge):
1. Настройки → Прокси-сервер
2. HTTP прокси: `raceguardvpn-production.up.railway.app:443`
3. HTTPS прокси: `raceguardvpn-production.up.railway.app:443`
4. При первом подключении браузер запросит логин и пароль

#### В Windows (системный прокси):
```
Настройки → Сеть и Интернет → Прокси
HTTP: raceguardvpn-production.up.railway.app:443
Логин: myuser
Пароль: mypass
```

#### В коде (Python):
```python
import urllib.request

proxy = urllib.request.ProxyHandler({
    'http': 'http://myuser:mypass@raceguardvpn-production.up.railway.app:443',
    'https': 'http://myuser:mypass@raceguardvpn-production.up.railway.app:443'
})
opener = urllib.request.build_opener(proxy)
urllib.request.install_opener(opener)
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

## Безопасность:

- 🔐 **Аутентификация включается автоматически** после добавления первого пользователя
- 🔒 Все прокси-запросы требуют Basic Authentication (HTTP код 407)
- ✅ Публичные endpoint'ы `/health`, `/server-info`, `/add-user` остаются доступными без аутентификации
- ⚡ Оптимизированная обработка HTTPS CONNECT с использованием `select()` вместо активного ожидания

## Тестирование:

```bash
python3 test_proxy.py
```

## Развертывание на Railway:

1. Fork этого репозитория
2. Создайте новый проект на [Railway.app](https://railway.app)
3. Подключите ваш GitHub репозиторий
4. Railway автоматически соберет и задеплоит прокси
5. После деплоя создайте пользователя через `/add-user`
