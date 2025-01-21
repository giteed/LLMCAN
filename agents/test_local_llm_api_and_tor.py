#!/usr/bin/env python3
# LLMCAN/agents/test_local_llm_api_and_tor.py
# ===========================================
# Сценарий тестирования локального LLM API (Ollama) 
# с проверкой IP и включением/выключением Tor
# ===========================================

import os
import sys
import requests
import socks
import socket
import logging
import subprocess

# Если у вас есть модуль colors.py (как в других скриптах),
# Подключаем для цветного вывода:
try:
    from colors import Colors
except ImportError:
    # Если нет - создадим простой заглушечный класс
    class Colors:
        RESET   = ""
        BOLD    = ""
        CYAN    = ""
        GREEN   = ""
        RED     = ""
        YELLOW  = ""
        MAGENTA = ""

# Если settings.py лежит на уровень выше, добавляем его в PYTHONPATH:
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from settings import LLM_API_GENERATE

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

USE_TOR = False
original_socket = None

def toggle_tor(enable=True):
    """
    Включает или отключает проксирование через TOR на уровне socket.
    """
    global USE_TOR, original_socket
    if enable:
        if not USE_TOR:
            original_socket = socket.socket
            socks.set_default_proxy(socks.SOCKS5, "localhost", 9050)
            socket.socket = socks.socksocket
            USE_TOR = True
            logger.info(Colors.MAGENTA + "TOR включен" + Colors.RESET)
    else:
        if USE_TOR and original_socket:
            socket.socket = original_socket
            socks.set_default_proxy()
            USE_TOR = False
            logger.info(Colors.MAGENTA + "TOR выключен" + Colors.RESET)

def check_tor_status():
    """
    Проверяем, запущен ли сервис Tor (systemd).
    Если нет systemd, можете убрать эту функцию или 
    заменить другим методом.
    """
    try:
        result = subprocess.run(["systemctl", "is-active", "tor"], capture_output=True, text=True)
        return result.stdout.strip() == "active"
    except subprocess.CalledProcessError:
        return False

def check_ip():
    """
    Запрашивает текущий внешний IP-адрес 
    (через https://api.ipify.org?format=json) и выводит в лог.
    """
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        ip = response.json()['ip']
        logger.info(Colors.CYAN + f"Текущий IP-адрес: {ip}" + Colors.RESET)
    except requests.RequestException as e:
        logger.error(Colors.RED + f"Не удалось получить IP-адрес: {e}" + Colors.RESET)

def test_llm_connection():
    """
    Тестовое обращение к локальному LLM (Ollama) по адресу LLM_API_GENERATE.
    Важно: session.proxies = {} отключает любой прокси для этого запроса,
    чтобы не ломиться через TOR к 10.x.x.x (что даст General SOCKS failure).
    """
    logger.info(Colors.YELLOW + "Начало теста подключения к LLM API (Ollama)" + Colors.RESET)
    
    payload = {
        "model": "qwen2:7b",
        "prompt": "Тестовый запрос",
        "stream": False
    }

    try:
        logger.info(Colors.YELLOW + f"Отправка запроса к {LLM_API_GENERATE}" + Colors.RESET)
        with requests.Session() as session:
            # Всегда отключаем прокси для локальных запросов:
            session.proxies = {}
            response = session.post(LLM_API_GENERATE, json=payload, timeout=10)

        logger.info(Colors.YELLOW + f"Статус ответа: {response.status_code}" + Colors.RESET)
        # Показываем только первые 100 символов ответа:
        logger.info(Colors.YELLOW + f"Содержимое ответа: {response.text[:100]}..." + Colors.RESET)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(Colors.RED + f"Ошибка при отправке запроса: {e}" + Colors.RESET)
        return None

if __name__ == "__main__":
    # 1) Проверяем, активен ли TOR в системе
    logger.info(Colors.GREEN + "Проверка статуса TOR" + Colors.RESET)
    tor_is_active = check_tor_status()
    logger.info(Colors.GREEN + f"Статус TOR (systemd): {'включен' if tor_is_active else 'выключен'}" + Colors.RESET)
    
    # Если TOR уже активен, выключим его, чтобы сначала проверить без TOR
    if tor_is_active:
        logger.info(Colors.GREEN + "Выключаем TOR для первого теста" + Colors.RESET)
        toggle_tor(False)
    else:
        logger.info(Colors.GREEN + "TOR неактивен, всё ок" + Colors.RESET)

    # 2) Проверка без TOR
    logger.info(Colors.BOLD + "\n=== Тест без использования TOR ===" + Colors.RESET)
    check_ip()  # Покажет внешний IP (скорее всего реальный)
    result = test_llm_connection()
    if result:
        logger.info(Colors.GREEN + "Тест без TOR успешно завершен" + Colors.RESET)
    else:
        logger.error(Colors.RED + "Тест без TOR завершился с ошибкой" + Colors.RESET)

    # 3) Включаем TOR
    logger.info(Colors.BOLD + "\n=== Включение TOR ===" + Colors.RESET)
    toggle_tor(True)
    check_ip()  # Покажет IP через TOR exit node

    logger.info(Colors.BOLD + "\n=== Тест c TOR (но локальный Ollama идёт без прокси) ===" + Colors.RESET)
    result = test_llm_connection()
    if result:
        logger.info(Colors.GREEN + "Тест с TOR успешно завершен" + Colors.RESET)
    else:
        logger.error(Colors.RED + "Тест с TOR завершился с ошибкой" + Colors.RESET)

    # 4) Отключаем TOR в конце (если нужно)
    logger.info(Colors.BOLD + "\n=== Выключение TOR ===" + Colors.RESET)
    toggle_tor(False)
    check_ip()  # Вернётся реальный IP
