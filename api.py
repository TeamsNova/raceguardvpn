#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import subprocess
import os

class VPNHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode())
        
        elif self.path == '/server-info':
            try:
                with open('/config/wg0/publickey', 'r') as f:
                    public_key = f.read().strip()
                
                # Получаем внешний IP
                endpoint = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'unknown')
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    'public_key': public_key,
                    'endpoint': endpoint,
                    'port': 51820
                }
                
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/add-client':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                client_name = data.get('name', 'client')
                
                # Генерируем ключи клиента
                private_key = subprocess.check_output(['wg', 'genkey']).decode().strip()
                public_key = subprocess.check_output(['wg', 'pubkey'], input=private_key.encode()).decode().strip()
                
                # Получаем следующий доступный IP
                client_ip = self.get_next_ip()
                
                # Добавляем клиента в конфиг
                with open('/config/wg0.conf', 'a') as f:
                    f.write(f'\n[Peer]\n')
                    f.write(f'PublicKey = {public_key}\n')
                    f.write(f'AllowedIPs = {client_ip}/32\n')
                
                # Перезагружаем WireGuard
                subprocess.run(['wg-quick', 'down', 'wg0'], check=False)
                subprocess.run(['wg-quick', 'up', 'wg0'], check=True)
                
                # Получаем серверный публичный ключ
                with open('/config/wg0/publickey', 'r') as f:
                    server_public_key = f.read().strip()
                
                endpoint = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'unknown')
                
                # Генерируем конфиг для клиента
                client_config = f"""[Interface]
PrivateKey = {private_key}
Address = {client_ip}/24
DNS = 1.1.1.1

[Peer]
PublicKey = {server_public_key}
Endpoint = {endpoint}:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    'config': client_config,
                    'client_ip': client_ip,
                    'private_key': private_key,
                    'public_key': public_key
                }
                
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def get_next_ip(self):
        """Получить следующий доступный IP адрес"""
        # Простая логика - берем последний октет от 2 до 254
        try:
            with open('/config/wg0.conf', 'r') as f:
                content = f.read()
                # Ищем все AllowedIPs
                import re
                ips = re.findall(r'AllowedIPs = 10\.13\.13\.(\d+)/32', content)
                if ips:
                    last_ip = max([int(ip) for ip in ips])
                    return f'10.13.13.{last_ip + 1}'
                else:
                    return '10.13.13.2'
        except:
            return '10.13.13.2'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), VPNHandler)
    print(f'API Server running on port {port}')
    server.serve_forever()
