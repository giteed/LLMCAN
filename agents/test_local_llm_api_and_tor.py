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

# Если settings.py лежит на уровень выше, добавляем его в PYTHONPATH:
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from settings import LLM_API_GENERATE

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Глобальная переменная, чтобы показать, включён ли TOR
USE_TOR = False
original_socket = None

def toggle_tor(enable=True):
    """
    Включает или отключает проксирование через TOR на уровне socket.
    Для локального адреса (10.x.x.x) это всё равно не будет работать,
    но оставляем, чтобы проверять смену IP для внешних запросов.
    """
    global USE_TOR, original_socket
    if enable:
        if not USE_TOR:
            original_socket = socket.socket
            socks.set_default_proxy(socks.SOCKS5, "localhost", 9050)
            socket.socket = socks.socksocket
            USE_TOR = True
            logger.info("TOR включен")
    else:
        if USE_TOR and original_socket:
            socket.socket = original_socket
            socks.set_default_proxy()
            USE_TOR = False
            logger.info("TOR выключен")

def test_llm_connection():
    """
    Тестовое обращение к локальному LLM (Ollama) по адресу LLM_API_GENERATE.
    Важно: session.proxies = {} отключает любой прокси для данного запроса,
    чтобы не было ошибки при попытке идти через Tor к 10.x.x.x.
    """
    logger.info("Начало теста подключения к LLM API")
    
    payload = {
        "model": "qwen2:7b",
        "prompt": "Тестовый запрос",
        "stream": False
    }

    try:
        logger.info(f"Отправка запроса к {LLM_API_GENERATE}")
        with requests.Session() as session:
            # Полностью обнуляем прокси для этого запроса, 
            # чтобы не ломиться через TOR к 10.x.x.x
            session.proxies = {}

            response = session.post(LLM_API_GENERATE, json=payload, timeout=10)
        logger.info(f"Статус ответа: {response.status_code}")
        # Показываем только первые 100 символов текста, чтобы не засорять логи
        logger.info(f"Содержимое ответа: {response.text[:100]}...")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при отправке запроса: {e}")
        return None

def check_ip():
    """Запрашивает текущий внешний IP-адрес (через https://api.ipify.org?format=json) и выводит в лог."""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        ip = response.json()['ip']
        logger.info(f"Текущий IP-адрес: {ip}")
    except requests.RequestException as e:
        logger.error(f"Не удалось получить IP-адрес: {e}")

def check_tor_status():
    """
    Проверяем, запущен ли сервис Tor (systemd).
    Если нет systemd, можете убрать эту функцию или заменить другим методом.
    """
    try:
        result = subprocess.run(["systemctl", "is-active", "tor"], capture_output=True, text=True)
        return result.stdout.strip() == "active"
    except subprocess.CalledProcessError:
        return False

if __name__ == "__main__":
    logger.info("Проверка статуса TOR")
    tor_status = check_tor_status()
    logger.info(f"Статус TOR: {'включен' if tor_status else 'выключен'}")

    logger.info("Тест без использования TOR")
    toggle_tor(False)
    check_ip()  # Покажет внешний IP без TOR
    result = test_llm_connection()
    if result:
        logger.info("Тест без TOR успешно завершен")
    else:
        logger.error("Тест без TOR завершился с ошибкой")

    logger.info("Включение TOR")
    toggle_tor(True)
    check_ip()  # Покажет IP через TOR (должен измениться)
    result = test_llm_connection()
    if result:
        logger.info("Тест с TOR успешно завершен")
    else:
        logger.error("Тест с TOR завершился с ошибкой")

    logger.info("Выключение TOR")
    toggle_tor(False)
    check_ip()  # Вернёт снова «реальный» внешний IP
