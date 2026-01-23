FROM linuxserver/wireguard:latest

# Установка дополнительных пакетов
RUN apk add --no-cache python3 py3-pip iptables

# Копируем скрипты
COPY start.sh /start.sh
COPY api.py /api.py

RUN chmod +x /start.sh

# Порты
EXPOSE 51820/udp
EXPOSE 8080/tcp

CMD ["/start.sh"]
