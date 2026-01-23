#!/bin/bash

# Генерация ключей WireGuard
mkdir -p /config/wg0
cd /config/wg0

# Генерируем серверные ключи если их нет
if [ ! -f "privatekey" ]; then
    wg genkey | tee privatekey | wg pubkey > publickey
fi

SERVER_PRIVATE_KEY=$(cat privatekey)
SERVER_PUBLIC_KEY=$(cat publickey)

# Создаем конфиг WireGuard
cat > /config/wg0.conf <<EOF
[Interface]
Address = 10.13.13.1/24
ListenPort = 51820
PrivateKey = $SERVER_PRIVATE_KEY
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
EOF

# Включаем IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward

# Запускаем WireGuard
wg-quick up wg0

# Запускаем API сервер
python3 /api.py &

# Держим контейнер запущенным
tail -f /dev/null
