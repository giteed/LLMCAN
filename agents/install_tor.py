#!/usr/bin/env python3
# install_tor.py

import os
import subprocess
import sys

def check_root():
    return os.geteuid() == 0

def install_tor():
    print("Начинаю установку Tor...")
    try:
        subprocess.run(["apt-get", "update"], check=True)
        subprocess.run(["apt-get", "install", "-y", "tor"], check=True)
        print("Tor успешно установлен.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при установке Tor: {e}")
        sys.exit(1)

def start_tor_service():
    print("Запускаю сервис Tor...")
    try:
        subprocess.run(["systemctl", "start", "tor"], check=True)
        print("Сервис Tor запущен.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при запуске сервиса Tor: {e}")
        sys.exit(1)

def check_tor_status():
    try:
        result = subprocess.run(["systemctl", "is-active", "tor"], capture_output=True, text=True)
        if result.stdout.strip() == "active":
            print("Сервис Tor активен.")
        else:
            print("Сервис Tor не активен.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при проверке статуса Tor: {e}")

def main():
    if not check_root():
        print("Этот скрипт должен быть запущен с правами root.")
        sys.exit(1)
    
    install_tor()
    start_tor_service()
    check_tor_status()

if __name__ == "__main__":
    main()
