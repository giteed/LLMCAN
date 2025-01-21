#!/usr/bin/env python3
# LLMCAN/agents/test_local_llm_api_and_tor.py
# ===========================================
# Сценарий тестирования локального LLM API (Ollama) 
# + проверка IP и включение/выключение TOR через session-level proxy
# ===========================================

import os
import sys
import requests
import logging
import subprocess

# Если colors.py есть в вашем проекте, подключаем его
try:
    from colors import Colors
except ImportError:
    # Заглушка, если нет colors.py
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

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

USE_TOR = False  # Флаг, указывающий, хотим ли мы пользоваться TOR для внешних запросов

def toggle_tor(enable: bool):
    """Устанавливаем флаг USE_TOR."""
    global USE_TOR
    USE_TOR = enable
    if enable:
        logger.info(Colors.MAGENTA + "TOR: теперь включен (session-level)" + Colors.RESET)
    else:
        logger.info(Colors.MAGENTA + "TOR: теперь выключен (session-level)" + Colors.RESET)

def get_session_for_external_requests() -> requests.Session:
    """
    Возвращаем session, которая либо использует TOR (socks5://127.0.0.1:9050),
    либо обычное прямое подключение, в зависимости от USE_TOR.
    """
    s = requests.Session()
    if USE_TOR:
        s.proxies = {
            "http": "socks5://127.0.0.1:9050",
            "https": "socks5://127.0.0.1:9050"
        }
    else:
        s.proxies = {}
    return s

def check_tor_status():
    """Смотрим, запущен ли tor (systemd)."""
    try:
        result = subprocess.run(["systemctl", "is-active", "tor"], capture_output=True, text=True)
        return result.stdout.strip() == "active"
    except subprocess.CalledProcessError:
        return False

def check_ip():
    """
    Показывает текущий внешний IP (через ipify).
    Здесь решаем, используем ли мы TOR или нет, 
    исходя из флага USE_TOR.
    """
    logger.info(Colors.GREEN + "Проверка текущего IP" + Colors.RESET)
    s = get_session_for_external_requests()
    try:
        resp = s.get("https://api.ipify.org?format=json", timeout=5)
        ip = resp.json().get("ip")
        logger.info(Colors.CYAN + f"Текущий IP-адрес: {ip}" + Colors.RESET)
    except requests.RequestException as e:
        logger.error(Colors.RED + f"Не удалось получить IP-адрес: {e}" + Colors.RESET)

def test_llm_connection():
    """
    Делаем запрос к локальному Ollama (http://10.x.x.x:11434).
    Здесь нам TOR не нужен, поэтому session.proxies = {}.
    """
    logger.info(Colors.YELLOW + "Тест подключения к локальному LLM (Ollama)" + Colors.RESET)
    payload = {
        "model": "qwen2:7b",
        "prompt": "Тестовый запрос",
        "stream": False
    }
    try:
        with requests.Session() as s:
            # Всегда без прокси для локального адреса:
            s.proxies = {}
            logger.info(Colors.YELLOW + f"Отправка запроса к {LLM_API_GENERATE}" + Colors.RESET)
            r = s.post(LLM_API_GENERATE, json=payload, timeout=10)
        
        logger.info(Colors.YELLOW + f"Статус ответа: {r.status_code}" + Colors.RESET)
        logger.info(Colors.YELLOW + f"Содержимое ответа: {r.text[:100]}..." + Colors.RESET)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        logger.error(Colors.RED + f"Ошибка при отправке запроса: {e}" + Colors.RESET)
        return None

if __name__ == "__main__":
    # 0) Проверяем, запущен ли TOR
    tor_systemd_status = check_tor_status()
    logger.info(Colors.BOLD + f"TOR (systemd) сейчас: {'активен' if tor_systemd_status else 'неактивен'}" + Colors.RESET)

    # 1) Отключаем TOR (session-level) и тестируем IP + локальный LLM
    logger.info(Colors.BOLD + "\n=== Тест без TOR ===" + Colors.RESET)
    toggle_tor(False)
    check_ip()
    result_no_tor = test_llm_connection()
    if result_no_tor:
        logger.info(Colors.GREEN + "Тест без TOR успешно завершен" + Colors.RESET)
    else:
        logger.error(Colors.RED + "Тест без TOR завершился с ошибкой" + Colors.RESET)

    # 2) Включаем TOR (session-level) и снова проверяем IP
    logger.info(Colors.BOLD + "\n=== Включаем TOR ===" + Colors.RESET)
    toggle_tor(True)
    check_ip()

    # 3) Тестим локальный LLM (но всё равно без прокси) 
    logger.info(Colors.BOLD + "\n=== Тест локального LLM при включенном TOR ===" + Colors.RESET)
    result_tor = test_llm_connection()
    if result_tor:
        logger.info(Colors.GREEN + "Тест с TOR (локальный LLM) успешно завершен" + Colors.RESET)
    else:
        logger.error(Colors.RED + "Тест с TOR завершился с ошибкой" + Colors.RESET)

    # 4) Выключаем TOR напоследок
    logger.info(Colors.BOLD + "\n=== Выключаем TOR ===" + Colors.RESET)
    toggle_tor(False)
    check_ip()
