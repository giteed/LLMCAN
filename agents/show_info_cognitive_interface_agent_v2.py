#!/usr/bin/env python3
# LLMCAN/agents/show_info_cognitive_interface_agent_v2.py
# ==================================================
# Сценарий для отображения текущей информации об агенте
# Версия: 1.2.0
# ==================================================

import socket
import requests
import logging
import subprocess
from pathlib import Path
from colors import Colors
from settings import LLM_API_URL

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def get_ip_address():
    """Получает локальный IP-адрес."""
    try:
        ip_address = socket.gethostbyname(socket.gethostname())
        return ip_address
    except Exception as e:
        logger.error(f"Ошибка получения локального IP-адреса: {e}")
        return f"{Colors.RED}Ошибка получения IP: {str(e)}{Colors.RESET}"

def check_tor_ip():
    """Возвращает текущий IP-адрес, используемый TOR."""
    try:
        response = requests.get(
            "https://api.ipify.org",
            proxies={"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"},
            timeout=10
        )
        return response.text
    except Exception as e:
        logger.error(f"Ошибка получения IP через TOR: {e}")
        return f"{Colors.RED}Ошибка получения IP TOR: {str(e)}{Colors.RESET}"

def check_llm_api_status():
    """Проверяет доступность API LLM."""
    try:
        response = requests.get(LLM_API_URL, timeout=5)
        if response.status_code == 200:
            return f"{Colors.GREEN}API доступен. Ollama работает.{Colors.RESET}"
        return f"{Colors.YELLOW}API вернул код {response.status_code}{Colors.RESET}"
    except Exception as e:
        logger.error(f"API недоступен: {e}")
        return f"{Colors.RED}API недоступен: {str(e)}{Colors.RESET}"

def ping_server(server_ip):
    """Выполняет пинг сервера."""
    try:
        result = subprocess.run(["ping", "-c", "3", server_ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return f"{Colors.GREEN}Сервер {server_ip} доступен.{Colors.RESET}\n{result.stdout}"
        return f"{Colors.RED}Сервер {server_ip} недоступен.{Colors.RESET}\n{result.stderr}"
    except Exception as e:
        logger.error(f"Ошибка пинга сервера {server_ip}: {e}")
        return f"{Colors.RED}Ошибка пинга: {str(e)}{Colors.RESET}"

def list_available_models():
    """Возвращает список доступных моделей Ollama."""
    try:
        response = requests.get(f"{LLM_API_URL}/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            return f"{Colors.GREEN}Доступные модели: {', '.join(models)}{Colors.RESET}"
        return f"{Colors.YELLOW}Не удалось получить список моделей. Код: {response.status_code}{Colors.RESET}"
    except Exception as e:
        logger.error(f"Ошибка получения списка моделей: {e}")
        return f"{Colors.RED}Ошибка: {str(e)}{Colors.RESET}"

def test_llm_response():
    """Отправляет тестовый запрос к модели Ollama."""
    try:
        payload = {"model": "test-model", "prompt": "Hello, world!"}
        response = requests.post(LLM_API_URL, json=payload, timeout=5)
        if response.status_code == 200:
            return f"{Colors.GREEN}Ответ модели: {response.json().get('response', '<Нет ответа>')}{Colors.RESET}"
        return f"{Colors.YELLOW}Ошибка запроса. Код: {response.status_code}{Colors.RESET}"
    except Exception as e:
        logger.error(f"Ошибка тестового запроса: {e}")
        return f"{Colors.RED}Ошибка: {str(e)}{Colors.RESET}"

def show_info(use_tor, log_level):
    """Отображает информацию об агенте в разделах."""
    print(Colors.CYAN + Colors.BOLD)
    print("╔═══════════════════════════════════════════════╗")
    print("║                Информация о сервере           ║")
    print("╚═══════════════════════════════════════════════╝")
    print(Colors.RESET)

    print(f"{Colors.GREEN}Локальный IP-адрес: {Colors.RESET}{get_ip_address()}")
    print(f"{Colors.GREEN}IP TOR: {Colors.RESET}{check_tor_ip()}")
    print(f"{Colors.GREEN}Режим TOR: {Colors.RESET}{'Включен' if use_tor else 'Отключен'}")
    print(f"{Colors.GREEN}Текущий режим логирования: {Colors.RESET}{log_level}")

    print(Colors.BLUE + Colors.BOLD)
    print("\n╔═══════════════════════════════════════════════╗")
    print("║              Информация о LLM и API           ║")
    print("╚═══════════════════════════════════════════════╝")
    print(Colors.RESET)

    print(f"{Colors.GREEN}Доступность LLM API: {Colors.RESET}{check_llm_api_status()}")
    print(f"{Colors.GREEN}Пинг сервера: {Colors.RESET}{ping_server('10.67.67.2')}")
    print(f"{Colors.GREEN}Список моделей: {Colors.RESET}{list_available_models()}")
    print(f"{Colors.GREEN}Тестовый запрос: {Colors.RESET}{test_llm_response()}")

    print(Colors.YELLOW + Colors.BOLD)
    print("\n╔═══════════════════════════════════════════════╗")
    print("║       Информация о скриптах и настройках      ║")
    print("╚═══════════════════════════════════════════════╝")
    print(Colors.RESET)

    print(f"{Colors.BOLD}Версии скриптов:{Colors.RESET}")
    for script, version in get_script_versions().items():
        print(f"{Colors.YELLOW}{script}: {Colors.RESET}{version}")

    print(Colors.GRAY + Colors.HORIZONTAL_LINE + Colors.RESET)

if __name__ == "__main__":
    USE_TOR = True
    LOG_LEVEL = "INFO"
    show_info(USE_TOR, LOG_LEVEL)
