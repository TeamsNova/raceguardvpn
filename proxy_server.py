#!/usr/bin/env python3
import asyncio
import socket
import struct
import os
import json
from datetime import datetime

# Простая база данных пользователей (в продакшене использовать Redis/PostgreSQL)
USERS = {}

class SOCKS5Server:
    def __init__(self, host='0.0.0.0', port=1080):
        self.host = host
        self.port = port
        
    async def handle_client(self, reader, writer):
        try:
            # SOCKS5 handshake
            data = await reader.read(2)
            if len(data) < 2 or data[0] != 0x05:
                writer.close()
                return
            
            nmethods = data[1]
            methods = await reader.read(nmethods)
            
            # Отправляем ответ (без аутентификации пока)
            writer.write(b'\x05\x00')
            await writer.drain()
            
            # Получаем запрос
            data = await reader.read(4)
            if len(data) < 4:
                writer.close()
                return
            
            ver, cmd, rsv, atyp = data
            
            if cmd != 0x01:  # Только CONNECT
                writer.write(b'\x05\x07\x00\x01\x00\x00\x00\x00\x00\x00')
                await writer.drain()
                writer.close()
                return
            
            # Получаем адрес
            if atyp == 0x01:  # IPv4
                addr_data = await reader.read(4)
                addr = socket.inet_ntoa(addr_data)
            elif atyp == 0x03:  # Domain
                addr_len = (await reader.read(1))[0]
                addr = (await reader.read(addr_len)).decode()
            else:
                writer.write(b'\x05\x08\x00\x01\x00\x00\x00\x00\x00\x00')
                await writer.drain()
                writer.close()
                return
            
            # Получаем порт
            port_data = await reader.read(2)
            port = struct.unpack('!H', port_data)[0]
            
            # Подключаемся к целевому серверу
            try:
                target_reader, target_writer = await asyncio.open_connection(addr, port)
                
                # Отправляем успешный ответ
                writer.write(b'\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00')
                await writer.drain()
                
                # Пересылаем данные в обе стороны
                await asyncio.gather(
                    self.pipe(reader, target_writer),
                    self.pipe(target_reader, writer)
                )
            except Exception as e:
                print(f"Connection error: {e}")
                writer.write(b'\x05\x05\x00\x01\x00\x00\x00\x00\x00\x00')
                await writer.drain()
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass
    
    async def pipe(self, reader, writer):
        try:
            while True:
                data = await reader.read(8192)
                if not data:
                    break
                writer.write(data)
                await writer.drain()
        except:
            pass
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass
    
    async def start(self):
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )
        print(f'SOCKS5 proxy running on {self.host}:{self.port}')
        async with server:
            await server.serve_forever()

# HTTP API для управления
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'type': 'socks5'}).encode())
        
        elif self.path == '/server-info':
            domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'unknown')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'type': 'socks5',
                'host': domain,
                'port': 1080,
                'users': len(USERS)
            }
            self.wfile.write(json.dumps(response).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
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
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    'username': username,
                    'host': domain,
                    'port': 1080,
                    'config': f'socks5://{username}:{password}@{domain}:1080'
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
    
    def log_message(self, format, *args):
        pass

def run_api():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), APIHandler)
    print(f'API Server running on port {port}')
    server.serve_forever()

if __name__ == '__main__':
    # Запускаем API в отдельном потоке
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Запускаем SOCKS5 сервер
    proxy = SOCKS5Server(host='0.0.0.0', port=1080)
    asyncio.run(proxy.start())
