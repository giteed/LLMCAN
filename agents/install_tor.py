#!/usr/bin/env python3
# agents/install_tor.py

import os
import subprocess
import sys
import time
import re
import requests

def check_root():
    return os.geteuid() == 0

def run_command(command):
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении команды {' '.join(command)}: {e}")
        print(f"Вывод ошибки: {e.stderr}")
        sys.exit(1)
def check_tor_installed():
    try:
        result = subprocess.run(["rpm", "-q", "tor"], capture_output=True, text=True)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False

def install_tor():
    print("Проверяю, установлен ли Tor...")
    if check_tor_installed():
        choice = input("Tor уже установлен. Хотите переустановить? (yes/enter для пропуска): ")
        if choice.lower() != 'yes':
            print("Пропускаю установку Tor.")
            return
    
    print("Начинаю установку Tor...")
    try:
        # Удаляем старый ключ и репозиторий ELRepo
        run_command(["rm", "-f", "/etc/pki/rpm-gpg/RPM-GPG-KEY-elrepo.org"])
        run_command(["rm", "-f", "/etc/yum.repos.d/elrepo.repo"])
        
        # Устанавливаем новый ключ и репозиторий ELRepo
        run_command(["rpm", "--import", "https://www.elrepo.org/RPM-GPG-KEY-elrepo.org"])
        run_command(["dnf", "install", "-y", "https://www.elrepo.org/elrepo-release-8.el8.elrepo.noarch.rpm"])
        
        run_command(["dnf", "clean", "all"])
        run_command(["dnf", "install", "-y", "epel-release"])
        run_command(["dnf", "update", "-y", "--refresh"])
        run_command(["dnf", "install", "-y", "tor"])
        print("Tor успешно установлен.")
        
        # Проверяем, существует ли сервис tor в firewalld
        firewall_services = run_command(["firewall-cmd", "--get-services"])
        if "tor" in firewall_services:
            run_command(["firewall-cmd", "--add-service=tor", "--permanent"])
        else:
            print("Сервис 'tor' не найден в firewalld. Открываем порт 9050/tcp.")
            run_command(["firewall-cmd", "--add-port=9050/tcp", "--permanent"])
        
        run_command(["firewall-cmd", "--reload"])
    except Exception as e:
        print(f"Ошибка при установке Tor: {e}")
        sys.exit(1)

def start_tor_service():
    print("Запускаю сервис Tor...")
    run_command(["systemctl", "enable", "--now", "tor"])
    print("Сервис Tor запущен.")

def check_tor_status():
    try:
        status = run_command(["systemctl", "is-active", "tor"])
        if status == "active":
            print("Сервис Tor активен.")
        else:
            print(f"Сервис Tor не активен. Статус: {status}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при проверке статуса Tor: {e}")

def main():
    if not check_root():
        print("Этот скрипт должен быть запущен с правами root.")
        sys.exit(1)
    
    install_tor()
    start_tor_service()
    check_tor_status()


def restart_tor_and_check_ddgr():
    max_retries = 5
    retries = 0

    while retries < max_retries:
        try:
            # Step 1: Restart TOR
            print("Перезапуск TOR...")
            subprocess.run(["sudo", "systemctl", "restart", "tor"], check=True, timeout=30)
            time.sleep(5)

            # Step 2: Check if TOR is active
            status = subprocess.run(["systemctl", "is-active", "tor"], capture_output=True, text=True, timeout=10)
            if status.stdout.strip() != "active":
                print("TOR не активен. Повторная попытка...")
                retries += 1
                continue

            # Step 3: Get new IP address
            try:
                ip_result = subprocess.run(["torsocks", "curl", "-m", "10", "https://api.ipify.org"], capture_output=True, text=True, timeout=15)
                new_ip = ip_result.stdout.strip()
                print(f"Отладка: Новый IP через TOR: {new_ip}")
            except subprocess.CalledProcessError:
                print("Отладка: Не удалось получить IP. Продолжаем без проверки IP.")

            # Step 4: Check network connectivity through TOR
            try:
                subprocess.run(["torsocks", "curl", "-m", "10", "https://www.google.com"], check=True, timeout=15)
                print("Отладка: Сеть через TOR доступна")
            except subprocess.CalledProcessError:
                print("Отладка: Сеть через TOR недоступна. Повторная попытка...")
                retries += 1
                continue

            # Step 5: Try to get exchange rate using an API
            try:
                response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usdt", proxies={'http': 'socks5h://localhost:9050', 'https': 'socks5h://localhost:9050'}, timeout=30)
                if response.status_code == 200:
                    rate = response.json()['bitcoin']['usdt']
                    print(f"Отладка: Курс BTC/USDT: {rate}")
                    return True
            except Exception as e:
                print(f"Отладка: Не удалось получить курс через API: {e}")

            # Step 6: If API fails, try ddgr
            print("Отладка: Выполнение запроса ddgr...")
            ddgr_command = ["torsocks", "ddgr", "-n", "1", "btc usdt price"]
            print(f"Отладка: Выполняемая команда: {' '.join(ddgr_command)}")
            ddgr_result = subprocess.run(ddgr_command, capture_output=True, text=True, timeout=60)
            ddgr_output = ddgr_result.stdout.strip()
            print(f"Отладка: Вывод ddgr (первые 100 символов): {ddgr_output[:100]}...")
            print(f"Отладка: Код возврата ddgr: {ddgr_result.returncode}")
            if ddgr_result.stderr:
                print(f"Отладка: Ошибка ddgr: {ddgr_result.stderr}")

            if "[ERROR]" in ddgr_output or "HTTP Error" in ddgr_output:
                print(f"Отладка: Ошибка при запросе ddgr. Повторная попытка... (Попытка {retries + 1})")
                retries += 1
                continue

            # Step 7: Parse and display result
            match = re.search(r'(\d+(?:\.\d+)?)\s*(?:\||USD\/BTC|BTC\/USD).*?\[(.*?)\]', ddgr_output, re.IGNORECASE)
            if match:
                rate, url = match.groups()
                print(f"Отладка: Курс BTC/USDT: {rate}")
                print(f"Отладка: Источник: {url}")
                return True
            else:
                print("Отладка: Не удалось распарсить результат ddgr. Повторная попытка...")
                retries += 1

        except subprocess.TimeoutExpired as te:
            print(f"Отладка: Превышено время ожидания при выполнении команды. Попытка {retries + 1}")
            print(f"Отладка: Детали таймаута: {te}")
            retries += 1
        except subprocess.CalledProcessError as e:
            print(f"Отладка: Ошибка при выполнении команды: {e}")
            print(f"Отладка: Вывод команды: {e.output}")
            retries += 1
        except Exception as e:
            print(f"Отладка: Общая ошибка: {e}")
            retries += 1

        time.sleep(2)

    print("Не удалось настроить TOR и ddgr после 5 попыток. Проверьте подключение.")
    return False


if __name__ == "__main__":
    main()
