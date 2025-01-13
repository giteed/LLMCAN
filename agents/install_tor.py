#!/usr/bin/env python3
# agents/install_tor.py

import os
import subprocess
import sys
import time
import re

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
            subprocess.run(["sudo", "systemctl", "restart", "tor"], check=True)
            time.sleep(2)  # Даем TOR время на перезапуск

            # Step 2: Check if TOR is active
            status = subprocess.run(["systemctl", "is-active", "tor"], capture_output=True, text=True)
            if status.stdout.strip() != "active":
                print("TOR не активен. Повторная попытка...")
                retries += 1
                continue

            # Step 3: Get new IP address
            ip_result = subprocess.run(["torsocks", "curl", "https://api.ipify.org"], capture_output=True, text=True)
            new_ip = ip_result.stdout.strip()
            print(f"Отладка: Новый IP через TOR: {new_ip}")

            # Step 4: Test ddgr with a query
            ddgr_result = subprocess.run(["torsocks", "ddgr", "-n", "1", "usdt/btc"], capture_output=True, text=True)
            ddgr_output = ddgr_result.stdout.strip()

            if "[ERROR]" in ddgr_output or "HTTP Error" in ddgr_output:
                print(f"Отладка: Ошибка при запросе ddgr. Повторная попытка... (Попытка {retries + 1})")
                retries += 1
                time.sleep(1)
                continue

            # Step 5: Parse and display result
            match = re.search(r'(\d+\.\d+)\s*\|\s*BTC USDT.*\[(.*?)\]', ddgr_output)
            if match:
                rate, url = match.groups()
                print(f"Отладка: Курс BTC/USDT: {rate}")
                print(f"Отладка: Источник: {url}")
                return True
            else:
                print("Отладка: Не удалось распарсить результат ddgr. Повторная попытка...")
                retries += 1

        except subprocess.CalledProcessError as e:
            print(f"Отладка: Ошибка при выполнении команды: {e}")
            retries += 1
        except Exception as e:
            print(f"Отладка: Общая ошибка: {e}")
            retries += 1

        time.sleep(1)  # Небольшая задержка перед следующей попыткой

    print("Не удалось настроить TOR и ddgr после 5 попыток. Проверьте подключение.")
    return False

if __name__ == "__main__":
    main()
