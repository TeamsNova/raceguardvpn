#!/usr/bin/env python3
import asyncio
import socket
import os
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import urllib.request

# База данных пользователей
USERS = {}

class HTTPProxyHandler(BaseHTTPRequestHandler):
    def do_CONNECT(self):
        """Handle HTTPS CONNECT requests"""
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
            
            # Пересылаем данные в обе стороны
            self.connection.setblocking(0)
            target_sock.setblocking(0)
            
            while True:
                # От клиента к серверу
                try:
                    data = self.connection.recv(8192)
                    if data:
                        target_sock.sendall(data)
                    else:
                        break
                except:
                    pass
                
                # От сервера к клиенту
                try:
                    data = target_sock.recv(8192)
                    if data:
                        self.connection.sendall(data)
                    else:
                        break
                except:
                    pass
        except Exception as e:
            print(f"CONNECT error: {e}")
        finally:
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
        else:
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
