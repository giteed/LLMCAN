#!/usr/bin/env python3
# LLMCAN/agents/show_info_cognitive_interface_agent_v2.py
# ==================================================
# Сценарий для отображения текущей информации об агенте
# Версия: 1.1.0
# ==================================================

import socket
import requests
import logging
import logging.config
from pathlib import Path
from colors import Colors
from settings import LLM_API_URL, LOGGING_CONFIG

# Настройка логирования
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

def get_ip_address():
    """Получает локальный IP-адрес."""
    try:
        ip_address = socket.gethostbyname(socket.gethostname())
        logger.info(f"Локальный IP-адрес: {ip_address}")
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
        tor_ip = response.text
        logger.info(f"IP через TOR: {tor_ip}")
        return tor_ip
    except Exception as e:
        logger.error(f"Ошибка получения IP через TOR: {e}")
        return f"{Colors.RED}Ошибка получения IP TOR: {str(e)}{Colors.RESET}"

def check_llm_api_status():
    """Проверяет доступность API LLM."""
    try:
        base_url = "http://10.67.67.2:11434/"
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            logger.info("LLM API доступен.")
            return f"{Colors.GREEN}API доступен. Ollama работает.{Colors.RESET}"
        logger.warning(f"Базовый URL доступен, но эндпоинт вернул код {response.status_code}")
        return f"{Colors.YELLOW}Базовый URL доступен, но эндпоинт вернул код {response.status_code}{Colors.RESET}"
    except Exception as e:
        logger.error(f"API недоступен: {e}")
        return f"{Colors.RED}API недоступен: {str(e)}{Colors.RESET}"

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
            absolute_path = Path(path).resolve()
            if not absolute_path.is_file():
                raise FileNotFoundError(f"Файл {absolute_path} не найден.")

            with open(absolute_path, "r", encoding="utf-8") as file:
                for line in file:
                    if "Версия:" in line or "Version:" in line:
                        versions[name] = line.strip().split(":")[1].strip()
                        logger.info(f"Версия для {name}: {versions[name]}")
                        break
                else:
                    versions[name] = f"{Colors.YELLOW}Версия не указана{Colors.RESET}"
                    logger.warning(f"Версия не указана для {name}")
        except FileNotFoundError as e:
            versions[name] = f"{Colors.RED}Файл не найден: {str(e)}{Colors.RESET}"
            logger.error(f"Файл не найден: {e}")
        except Exception as e:
            versions[name] = f"{Colors.RED}Ошибка: {str(e)}{Colors.RESET}"
            logger.error(f"Ошибка обработки файла {name}: {e}")
    return versions

def show_info(use_tor, log_level):
    """Отображает информацию об агенте в разделах."""
    logger.info("Начало отображения информации об агенте.")
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

    print(f"{Colors.BOLD}Версии скриптов:{Colors.RESET}")
    for script, version in get_script_versions().items():
        print(f"{Colors.YELLOW}{script}: {Colors.RESET}{version}")

    print(Colors.GRAY + Colors.HORIZONTAL_LINE + Colors.RESET)
    logger.info("Отображение информации об агенте завершено.")

if __name__ == "__main__":
    USE_TOR = True  # Или False
    LOG_LEVEL = "INFO"
    show_info(USE_TOR, LOG_LEVEL)
