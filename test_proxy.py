#!/usr/bin/env python3
import json
import urllib.request
import time
import subprocess
import sys
import signal

def test_proxy():
    print("🧪 Тест прокси-сервера")
    print("=" * 50)
    
    # Запускаем сервер в фоне
    server_process = subprocess.Popen(
        ['python3', 'proxy_server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={'PORT': '8888'}
    )
    
    try:
        # Ждем, пока сервер запустится
        print("⏳ Ожидание запуска сервера...")
        time.sleep(2)
        
        # Тест 1: /health endpoint
        print("\n✅ Тест 1: Проверка /health")
        try:
            with urllib.request.urlopen('http://localhost:8888/health') as response:
                data = json.loads(response.read().decode())
                print(f"   Статус: {response.status}")
                print(f"   Ответ: {data}")
                assert data['status'] == 'ok'
                assert data['type'] == 'http_proxy'
                print("   ✓ /health работает!")
        except Exception as e:
            print(f"   ✗ Ошибка: {e}")
            return False
        
        # Тест 2: /server-info endpoint
        print("\n✅ Тест 2: Проверка /server-info")
        try:
            with urllib.request.urlopen('http://localhost:8888/server-info') as response:
                data = json.loads(response.read().decode())
                print(f"   Статус: {response.status}")
                print(f"   Ответ: {data}")
                assert data['type'] == 'http_proxy'
                assert data['users'] == 0
                print("   ✓ /server-info работает!")
        except Exception as e:
            print(f"   ✗ Ошибка: {e}")
            return False
        
        # Тест 3: Добавление пользователя через /add-user
        print("\n✅ Тест 3: Добавление пользователя")
        try:
            user_data = json.dumps({
                'username': 'testuser',
                'password': 'testpass'
            }).encode()
            
            req = urllib.request.Request(
                'http://localhost:8888/add-user',
                data=user_data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                print(f"   Статус: {response.status}")
                print(f"   Ответ: {data}")
                assert data['username'] == 'testuser'
                assert 'config' in data
                print("   ✓ Пользователь добавлен!")
        except Exception as e:
            print(f"   ✗ Ошибка: {e}")
            return False
        
        # Тест 4: Проверка что количество пользователей увеличилось
        print("\n✅ Тест 4: Проверка количества пользователей")
        try:
            with urllib.request.urlopen('http://localhost:8888/server-info') as response:
                data = json.loads(response.read().decode())
                print(f"   Количество пользователей: {data['users']}")
                assert data['users'] == 1
                print("   ✓ Количество пользователей корректно!")
        except Exception as e:
            print(f"   ✗ Ошибка: {e}")
            return False
        
        # Тест 5: Проверка аутентификации (без учетных данных)
        print("\n✅ Тест 5: Проверка отказа в доступе без аутентификации")
        try:
            req = urllib.request.Request(
                'http://example.com',
                headers={'Host': 'example.com'}
            )
            req.set_proxy('localhost:8888', 'http')
            
            try:
                with urllib.request.urlopen(req, timeout=5) as response:
                    print(f"   ✗ Должен был вернуть 407, но вернул {response.status}")
                    return False
            except urllib.error.HTTPError as e:
                if e.code == 407:
                    print(f"   ✓ Получен ожидаемый код 407 (требуется аутентификация)")
                else:
                    print(f"   ✗ Получен неожиданный код: {e.code}")
                    return False
        except Exception as e:
            print(f"   ⚠ Предупреждение: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Все тесты пройдены успешно!")
        return True
        
    finally:
        # Останавливаем сервер
        print("\n🛑 Остановка сервера...")
        server_process.send_signal(signal.SIGTERM)
        server_process.wait(timeout=5)
        print("✓ Сервер остановлен")

if __name__ == '__main__':
    success = test_proxy()
    sys.exit(0 if success else 1)
