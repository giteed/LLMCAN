#!/usr/bin/env python3
# LLMCAN/agents/test_local_llm_api_and_tor.py
# ============================================

import os
import sys

# Добавляем верхнюю папку в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import requests
import socks
import socket
import logging
import subprocess

from settings import LLM_API_GENERATE  # <-- теперь сработает

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

USE_TOR = False
original_socket = None

def toggle_tor(enable=True):
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
    logger.info("Начало теста подключения к LLM API")
    
    payload = {
        "model": "qwen2:7b",
        "prompt": "Тестовый запрос",
        "stream": False
    }

    try:
        logger.info(f"Отправка запроса к {LLM_API_GENERATE}")
        with requests.Session() as session:
            if USE_TOR:
                session.proxies = {}
            response = session.post(LLM_API_GENERATE, json=payload, timeout=10)
        logger.info(f"Статус ответа: {response.status_code}")
        logger.info(f"Содержимое ответа: {response.text[:100]}...")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при отправке запроса: {e}")
        return None

def check_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        ip = response.json()['ip']
        logger.info(f"Текущий IP-адрес: {ip}")
    except requests.RequestException as e:
        logger.error(f"Не удалось получить IP-адрес: {e}")

def check_tor_status():
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
    check_ip()
    result = test_llm_connection()
    if result:
        logger.info("Тест без TOR успешно завершен")
    else:
        logger.error("Тест без TOR завершился с ошибкой")

    logger.info("Включение TOR")
    toggle_tor(True)
    check_ip()
    result = test_llm_connection()
    if result:
        logger.info("Тест с TOR успешно завершен")
    else:
        logger.error("Тест с TOR завершился с ошибкой")

    logger.info("Выключение TOR")
    toggle_tor(False)
    check_ip()
