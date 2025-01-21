#!/usr/bin/env python3
# LLMCAN/agents/show_info_cognitive_interface_agent_v2.py
# ==================================================
# Сценарий для отображения текущей информации об агенте
# Версия: 1.2.0
# ==================================================

import socket
import requests
import logging
from pathlib import Path
from colors import Colors
from settings import LLM_API_URL

def get_ip_address():
    """Получает локальный IP-адрес."""
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception as e:
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
        return f"{Colors.RED}Ошибка получения IP TOR: {str(e)}{Colors.RESET}"

def check_llm_api_status():
    """Проверяет доступность API LLM с детализацией."""
    try:
        base_url = "http://10.67.67.2:11434/"
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            logger.info("LLM API доступен и отвечает корректно.")
            return f"{Colors.GREEN}API доступен. Ollama работает корректно.{Colors.RESET}"
        elif 400 <= response.status_code < 500:
            logger.warning(f"API доступен, но вернул ошибку клиента: {response.status_code}")
            return f"{Colors.YELLOW}API доступен, но вернул ошибку клиента: {response.status_code}{Colors.RESET}"
        elif 500 <= response.status_code < 600:
            logger.error(f"API доступен, но вернул ошибку сервера: {response.status_code}")
            return f"{Colors.RED}API доступен, но вернул ошибку сервера: {response.status_code}{Colors.RESET}"
        else:
            logger.warning(f"API доступен, но вернул неизвестный статус: {response.status_code}")
            return f"{Colors.YELLOW}API доступен, но вернул неизвестный статус: {response.status_code}{Colors.RESET}"
    except requests.exceptions.Timeout:
        logger.error("Таймаут при подключении к API.")
        return f"{Colors.RED}API недоступен: Таймаут подключения.{Colors.RESET}"
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Ошибка подключения к API: {e}")
        return f"{Colors.RED}API недоступен: Ошибка подключения.{Colors.RESET}"
    except Exception as e:
        logger.error(f"Общая ошибка при проверке API: {e}")
        return f"{Colors.RED}API недоступен: {str(e)}{Colors.RESET}"


def get_ollama_models():
    """Получает список доступных моделей Ollama."""
    try:
        response = requests.get(f"{LLM_API_URL}models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            return ", ".join(models) if models else "{Colors.YELLOW}Нет доступных моделей.{Colors.RESET}"
        return f"{Colors.RED}Ошибка получения моделей: {response.status_code}{Colors.RESET}"
    except Exception as e:
        return f"{Colors.RED}Ошибка получения моделей: {str(e)}{Colors.RESET}"

def test_ollama_query():
    """Выполняет тестовый запрос к API LLM."""
    try:
        payload = {"model": "test-model", "prompt": "Hello, world!"}
        response = requests.post(LLM_API_URL, json=payload, timeout=5)
        if response.status_code == 200:
            return f"{Colors.GREEN}Ответ: {response.json().get('response', 'Нет ответа')}{Colors.RESET}"
        return f"{Colors.RED}Ошибка тестового запроса: {response.status_code}{Colors.RESET}"
    except Exception as e:
        return f"{Colors.RED}Ошибка тестового запроса: {str(e)}{Colors.RESET}"

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
                        versions[name] = line.strip().split(":")[1].strip()
                        break
                else:
                    versions[name] = f"{Colors.YELLOW}Версия не указана{Colors.RESET}"
        except FileNotFoundError:
            versions[name] = f"{Colors.RED}Файл не найден{Colors.RESET}"
        except Exception as e:
            versions[name] = f"{Colors.RED}Ошибка: {str(e)}{Colors.RESET}"
    return versions

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
    print(f"{Colors.GREEN}Модели Ollama: {Colors.RESET}{get_ollama_models()}")
    print(f"{Colors.GREEN}Тестовый запрос к модели: {Colors.RESET}{test_ollama_query()}")

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
    USE_TOR = True  # Или False
    LOG_LEVEL = "INFO"
    show_info(USE_TOR, LOG_LEVEL)
