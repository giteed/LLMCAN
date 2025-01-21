#!/usr/bin/env python3
# LLMCAN/agents/show_info_cognitive_interface_agent_v2.py
# ==================================================
# Сценарий для отображения текущей информации об агенте
# Версия: 1.1.1
# ==================================================

import socket
import requests
from pathlib import Path
from colors import Colors
from settings import LLM_API_URL

# Настройка логирования
def initialize_logger():
    import logging
    logger = logging.getLogger("show_info")
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

    return logger

logger = initialize_logger()

def get_ip_address():
    """Получает локальный IP-адрес."""
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception as e:
        logger.error(f"Ошибка получения локального IP-адреса: {e}")
        return f"{Colors.RED}Ошибка получения IP: {e}{Colors.RESET}"

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
        return f"{Colors.RED}Ошибка получения IP TOR: {e}{Colors.RESET}"

def check_llm_api_status():
    """Проверяет доступность API LLM."""
    try:
        base_url = LLM_API_URL.rstrip('/')
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            return f"{Colors.GREEN}API доступен. Ollama работает.{Colors.RESET}"
        else:
            return f"{Colors.YELLOW}API доступен, но вернул код {response.status_code}.{Colors.RESET}"
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка подключения к API LLM: {e}")
        return f"{Colors.RED}API недоступен: {e}{Colors.RESET}"

def get_script_versions():
    """Возвращает версии скриптов из их заголовков."""
    script_files = {
        "cognitive_interface_agent_v2.py": "./agents/cognitive_interface_agent_v2.py",
        "cognitive_logic.py": "./agents/cognitive_logic.py",
        "data_management.py": "./agents/data_management.py",
        "preprocess_query.py": "./agents/preprocess_query.py"
    }
    versions = {}
    for name, path in script_files.items():
        try:
            with open(Path(path).resolve(), "r", encoding="utf-8") as file:
                for line in file:
                    if "Версия:" in line or "Version:" in line:
                        versions[name] = line.split(":", 1)[1].strip()
                        break
                else:
                    versions[name] = f"{Colors.YELLOW}Версия не указана{Colors.RESET}"
        except FileNotFoundError:
            versions[name] = f"{Colors.RED}Файл не найден{Colors.RESET}"
    return versions

def show_info(use_tor, log_level):
    """Отображает информацию об агенте."""
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

    print(Colors.YELLOW + Colors.BOLD)
    print("\n╔═══════════════════════════════════════════════╗")
    print("║       Информация о скриптах и настройках      ║")
    print("╚═══════════════════════════════════════════════╝")
    print(Colors.RESET)

    versions = get_script_versions()
    for script, version in versions.items():
        print(f"{Colors.YELLOW}{script}: {Colors.RESET}{version}")

    print(Colors.GRAY + Colors.HORIZONTAL_LINE + Colors.RESET)

if __name__ == "__main__":
    USE_TOR = True  # Или False
    LOG_LEVEL = "INFO"
    show_info(USE_TOR, LOG_LEVEL)
