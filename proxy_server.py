#!/usr/bin/env python3
import socket
import os
import json
import base64
import select
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request

# База данных пользователей
USERS = {}

class HTTPProxyHandler(BaseHTTPRequestHandler):
    def _check_auth(self):
        """Проверка Basic Authentication через Proxy-Authorization"""
        if not USERS:
            return True
        
        auth_header = self.headers.get('Proxy-Authorization', '')
        if not auth_header.startswith('Basic '):
            return False
        
        try:
            credentials = base64.b64decode(auth_header[6:]).decode('utf-8')
            username, password = credentials.split(':', 1)
            
            if username in USERS and USERS[username]['password'] == password:
                return True
        except Exception as e:
            print(f"Auth error: {e}")
        
        return False
    
    def _send_auth_required(self):
        """Отправка 407 Proxy Authentication Required"""
        self.send_response(407)
        self.send_header('Proxy-Authenticate', 'Basic realm="Proxy"')
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Proxy Authentication Required')
    
    def do_CONNECT(self):
        """Handle HTTPS CONNECT requests"""
        if not self._check_auth():
            self._send_auth_required()
            return
        
        target_sock = None
        try:
            # Парсим хост и порт
            host, port = self.path.split(':')
            port = int(port)
            
            # Подключаемся к целевому серверу
            target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_sock.connect((host, port))
            
            # Отправляем успешный ответ
            self.send_response(200, 'Connection Established')
            self.end_headers()
            
            # Пересылаем данные в обе стороны используя select
            self.connection.setblocking(0)
            target_sock.setblocking(0)
            
            sockets = [self.connection, target_sock]
            
            while True:
                readable, _, exceptional = select.select(sockets, [], sockets, 1.0)
                
                if exceptional:
                    break
                
                for sock in readable:
                    if sock is self.connection:
                        # От клиента к серверу
                        try:
                            data = self.connection.recv(8192)
                            if data:
                                target_sock.sendall(data)
                            else:
                                return
                        except:
                            return
                    elif sock is target_sock:
                        # От сервера к клиенту
                        try:
                            data = target_sock.recv(8192)
                            if data:
                                self.connection.sendall(data)
                            else:
                                return
                        except:
                            return
        except Exception as e:
            print(f"CONNECT error: {e}")
        finally:
            if target_sock:
                try:
                    target_sock.close()
                except:
                    pass
    
    def do_GET(self):
        """Handle HTTP GET requests"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'type': 'http_proxy'}).encode())
            return
        
        if self.path == '/server-info':
            domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'unknown')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'type': 'http_proxy',
                'host': domain,
                'port': int(os.environ.get('PORT', 8080)),
                'users': len(USERS)
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Проверяем аутентификацию для прокси-запросов
        if not self._check_auth():
            self._send_auth_required()
            return
        
        # Проксируем обычные HTTP запросы
        try:
            # Получаем URL
            url = self.path if self.path.startswith('http') else f'http://{self.headers.get("Host")}{self.path}'
            
            # Делаем запрос
            req = urllib.request.Request(url, headers=dict(self.headers))
            with urllib.request.urlopen(req) as response:
                self.send_response(response.status)
                for key, value in response.headers.items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.read())
        except Exception as e:
            self.send_error(500, str(e))
    
    def do_POST(self):
        if self.path == '/add-user':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                username = data.get('username', 'user')
                password = data.get('password', '')
                
                USERS[username] = {
                    'password': password,
                    'created': datetime.now().isoformat()
                }
                
                domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'unknown')
                port = int(os.environ.get('PORT', 8080))
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    'username': username,
                    'host': domain,
                    'port': port,
                    'type': 'http',
                    'config': f'http://{username}:{password}@{domain}:{port}'
                }
                
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
            return
        
        # Проверяем аутентификацию для прокси-запросов
        if not self._check_auth():
            self._send_auth_required()
            return
        
        # Проксируем POST запросы
        try:
            url = self.path if self.path.startswith('http') else f'http://{self.headers.get("Host")}{self.path}'
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            req = urllib.request.Request(url, data=post_data, headers=dict(self.headers))
            with urllib.request.urlopen(req) as response:
                self.send_response(response.status)
                for key, value in response.headers.items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.read())
        except Exception as e:
            self.send_error(500, str(e))
    
    def log_message(self, format, *args):
        # Логируем только ошибки
        if '500' in str(args) or '404' in str(args):
            print(f"{self.address_string()} - {format % args}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HTTPProxyHandler)
    print(f'HTTP Proxy Server running on port {port}')
    print(f'Use as HTTP proxy: http://host:{port}')
    server.serve_forever()
