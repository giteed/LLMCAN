#!/usr/bin/env python3
# agents/install_tor.py
# Версия: 1.1.1

import os
import subprocess
import sys
import time
import re
import logging
import logging.config
from pathlib import Path

# Добавление пути к settings
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from settings import LOGGING_CONFIG

# Настройка логирования
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

def check_root():
    logger.info("Проверка прав root.")
    return os.geteuid() == 0

def run_command(command):
    try:
        logger.debug(f"Выполняю команду: {' '.join(command)}")
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при выполнении команды {' '.join(command)}: {e}")
        logger.error(f"Вывод ошибки: {e.stderr}")
        sys.exit(1)

def check_tor_installed():
    logger.info("Проверка, установлен ли Tor.")
    try:
        result = subprocess.run(["rpm", "-q", "tor"], capture_output=True, text=True)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        logger.error("Ошибка при проверке наличия Tor.")
        return False

def install_tor():
    logger.info("Начало установки Tor.")
    print("Проверяю, установлен ли Tor...")
    if check_tor_installed():
        choice = input("Tor уже установлен. Хотите переустановить? (yes/enter для пропуска): ")
        if choice.lower() != 'yes':
            print("Пропускаю установку Tor.")
            return
    
    try:
        logger.info("Запуск процесса установки Tor.")
        run_command(["rm", "-f", "/etc/pki/rpm-gpg/RPM-GPG-KEY-elrepo.org"])
        run_command(["rm", "-f", "/etc/yum.repos.d/elrepo.repo"])
        run_command(["rpm", "--import", "https://www.elrepo.org/RPM-GPG-KEY-elrepo.org"])
        run_command(["dnf", "install", "-y", "https://www.elrepo.org/elrepo-release-8.el8.elrepo.noarch.rpm"])
        run_command(["dnf", "clean", "all"])
        run_command(["dnf", "install", "-y", "epel-release"])
        run_command(["dnf", "update", "-y", "--refresh"])
        run_command(["dnf", "install", "-y", "tor"])
        print("Tor успешно установлен.")
        logger.info("Tor успешно установлен.")
        
        firewall_services = run_command(["firewall-cmd", "--get-services"])
        if "tor" in firewall_services:
            run_command(["firewall-cmd", "--add-service=tor", "--permanent"])
        else:
            print("Сервис 'tor' не найден в firewalld. Открываем порт 9050/tcp.")
            run_command(["firewall-cmd", "--add-port=9050/tcp", "--permanent"])
        
        run_command(["firewall-cmd", "--reload"])
    except Exception as e:
        logger.error(f"Ошибка при установке Tor: {e}")
        sys.exit(1)

def start_tor_service():
    logger.info("Запуск сервиса Tor.")
    print("Запускаю сервис Tor...")
    run_command(["systemctl", "enable", "--now", "tor"])
    print("Сервис Tor запущен.")
    logger.info("Сервис Tor запущен.")

def check_tor_status():
    logger.info("Проверка статуса Tor.")
    try:
        status = run_command(["systemctl", "is-active", "tor"])
        if status == "active":
            print("Сервис Tor активен.")
            logger.info("Сервис Tor активен.")
        else:
            print(f"Сервис Tor не активен. Статус: {status}")
            logger.warning(f"Сервис Tor не активен. Статус: {status}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при проверке статуса Tor: {e}")

def restart_tor_and_check_ddgr():
    logger.info("Перезапуск Tor и проверка ddgr.")
    max_retries = 5
    retries = 0

    while retries < max_retries:
        try:
            print("Перезапуск TOR...")
            logger.debug("Перезапуск TOR...")
            subprocess.run(["sudo", "systemctl", "restart", "tor"], check=True, timeout=30)
            time.sleep(5)

            status = subprocess.run(["systemctl", "is-active", "tor"], capture_output=True, text=True, timeout=10)
            if status.stdout.strip() != "active":
                logger.warning("TOR не активен. Повторная попытка...")
                retries += 1
                continue

            try:
                ip_result = subprocess.run(["torsocks", "curl", "-m", "10", "https://api.ipify.org"], capture_output=True, text=True, timeout=3)
                new_ip = ip_result.stdout.strip()
                logger.info(f"Новый IP через TOR: {new_ip}")
                print(f"Отладка: Новый IP через TOR: {new_ip}")
            except subprocess.CalledProcessError:
                logger.warning("Не удалось получить IP через TOR.")
            return True

        except subprocess.TimeoutExpired as te:
            logger.error(f"Превышено время ожидания при выполнении команды. Попытка {retries + 1}: {te}")
            retries += 1
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка при выполнении команды: {e}")
            retries += 1
        except Exception as e:
            logger.error(f"Общая ошибка: {e}")
            retries += 1
        time.sleep(2)

    logger.error("Не удалось настроить TOR после 5 попыток. Проверьте подключение.")
    return False

def main():
    logger.info("Запуск основного процесса установки Tor.")
    if not check_root():
        logger.error("Скрипт должен быть запущен с правами root.")
        print("Этот скрипт должен быть запущен с правами root.")
        sys.exit(1)
    
    install_tor()
    start_tor_service()
    check_tor_status()

if __name__ == "__main__":
    main()
