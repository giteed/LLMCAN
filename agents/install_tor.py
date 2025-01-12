#!/usr/bin/env python3
# install_tor.py

import os
import subprocess
import sys

def check_root():
    return os.geteuid() == 0

def run_command(command):
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении команды {' '.join(command)}: {e}")
        sys.exit(1)

def install_tor():
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
        run_command(["firewall-cmd", "--add-service=tor", "--permanent"])
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
