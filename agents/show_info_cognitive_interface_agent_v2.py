#!/usr/bin/env python3
# LLMCAN/agents/show_info_cognitive_interface_agent_v2.py
# ==================================================
# Сценарий для отображения текущей информации об агенте
# Версия: 1.2.3
# ==================================================

import socket
import requests
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
    """Проверяет доступность API LLM."""
    try:
        base_url = "http://10.67.67.2:11434/"
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            return f"{Colors.GREEN}API доступен. Ollama работает.{Colors.RESET}"
        return f"{Colors.YELLOW}Базовый URL доступен, но эндпоинт вернул код {response.status_code}{Colors.RESET}"
    except Exception as e:
        return f"{Colors.RED}API недоступен: {str(e)}{Colors.RESET}"

def get_ollama_models():
    """Получает список доступных моделей Ollama."""
    try:
        response = requests.get(f"{LLM_API_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            return f"{Colors.GREEN}Ответ сервера:{Colors.RESET}\n{response.text}"
        return f"{Colors.RED}Ошибка получения моделей: {response.status_code}, {response.text}{Colors.RESET}"
    except Exception as e:
        return f"{Colors.RED}Ошибка получения моделей: {str(e)}{Colors.RESET}"


def test_ollama_query():
    """Выполняет тестовый запрос к API LLM."""
    try:
        payload = {"model": "qwen2:7b", "prompt": "Hello, world!"}
        response = requests.post(f"{LLM_API_URL}/api/generate", json=payload, timeout=5)
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

    print(Colors.BLUE + Colors.BOLD)
    print("\n╔═══════════════════════════════════════════════╗")
    print("║              Информация о LLM и API           ║")
    print("╚═══════════════════════════════════════════════╝")
    print(Colors.RESET)
    
    print(f"{Colors.GREEN}Доступность LLM API: {Colors.RESET}{check_llm_api_status()}")
    print(f"{Colors.GREEN}Модели Ollama: {Colors.RESET}{get_ollama_models()}")
    print(f"{Colors.GREEN}Тестовый запрос к модели: {Colors.RESET}{test_ollama_query()}")

    print(Colors.GRAY + Colors.HORIZONTAL_LINE + Colors.RESET)

if __name__ == "__main__":
    USE_TOR = True  # Или False
    LOG_LEVEL = "INFO"
    show_info(USE_TOR, LOG_LEVEL)
